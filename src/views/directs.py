#Django libs
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from mongoengine.queryset.visitor import Q

#Python libs
from datetime import date, datetime, timedelta
from time import mktime
from copy import deepcopy

#Internal libs
from toolkit.toolkit import existence_error, response_creator, validate_error
from toolkit.image import upload_image, delete_image
from apps.users.authentication import TokenAuthentication
from apps.ideas.models import Image
from apps.ideas.serializers import ImageSerializer
from apps.directs.models import (
    MessageBox,
    Message,
    AutomaticMessage,
    ChatRoom,
)
from apps.directs.serializers import (
    MessageBoxSerializer,
    MessageSerializer,
    AutomaticMessageSerializer,
    ChatRoomSerializer,
    ChatRoomDeepSerializer,
    MessageDeepSerializer,
)
import repositories.directs as repo_direct

#VARIABELS
PAGE_CAPACITY = 20


class CreateRoom(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        user_list = [request.data.get("user_id"),equest.user.id,]

        chatroom_objs = repo_direct.get_room_obj_by_users(user_list)
        
        if len(chatroom_objs) != 0:
            return response_creator(
                data = {"error":"chatroom with this 2 users exist"},
                status="fail",
                status_code=400,
            )
        
        chatroom_serialized, err = repo_direct.create_room_object(data={"users":user_list})

        if err is not None:
            return err

        return response_creator(data= chatroom_serialized, status_code = 201)

class GetAllRooms(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        page_number = request.GET.get("page_number",0)

        chatroom_objs = repo_direct.get_room_obj_by_users([request.user.id,])[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
        
        chatrooms_serialized = ChatRoomDeepSerializer(chatroom_objs, many=True)

        return response_creator(data={"Chat Rooms":chatrooms_serialized.data})


class SendMessage(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        data = deepcopy(request.data)

        if data.get("is_read") is not None:
            data.pop("is_read")
        if data.get("chatroom_id") is None:
            return response_creator(
                data={"error":"message must have chatroom_id"},
                status="fail",
                status_code=400
            )
        chatroom_id = data.get("chatroom_id")
        data.pop("chatroom_id")

        chatroom_obj, err = repo_direct.get_room_object_by_id(chatroom_id)
        if err is not None:
            return err
        
        chatroom_serialized = repo_direct.get_room_data_by_obj(chatroom_obj)

        users_list = chatroom_serialized.get("users")

        if request.user.id not in users_list:
            return response_creator(
                data={"error":"permission denied."},
                status="fail",
                status_code=403
            )

        if data.get("image") is not None:
            image_serialized, err = repo.ideas.create_image_object(image=image,dir="directs",prefix_dir= request.user.id,limit_size = 2000)

            if err is not None:
                return err
            data["image"] = image_serialized.get("id")
            
        data["user"] = request.user.id

        messages_list = chatroom_serialized.get("messages")
        
        message_serialized, err = repo_direct.create_message_object(data)

        if err is not None:
            return err
        
        messages_list.append(message_serialized.get("id"))
        
        chatroom_serialized, err = repo_direct.update_room(
            room_obj =chatroom_obj,
            data = {"users": user_list}
        )

        if err is not None:
            return err
    
        return response_creator(data=message_serialized,status_code=201)


class GetRoom(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self,request):
        chatroom_id = request.GET.get("chatroom_id")
        
        chatroom_serialized, err = repo_direct.get_room_data_by_id(chatroom_id)

        if err is not None:
            return err

        users_list = chatroom_serialized.get("users")

        if request.user.id not in users_list:
            return response_creator(
                data={"error":"permission denied"},
                status="fail",
                status_code=403
            )
        messages_list = chatroom_serialized.get("messages")

        message_objs = Message.objects.filter(id__in = messages_list, user__ne=request.user.id)

        for msg_obj in message_objs:
            if not msg_obj.is_read:
                msg_serialized, err = repo_direct.update_message(
                    msg_obj,
                    data={"is_read":True,}
                )
                if err is not None:
                    return err
        
        message_objs = Message.objects.filter(id__in = messages_list)

        messages_serialized = MessageDeepSerializer(message_objs,many=True)

        return response_creator(data=messages_serialized.data)

class GetUnreadMessagesNumber(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        chatroom_id = request.GET.get("chatroom_id")
        chatroom_obj, err = repo_direct.get_room_object_by_id(chatroom_id)
        if err is not None:
            return err

        chatroom_serialized = repo_direct.get_room_data_by_obj(chatroom_obj)
 
        users_list = chatroom_serialized.get("users")
        messages_list = chatroom_serialized.get("messages")


        if request.user.id not in users_list:
            return response_creator(
                data={"error":"permission denied"},
                status="fail",
                status_code=403
            )

        msg_unread_cnt = Message.objects.filter(id__in = messages_list, user__ne=request.user.id, is_read=False).count()

        return response_creator(data={"unread_msg_number":msg_unread_cnt})

class GetAllMessageNumber(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        
        chatrooms_objs = repo_direct.get_room_obj_by_users([request.user.id,])
        cnt = 0
        for chtr_obj in chatrooms_objs:
            chtr_serialized = ChatRoomSerializer(chtr_obj)
            msg_list = chtr_serialized.data.get("messages")

            cnt = cnt + Message.objects.filter(id__in = msg_list, user__ne = request.user.id, is_read=False).count()
        
        return response_creator(data={"unread_msg_number":cnt})


class SearchRoomByUserID(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_id = request.GET.get("user_id")
        user2_id = request.user.id

        chatroom_obj = repo_direct.get_room_obj_by_users([request.GET.get("user_id"),request.user.id])

        if chatroom_obj is None:
            return existence_error("ChatRoom")
        
        chatroom_serialized = ChatRoomDeepSerializer(chatroom_obj)

        return response_creator(data=chatroom_serialized.data)
