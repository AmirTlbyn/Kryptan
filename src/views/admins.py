#Django libs
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

#Python lib
from copy import deepcopy

#Internal libs
from apps.users.authentication import TokenAuthentication
from toolkit.toolkit import existence_error, response_creator, validate_error
from toolkit.image import upload_image, delete_image
from repositories.permissions import IsSuperUser
from apps.users.models import (
    User,
    Plan,
)
from apps.users.serializers import(
    UserDeepSerializer,
    UserSerializer,
    AdminUserDeepSerializer,
    AdminUserSerializer,
    PlanSerializer,
)
from apps.ideas.models import Idea, Image
from apps.ideas.serializers import IdeaDeepSerializer, IdeaSerializer, ImageSerializer

from apps.tickets.models import TicketText,TicketRoom
from apps.tickets.serializers import (
    TicketRoomSerializer,
    TicketRoomDeepSerializer,
    TicketTextSerializer
)
from apps.directs.models import MessageBox,AutomaticMessage
from apps.directs.serializers import MessageBoxSerializer,AutomaticMessageSerializer
from repositories.auto_msg import send_message
from apps.symbols.models import Symbol
from apps.symbols.serializers import SymbolSerializer


#VARIABELS
PAGE_CAPACITY = 50

#_________________________________USERS__________________________

