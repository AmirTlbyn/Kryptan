#Django libs
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

#Python lib
from copy import deepcopy
from datetime import datetime

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
import repositories.users as repo_user
import repositories.ideas as repo_idea
import repositories.tickets as repo_ticket
import repositories.directs as repo_direct
import repositories.admins as repo_admin
import repositories.symbols as repo_symbol

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


        user_obj, err = repo_user.get_user_object_by_id(user_id)
        if err is not None:
            return err

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

        user_obj, err = repo_user.get_user_object_by_id(user_id)
        if err is not None:
            return err

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

        user_obj, err = repo_user.get_user_object_by_id(user_id)
        if err is not None:
            return err

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

        if plan_version == "0" :
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
        idea_obj, err = repo_idea.get_idea_object_by_id(idea_id)
        if err is not None:
            return err       
     
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
        
        idea_serialized, err = repo_idea.update_idea(
            idea_obj,
            data={
                "is_hide":is_hide,
        })
        if err is not None:
            return err

        return response_creator(data=idea_serialized)

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

class GetInProgressTickets (APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        order_by = request.GET.get("order_by")

        ticket_objs = TicketRoom.objects.filter(status="i")

        tickets_serialized = TicketRoomSerializer(ticket_objs, many=True)

        return response_creator(data={"tickets": tickets_serialized.data})

class SendText(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        ticket_id = request.data.get("ticket_id")
        ticket_obj, err = repo_ticket.get_ticket_object_by_id(ticket_id)
        if err is not None:
            return err

        ticket_serializer = repo_ticket.get_ticket_data_by_obj(ticket_obj)

        texts_list = ticket_serializer.get("texts")

        if image is not None:
            image_serialized, err = repo_idea.create_image_object(
                image=data.get("image"),
                dir="tickets",
                prefix_dir=request.user.id,
                limit_size=4000,
            )
            if err is not None:
                return err

            text_serialized, err = repo_ticket.create_text_obj(
                data={
                    "text":text,
                    "image" : image_serialized.data.get("id"),
                    "user" : request.user.id,
            })
            if err is not None:
                return err
        else:

            text_serialized, err = repo_ticket.create_text_obj(
                data={
                    "text":text,
                    "user":request.user.id,
            })
            if err is not None:
                return err

        texts_list.append(text_serialized.get("id"))

        ticket_serialized, err = repo_ticket.update_ticket(
            ticket_obj,
            data={
                "texts":texts_list,
                "status":"a",
                "last_update":text_serialized.get("create_date"),
        })
        if err is not None:
            return err

        return response_creator(data=ticket_serialized)

class EndTicket(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        ticket_id = request.data.get("ticket_id")

        ticket_obj, err = repo_ticket.get_ticket_object_by_id(ticket_id)
        if err is not None:
            return err
        
        ticket_serialized, err = repo_ticket.update_ticket(
            ticket_obj,
            data={
                "status":"e",
                "last_update":datetime.timestamp(datetime.now()),
        })
        if err is not None:
            return err

        return response_creator(data=ticket_serialized)

#_________________________________NOTIFICATIONS__________________________

class SendBanWarn(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)
    
    def post(self, request):
        user_id = request.data.get("user_id")

        user_obj,err = repo_user.get_user_object_by_id(user_id)
        if err is not None:
            return err

        user_serialized = repo_user.get_user_data_by_obj(user_obj)

        send_message(user_serialized=user_serialized ,ban_bool=True)

        return response_creator(data={"message":"notif sent."})

class SendNotif(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        user_id = request.data.get("user_id")
        text = request.data.get("text")
        title = request.data.get("title")

        user_obj,err = repo_user.get_user_object_by_id(user_id)
        if err is not None:
            return err

        user_serialized = repo_user.get_user_data_by_obj(user_obj)

        send_message(user_serialized=user_serialized,other=True,title=title,msg_text=text)

        return response_creator(data={"message":"notif sent!"})


class SendNotif2All(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        text = request.data.get("text")
        title = request.data.get("title")    
        automatic_message_serialized, err = repo_direct.create_automatic_message_object(
            data={
                "title" : title,
                "text" : text,})
        if err is not None:
            return err

        messagebox_objs = MessageBox.objects.all()
        
        for msg_box in messagebox_objs:

            msgbox_serialized = MessageBoxSerializer(msg_box)

            automsg_list = msgbox_serialized.data.get("automatic_messages")
            automsg_unread = msgbox_serialized.data.get("automatic_msg_unread")

            automsg_list.append(automatic_message_serialized.data.id)
            automsg_unread += 1

            msgbox_serialized, err = repo_direct.update_msgbox(
                msg_box,
                data={
                    "automatic_messages": automsg_list,
                    "automatic_msg_unread": automsg_unread,
            })
            if err is not None:
                return err

            user_obj, err = repo_user.get_user_object_by_id(int(msgbox_serialized.get("user")))
            if err is not None:
                return err

            user_serialized = repo_user.get_user_data_by_obj(user_obj)
            # send push notification
            if user_serialized.get("device_token") is not None:
                push_notification(
                    title = "کریپتان",
                    text = text,
                    device_token = user_serialized.get("device_token"),
                )

        return response_creator(data={"message":"notifs sent!"})

class SendNotif2Premiums(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        text = request.data.get("text")
        title = request.data.get("title")

        automatic_message_serialized, err = repo_direct.create_automatic_message_object (
            data={
                "title" : title,
                "text" : text,
        })
        if err is not None:
            return err

        user_objs = User.objects.filter(plan__plan_version="2")
        user_list=[]
        for user_obj in user_objs:
            user_list.append(user_obj.id)
        
        messagebox_objs = MessageBox.objects.filter(user__in=user_list)

        for msg_box in messagebox_objs:

            msgbox_serialized = MessageBoxSerializer(msg_box)

            automsg_list = msgbox_serialized.data.get("automatic_messages")
            automsg_unread = msgbox_serialized.data.get("unread")

            automsg_list.append(automatic_message_serialized.get("id"))
            automsg_unread += 1

            msgbox_serialized, err = repo_direct.update_msgbox(
                msg_box,
                data={
                    "automatic_messages": automsg_list,
                    "unread": automsg_unread,
                }
            )
            if err is not None:
                return err

            user_obj, err = repo_user.get_user_object_by_id(int(msgbox_serialized.data.get("user")))
            if err is not None:
                return err

            user_serialized = repo_user.get_user_data_by_obj(user_obj)
            # send push notification
            if user_serialized.get("device_token") is not None:
                push_notification(
                title = "کریپتان",
                text = text,
                device_token = user_serialized.get("device_token"),
            )

        return response_creator(data={"message":"notifs sent!"})

class SendNotif2Pros(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        text = request.data.get("text")
        title = request.data.get("title")

        automatic_message_serialized, err = repo_direct.create_automatic_message_object (
            data={
                "title" : title,
                "text" : text,
        })
        if err is not None:
            return err

        user_objs = User.objects.filter(plan__plan_version="1")
        user_list=[]
        for user_obj in user_objs:
            user_list.append(user_obj.id)
        
        messagebox_objs = MessageBox.objects.filter(user__in=user_list)

        for msg_box in messagebox_objs:

            msgbox_serialized = MessageBoxSerializer(msg_box)

            automsg_list = msgbox_serialized.data.get("automatic_messages")
            automsg_unread = msgbox_serialized.data.get("unread")

            automsg_list.append(automatic_message_serialized.get("id"))
            automsg_unread += 1

            msgbox_serialized, err = repo_direct.update_msgbox (
                msg_box,
                data={
                    "automatic_messages": automsg_list,
                    "unread": automsg_unread,
            })
            if err is not None:
                return err

            user_obj, err = repo_user.get_user_object_by_id(int(msgbox_serialized.data.get("user")))
            if err is not None:
                return err

            user_serialized = repo_user.get_user_data_by_obj(user_obj)

            # send push notification
            if user_serialized.get("device_token") is not None:
                push_notification(
                title = "کریپتان",
                text = text,
                device_token = user_serialized.get("device_token"),
            )

        return response_creator(data={"message":"notifs sent!"})



#_________________________________SYMBOLS__________________________

class CreateSymbol(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        data = deepcopy(request.data)

        logo_40_serialized, err = repo_idea.create_image_object(
            image=data.get("logo_40"),
            dir="symbols",
            prefix_dir=data.get("name"),
            limit_size=4000,
            desc=str(data.get("name")) + " " + str(data.get("name_fa")) + " " + str(data.get("symbol"))
            )
        if err is not None:
            return err
        
        logo_24_serialized, err = repo_idea.create_image_object(
            image=data.get("logo_24"),
            dir="symbols",
            prefix_dir=data.get("name"),
            limit_size=4000,
            desc=str(data.get("name")) + " " + str(data.get("name_fa")) + " " + str(data.get("symbol"))
        )
        if err is not None:
            return err

        data["logo_24"] = logo_24_serialized.get("id")
        data["logo_40"] = logo_40_serialized.get("id")

        symbol_serialized, err = repo_symbol.create_symbol_object(data=data)
        if err is not None:
            return err

        return response_creator(data=symbol_serialized, status_code=201)


#_________________________________TETHERTOMAN__________________________

class UpdateTetherToman(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        price = request.data.get("price")
        tethertoman_obj, err = repo_admin.get_tethertoman_obj()
        if err is not None:
            return err

        tethertoman_serialized, err = repo_admin.update_tethertoman(
            tethertoman_obj,
            price=price
        )
        if err is not None:
            return err

        return response_creator(data=tethertoman_serialized)



