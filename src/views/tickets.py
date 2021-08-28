#Django libs
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

#Python libs
from copy import deepcopy

#Internal libs
from toolkit.toolkit import existence_error, response_creator, validate_error
from toolkit.image import upload_image, delete_image
from apps.users.authentication import TokenAuthentication
from apps.ideas.models import Image
from apps.ideas.serializers import ImageSerializer
from apps.tickets.models import TicketRoom,TicketText
from apps.tickets.serializers import TicketRoomSerializer, TicketRoomDeepSerializer, TicketTextSerializer

class CreateTicket (APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        data = deepcopy(request.data)

        if data.get("status") is not None:
            data.pop("status")
        if data.get("create_date") is not None:
            data.pop("create_date")
        if data.get("section") is None or \
            data.get("priority") is None or \
            data.get("subject") is None:

            return response_creator(
                data={"error":"not valid"},
                status_code=400, 
                status="fail"
            )
        data["user"] = request.user.id

        if data.get("text") is None:
            return response_creator(
                data={"error":"not valid"},
                status_code=400, 
                status="fail"
            )
        
        text = data.pop("text")

        if data.get("image") is not None:

            file_path = upload_image(
            file=data.get("image"),
            dir="tickets",
            prefix_dir=[str(request.user.id)],
            limit_size=4000,
            )

            image_serialized = ImageSerializer(data={
                "image":file_path,
            })

            if not image_serialized.is_valid():
                return validate_error(image_serialized)
            
            image_serialized.save()
            text_serialized = TicketTextSerializer(
                data={
                    "text":text,
                    "image" : image_serialized.data.get("id"),
                    "user" : request.user.id,
            })

            if not text_serialized.is_valid():
                return validate_error(text_serialized)
            text_serialized.save()

        else:
            text_serialized = TicketTextSerializer(
                data={
                    "text":text,
                    "user":request.user.id,
            })

            if not text_serialized.is_valid():
                return validate_error(text_serialized)

            text_serialized.save()

        data["texts"] = [text_serialized.data.get("id"),]

        ticket_serialized = TicketRoomSerializer(data=data)

        if not ticket_serialized.is_valid():
            return validate_error(ticket_serialized)

        ticket_serialized.save()

        return response_creator(data=ticket_serialized.data)

class SendText(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        ticket_id = request.data.get("ticket_id")
        image = request.data.get("image", None)
        ticket_obj = TicketRoom.objects.filter(id=ticket_id).first()

        if ticket_obj is None:
            return existence_error("Ticket")

        ticket_serialized = TicketRoomSerializer(ticket_obj)

        if int(request.user.id) != int(ticket_serialized.data.get("id")):
            return response_creator(
                data={
                    "error":"permission denied"
                },
                status="fail",
                status_code=400
            )
        
        if image is not None:
            file_path = upload_image(
                file=data.get("image"),
                dir="tickets",
                prefix_dir=[str(request.user.id)],
                limit_size=4000,
            )

            image_serialized = ImageSerializer(data={
                "image":file_path,
            })

            if not image_serialized.is_valid():
                return validate_error(image_serialized)

            image_serialized.save()
            text_serialized = TicketTextSerializer(
                data={
                    "text":text,
                    "image" : image_serialized.data.get("id"),
                    "user" : request.user.id,
            })

            if not text_serialized.is_valid():
                return validate_error(text_serialized)
            text_serialized.save()
        else:

            text_serialized = TicketTextSerializer(
                data={
                    "text":text,
                    "user":request.user.id,
            })

            if not text_serialized.is_valid():
                return validate_error(text_serialized)
            text_serialized.save()

        
        texts_list = ticket_serialized.data.get("texts")

        texts_list.append(text_serialized.data.get("id"))

        ticket_serialized = TicketRoomSerializer(
            ticket_obj,
            data={
                "texts":texts_list,
                "status":"i",
            },
            partial=True
        )

        if not ticket_serialized.is_valid():
            return validate_error(ticket_serialized)
        ticket_serialized.save()


        return response_creator(data=ticket_serialized.data)

class ShowTicket(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        ticket_id = request.GET.get("ticket_id")

        ticket_obj = TicketRoom.objects.filter(id=ticket_id).first()

        if ticket_obj is None:
            return existence_error("Ticket")

        ticket_serialized = TicketRoomDeepSerializer(ticket_obj)
        user = ticket_serialized.data.get("user")
        user_id = int(user["id"])

        if int(request.user.id) != user_id:
            return response_creator(
                data={
                    "error":"permission denid"
                },
                status="fail",
                status_code=400
            )
        
        return response_creator (data=ticket_serialized.data)


class GetAllTickets(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        ticket_objs = TicketRoom.objects.filter(user=request.user.id)

        tickets_serialized = TicketRoomSerializer(ticket_objs,many=True)

        return response_creator(data={"tickets":tickets_serialized.data})

class EndTicket(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        ticket_id = request.data.get("ticket_id")

        ticket_obj = TicketRoom.objects.filter(id=ticket_id).first()

        if ticket_obj is None:
            return existence_error("Ticket")

        ticket_serialized = TicketRoomSerializer(ticket_obj)

        if int(request.user.id) != int(ticket_serialized.data.get("user")):
            return response_creator(
                data={
                    "error":"permission denid."
                },
                status="fail",
                status_code=400
            )
        
        ticket_serialized = TicketRoomSerializer(
            ticket_obj,
            data={
                "status":"e"
            },
            partial=True
        )

        if not ticket_serialized.is_valid():
            return validate_error(ticket_serialized)
        
        ticket_serialized.save()

        return response_creator(data=ticket_serialized.data)