class ShowUsers(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        order_by = request.data.get("order_by")
        page_number = request.data.get("page_number", 0)

        user_objs = User.objects.all().order_by(order_by)[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]

        users_serialized = AdminUserDeepSerializer(user_objs, many=True)

        return response_creator(data={"users":users_serialized.data})

class ChangeRole(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        user_id = request.data.get("user_id")
        role = request.data.get("role")


        user_obj = User.objects.filter(id = user_id).first()

        if user_obj is None:
            return existence_error("User")

        user_serialized = AdminUserSerializer(
            user_obj,
            data={
                "role":role
            },
            partial=True,
        )
        if not user_serialized.is_valid():
            return validate_error(user_serialized)

        user_serialized.save()

        return response_creator(data = user_serialized.data)

class BanUser(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        user_id = request.data.get("user_id")
        is_active = request.data.get("is_active")

        user_obj = User.objects.filter(id=user_id).first()

        if user_obj is None:
            return existence_error("User")

        user_serialized = AdminUserSerializer(
            user_obj,
            data={"is_active":is_active},
            partial=True,
        )

        if not user_serialized.is_valid():
            return validate_error(user_serialized)

        user_serialized.save()

        return response_creator(data=user_serialized.data)

class ChangePlan(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):

        user_id = request.data.get("user_id")

        plan_version = request.data.get("plan_version")
        expire_date = request.data.get("expire_date")

        user_obj = User.objects.filter(id = user_id).first()

        if user_obj is None:
            return existence_error("User")

        user_serialized = AdminUserSerializer(user_obj)

        plan_id = user_serialized.data.get("plan")

        plan_obj = Plan.objects.filter(id=plan_id).first()

        if plan_obj is None:

            plan_serialized = PlanSerializer(data={
                "plan_version":plan_version,
                "expire_date":expire_date,
            })

            if not plan_serialized.is_valid():
                return validate_error(plan_serialized)
            plan_serialized.save()
            return response_creator(data=plan_serialized.data)

        if plan_version == 0 :
            plan_obj.delete()
            return response_creator()

        plan_serialized = PlanSerializer(
            plan_obj,
            data={
                "plan_version":plan_version,
                "expire_date":expire_date,
            },
            partial=True,
        )

        if not plan_serialized.is_valid():
            return validate_error(plan_serialized)
        plan_serialized.save()

        return response_creator(data=plan_serialized.data)


#_________________________________IDEAS__________________________

class DeleteIdea(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def delete(self, request):
         
        idea_id = request.data.get("idea_id")
        idea_obj = Idea.objects.filter(id=idea_id).first()        

        if idea_obj is None:
            return existence_error("Idea")
        
        idea_serialized = IdeaSerializer(idea_obj)
        idea_obj.delete()

        return response_creator()

class ChangeHideness(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        idea_id = request.data.get("idea_id")
        is_hide = request.data.get("is_hide")
        idea_obj = Idea.objects.filter(id=idea_id).first()        

        if idea_obj is None:
            return existence_error("Idea")
        
        idea_serialized = IdeaSerializer(
            idea_obj,
            data={
                "is_hide":is_hide,
            },
            partial=True
        )

        if not idea_serialized.is_valid():
            return validate_error(idea_serialized)

        idea_serialized.save()

class ShowAllIdeas(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        order_by = request.GET.get("order_by")
        page_number = request.GET.get("page_number", 0)
        idea_objs = Idea.objects.all().order_by(order_by)[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]

        ideas_serialized = IdeaSerializer(idea_objs,many=True)

        return response_creator(data={"ideas":ideas_serialized.data})



#_________________________________TICKETS__________________________

class ShowAllTickets(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        order_by = request.GET.get("order_by")

        ticket_objs = TicketRoom.objects.all().order_by(order_by)

        tickets_serialized = TicketRoomSerializer(ticket_objs)

        return response_creator(data={"tickets":tickets_serialized.data})

class SendText(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        ticket_id = request.data.get("ticket_id")
        ticket_obj = TicketRoom.objects.filter(id = ticket_id).first()

        if ticket_obj is None:
            return existence_error("Ticket")

        ticket_serializer = TicketRoomSerializer(ticket_obj)

        texts_list = ticket_serializer.data.get("texts")

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

        texts_list.append(text_serialized.data.get("id"))

        ticket_serialized = TicketRoomSerializer(
            ticket_obj,
            data={
                "texts":texts_list,
                "status":"a",
            },
            partial=True
        )

        if not ticket_serialized.is_valid():
            return validate_error(ticket_serialized)
        ticket_serialized.save()


        return response_creator(data=ticket_serialized.data)

class EndTicket(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        ticket_id = request.data.get("ticket_id")

        ticket_obj = TicketRoom.objects.filter(id=ticket_id).first()

        if ticket_obj is None:
            return existence_error("Ticket")

        ticket_serialized = TicketRoomSerializer(ticket_obj)
        
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

#_________________________________NOTIFICATIONS__________________________

class SendBanWarn(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)
    
    def post(self, request):
        user_id = request.data.get("user_id")

        user_obj = User.objects.filter(id=user_id).first()

        if user_obj is None:
            existence_error("User")

        user_serialized = UserSerializer(user_obj)

        send_message(user_serialized=user_serialized ,ban_bool=True)

        return response_creator(data={"message":"notif sent."})

class SendNotif(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        user_id = request.data.get("user_id")
        text = request.data.get("text")
        title = request.data.get("title")

        user_obj = User.objects.filter(id=user_id).first()

        if user_obj is None:
            existence_error("User")

        user_serialized = UserSerializer(user_obj)

        send_message(user_serialized=user_serialized,other=True,title=title,msg_text=text)

        return response_creator(data={"message":"notif sent!"})


class SendNotif2All(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        text = request.data.get("text")
        title = request.data.get("title")    
        automatic_message_serialized = AutomaticMessageSerializer(data={
        "title" : title,
        "text" : text,
        })
        if not automatic_message_serialized.is_valid():
            return  validate_error(automatic_message_serialized)
        automatic_message_serialized.save()
        messagebox_objs = MessageBox.objects.all()
        
        for msg_box in messagebox_objs:

            msgbox_serialized = MessageBoxSerializer(msg_box)

            automsg_list = msgbox_serialized.data.get("automatic_messages")
            automsg_unread = msgbox_serialized.data.get("automatic_msg_unread")

            automsg_list.append(automatic_message_serialized.data.id)
            automsg_unread += 1

            msgbox_serialized = MessageBoxSerializer(
                msg_box,
                data={
                    "automatic_messages": automsg_list,
                    "automatic_msg_unread": automsg_unread,
                },
                partial=True
            )

            if not msgbox_serialized.is_valid():
                return validate_error(msgbox_serialized)

            msgbox_serialized.save()

            user_obj = User.objects.filter(id=int(msgbox_serialized.data.get("user"))).first()

            if user_obj is None:
                return existence_error("User")
            user_serialized = UserSerializer(user_obj)
            # send push notification
            if user_serialized.data.get("device_token") is not None:
                push_notification(
                title = "کریپتان",
                text = text,
                device_token = user_serialized.data.get("device_token"),
            )

        return response_creator(data={"message":"notifs sent!"})

class SendNotif2Premiums(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        text = request.data.get("text")
        title = request.data.get("title")

        automatic_message_serialized = AutomaticMessageSerializer(data={
            "title" : title,
            "text" : text,
        })
        if not automatic_message_serialized.is_valid():
            return  validate_error(automatic_message_serialized)
        automatic_message_serialized.save()  

        user_objs = User.objects.filter(plan__plan_version="2")
        user_list=[]
        for user_obj in user_objs:
            user_list.append(user_obj.id)
        
        messagebox_objs = MessageBox.objects.filter(user__in=user_list)

        for msg_box in messagebox_objs:

            msgbox_serialized = MessageBoxSerializer(msg_box)

            automsg_list = msgbox_serialized.data.get("automatic_messages")
            automsg_unread = msgbox_serialized.data.get("automatic_msg_unread")

            automsg_list.append(automatic_message_serialized.data.id)
            automsg_unread += 1

            msgbox_serialized = MessageBoxSerializer(
                msg_box,
                data={
                    "automatic_messages": automsg_list,
                    "automatic_msg_unread": automsg_unread,
                },
                partial=True
            )

            if not msgbox_serialized.is_valid():
                return validate_error(msgbox_serialized)

            msgbox_serialized.save()

            user_obj = User.objects.filter(id=int(msgbox_serialized.data.get("user"))).first()

            if user_obj is None:
                return existence_error("User")
            user_serialized = UserSerializer(user_obj)
            # send push notification
            if user_serialized.data.get("device_token") is not None:
                push_notification(
                title = "کریپتان",
                text = text,
                device_token = user_serialized.data.get("device_token"),
            )

        return response_creator(data={"message":"notifs sent!"})

class SendNotif2Pros(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        text = request.data.get("text")
        title = request.data.get("title")

        automatic_message_serialized = AutomaticMessageSerializer(data={
            "title" : title,
            "text" : text,
        })
        if not automatic_message_serialized.is_valid():
            return  validate_error(automatic_message_serialized)
        automatic_message_serialized.save()  

        user_objs = User.objects.filter(plan__plan_version="1")
        user_list=[]
        for user_obj in user_objs:
            user_list.append(user_obj.id)
        
        messagebox_objs = MessageBox.objects.filter(user__in=user_list)

        for msg_box in messagebox_objs:

            msgbox_serialized = MessageBoxSerializer(msg_box)

            automsg_list = msgbox_serialized.data.get("automatic_messages")
            automsg_unread = msgbox_serialized.data.get("automatic_msg_unread")

            automsg_list.append(automatic_message_serialized.data.id)
            automsg_unread += 1

            msgbox_serialized = MessageBoxSerializer(
                msg_box,
                data={
                    "automatic_messages": automsg_list,
                    "automatic_msg_unread": automsg_unread,
                },
                partial=True
            )

            if not msgbox_serialized.is_valid():
                return validate_error(msgbox_serialized)

            msgbox_serialized.save()

            user_obj = User.objects.filter(id=int(msgbox_serialized.data.get("user"))).first()

            if user_obj is None:
                return existence_error("User")
            user_serialized = UserSerializer(user_obj)
            # send push notification
            if user_serialized.data.get("device_token") is not None:
                push_notification(
                title = "کریپتان",
                text = text,
                device_token = user_serialized.data.get("device_token"),
            )

        return response_creator(data={"message":"notifs sent!"})



#_________________________________SYMBOLS__________________________

class CreateSymbol(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        data = deepcopy(request.data)

        file_path_40 = upload_image(
            file=data.get("logo_40"),
            dir="symbols",
            prefix_dir=[data.get("name")],
            limit_size=4000,
            )

        desc_40 = str(data.get("name")) + " " + str(data.get("name_fa")) + " " + str(data.get("symbol"))
        
        logo_40_serialized = ImageSerializer(
            data={
                "image":file_path_40,
                "description":desc_40,
        })

        if not logo_40_serialized.is_valid():
            return validate_error(logo_40_serialized)

        logo_40_serialized.save()

        file_path_24 = upload_image(
            file=data.get("logo_24"),
            dir="symbols",
            prefix_dir=[data.get("name")],
            limit_size=4000,
            )
        desc_24 = str(data.get("name")) + " " + str(data.get("name_fa")) + " " + str(data.get("symbol"))
        
        logo_24_serialized = ImageSerializer(
            data={
                "image":file_path_24,
                "description":desc_24,
        })

        if not logo_24_serialized.is_valid():
            return validate_error(logo_24_serialized)

        logo_24_serialized.save()

        data["logo_24"] = logo_24_serialized.data.id
        data["logo_40"] = logo_40_serialized.data.id

        symbol_serialized = SymbolSerializer(data=data)

        if not symbol_serialized.is_valid():
            return validate_error(symbol_serialized)

        symbol_serialized.save()

        return response_creator(data=symbol_serialized.data, status_code=201)



