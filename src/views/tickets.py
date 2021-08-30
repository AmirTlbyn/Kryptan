#Django libs
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

#Python libs
from copy import deepcopy
from datetime import datetime

#Internal libs
from apps.tickets.tasks import check_for_ticket_expireness
from toolkit.toolkit import existence_error, response_creator, validate_error
from toolkit.image import upload_image, delete_image
from apps.users.authentication import TokenAuthentication
from apps.ideas.models import Image
from apps.ideas.serializers import ImageSerializer
from apps.tickets.models import TicketRoom,TicketText
from apps.tickets.serializers import TicketRoomSerializer, TicketRoomDeepSerializer, TicketTextSerializer
import repositories.ideas as repo_idea
import repositories.tickets as repo_ticket

class CreateTicket (APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        data = deepcopy(request.data)

        ticket_obj = TicketRoom.objects.filter(user=request.user.id, status__ne="e").first()
        
        if ticket_obj is not None:
            return response_creator(
                data={
                    "error":"you have open tickets please closed it first"
                },
                status="fail",
                status_code=400
            )

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
            
            image_serialized, err = repo_idea.create_image_object(
                image=data.get("image"), 
                dir="tickets", 
                prefix_dir=request.user.id,
                limit_size=4000
            )
            if err is not None:
                return err
            
            text_serialized, err = repo_ticket.create_text_obj(
                data={
                    "text":text,
                    "image" : image_serialized.get("id"),
                    "user" : request.user.id,
            })
            if err is not None:
                return err

        else:
            text_serialized, err = repo_ticket.create_text_obj(data={
                    "text":text,
                    "user":request.user.id,
            })
            if err is not None:
                return err

        data["texts"] = [text_serialized.get("id"),]

        ticket_serialized, err = repo_ticket.create_ticket_obj(data=data)

        if err is not None:
            return err

        check_time = datetime.timestamp(
            datetime.fromtimestamp(ticket_serialized.get("last_update")) + \
                timedelta(days = 7)
        )

        check_for_ticket_expireness.apply_async(
            (ticket_serialized.get("id"),),
            countdown = check_time,
        )

        return response_creator(data=ticket_serialized)

class SendText(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        ticket_id = request.data.get("ticket_id")
        image = request.data.get("image", None)

        ticket_obj, err = repo_ticket.get_ticket_object_by_id(ticket_id)
        if err is not None:
            return err
        
        ticket_serialized = repo_ticket.get_ticket_data_by_obj(ticket_obj)

        if int(request.user.id) != int(ticket_serialized.get("user")):
            return response_creator(
                data={
                    "error":"permission denied"
                },
                status="fail",
                status_code=400
            )
        
        if image is not None:

            image_serialized, err = repo_idea.create_image_object(
                image=data.get("image"), 
                dir="tickets",
                 prefix_dir=request.user.id, 
                 limit_size=4000
            )
            if err is not None:
                return err

            text_serialized, err = repo_ticket.create_text_obj(data={
                    "text":text,
                    "image" : image_serialized.get("id"),
                    "user" : request.user.id,
            })
            if err is not None:
                return err

        else:

            text_serialized, err = repo_ticket.create_text_obj(data={
                    "text":text,
                    "user":request.user.id,
            })

            if err is not None:
                return err


        
        texts_list = ticket_serialized.get("texts")

        texts_list.append(text_serialized.get("id"))

        ticket_obj, err = repo_ticket.get_ticket_object_by_id(ticket_id)

        if err is not None:
            return err

        ticket_serialized, err = repo_ticket.update_ticket(
            ticket_obj, 
            data={
                "texts":texts_list,
                "status":"i",
                "last_update":text_serialized.get("create_date"),
            })
        if err is not None:
            return err

        return response_creator(data=ticket_serialized)

class ShowTicket(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        ticket_id = request.GET.get("ticket_id")

        ticket_obj, err = repo_ticket.get_ticket_object_by_id(ticket_id)
        if err is not None:
            return err

        ticket_serialized = TicketRoomDeepSerializer(ticket_obj)
        user = ticket_serialized.data.get("user")
        user_id = int(user.get("id"))

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
        tickets_serialized = repo_ticket.get_tickes_data_by_user(request.user.id)

        return response_creator(data={"tickets":tickets_serialized})

class EndTicket(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        ticket_id = request.data.get("ticket_id")
        ticket_obj, err = repo_ticket.get_ticket_object_by_id(ticket_id)
        if err is not None:
            return err
        
        ticket_serialized = repo_ticket.get_ticket_data_by_obj(ticket_obj)

        if int(request.user.id) != int(ticket_serialized.get("user")):
            return response_creator(
                data={
                    "error":"permission denid."
                },
                status="fail",
                status_code=400
            )
        
        ticket_serialized, err = repo_ticket.update_ticket(
            ticket_obj, 
            data={
                "status":"e",
                "last_update":datetime.timestamp(datetime.now()),
            })
        if err is not None:
            return err

        return response_creator(data=ticket_serialized)