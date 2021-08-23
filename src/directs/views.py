from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from datetime import date, datetime, timedelta
from time import mktime
from copy import deepcopy

from toolkit.toolkit import existence_error, response_creator, validate_error
from toolkit.image import upload_image, delete_image

from users.authentication import TokenAuthentication
from directs.models import (
    MessageBox,
    Message,
    AutomaticMessage,
    ChatRoom,
)

from ideas.models import Image
from ideas.serializers import ImageSerializer

from directs.serializers import (
    MessageBoxSerializer,
    MessageSerializer,
    AutomaticMessageSerializer,
    ChatRoomSerializer,
    ChatRoomDeepSerializer,
    MessageDeepSerializer,
)

from mongoengine.queryset.visitor import Q

PAGE_CAPACITY = 20


class CreateRoom(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        user_id = request.data.get("user_id")
        user2_id = request.user.id

        query = Q()

        query &= Q(users__in = [user_id,])

        query &= Q(users__in = [user2_id,])

        chatroom_obj = ChatRoom.objects.filter(query).first()

        if chatroom_obj is not None:
            return response_creator(
                data = {"error":"chatroom with this 2 users exist"},
                status="fail",
                status_code=400,
            )

        user_list = [user_id,user2_id,]

        chatroom_serialized = ChatRoomSerializer(data={"users":user_list})

        if not chatroom_serialized.is_valid():
            return validate_error(chatroom_serialized)
        
        chatroom_serialized.save()

        return response_creator(data= chatroom_serialized.data, status_code = 201)

class GetAllChatrooms(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        
        page_number = request.GET.get("page_number",0)

        chatroom_objs = ChatRoom.objects.filter(users__in = [request.user.id])[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
        
        chatrooms_serialized = ChatRoomDeepSerializer(chatroom_objs, many=True)

        return response_creator(data={"Chat Rooms":chatrooms_serialized.data})


class SendMessage(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        data = deepcopy(request.data)

        if data.get("title")  is not None:
            data.pop("title")
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

        chatroom_obj = ChatRoom.objects.filter(id=chatroom_id).first()

        if chatroom_obj is None:
            return existence_error("ChatRoom")
        
        chatroom_serialized = ChatRoomSerializer(chatroom_obj)

        users_list = chatroom_serialized.data.get("users")

        if request.user.id not in users_list:
            return response_creator(
                data={"error":"permission denied"},
                status="fail",
                status_code=403
            )

        if data.get("image") is not None:
            file_path = upload_image(
                file=request.data.get("image"),
                dir="directs",
                prefix_dir=[str(request.user.id)],
                limit_size=2000,
            )
            data.pop("image")
            image_serialized = ImageSerializer(image = file_path)
            if not image_serialized.is_valid():
                return validate_error(image_serialized)
        
            image_serialized.save()

            data["image"] = image_serialized.data.get("id")
            
        data["user"] = request.user.id

        messages_list = chatroom_serialized.data.get("messages")
        
        message_serialized = MessageSerializer(data=data)

        if not message_serialized.is_valid():
            return validate_error(message_serialized)

        message_serialized.save()
        
        messages_list.append(message_serialized.id)

        chatroom_serialized = ChatRoomSerializer(
            chatroom_obj,
            data = {"messages":messages_list},
            partial=True,
        )
        if not chatroom_serialized.is_valid():
            return validate_error(chatroom_serialized)

        chatroom_serialized.save()
    
        return response_creator(data=message_serialized.data,status_code=201)


class GetChatRoom(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self,request):
        chatroom_id = request.GET.get("chatroom_id")

        chatroom_obj = ChatRoom.objecta.filter(id=chatroom_id).first()

        if chatroom_obj is None:
            return existence_error("ChatRoom")

        chatroom_serialized = ChatRoomSerializer(chatroom_obj)

        users_list = chatroom_serialized.data.get("users")

        if request.user.id not in users_list:
            return response_creator(
                data={"error":"permission denied"},
                status="fail",
                status_code=403
            )
        messages_list = chatroom_serialized.data.get("messages")

        message_objs = Message.objects.filter(id__in = messages_list, user__ne=request.user.id)

        for msg_obj in message_objs:
            if not msg_obj.is_read:
                msg_serialized = MessageSerializer(
                    msg_obj,
                    data={"is_read":True,},
                    partial=True,
                )
                if not msg_serialized.is_valid():
                    return validate_error(msg_serialized)
        
                msg_serialized.save()
        
        message_objs = Message.objects.filter(id__in = messages_list)

        messages_serialized = MessageDeepSerializer(message_objs,many=True)

        return response_creator(data=messages_serialized.data)

class GetUnreadMessagesNumber(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        chatroom_id = request.GET.get("chatroom_id")

        chatroom_obj = ChatRoom.objects.filter(id=chatroom_id).first()

        if chatroom_obj is None:
            return existence_error("ChatRoom")

        chatroom_serialized = ChatRoomSerializer(chatroom_obj)

        users_list = chatroom_serialized.data.get("users")
        messages_list = chatroom_serialized.data.get("messages")


        if request.user.id not in users_list:
            return response_creator(
                data={"error":"permission denied"},
                status="fail",
                status_code=403
            )

        msg_unread_cnt = Message.objects.filter(id__in = messages_list, user__ne=request.user.id, is_read=False).count()

        return response_creator(data={"unread_msg_number":msg_unread_cnt})

class SearchChatRoomByUserID(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_id = request.GET.get("user_id")
        user2_id = request.user.id

        query = Q()

        query &= Q(users__in = [user_id,])

        query &= Q(users__in = [user2_id,])

        chatroom_obj = ChatRoom.objects.filter(query).first()

        if chatroom_obj is None:
            return existence_error("ChatRoom")

        chatroom_serialized = ChatRoomDeepSerializer(chatroom_obj)

        return response_creator(data=chatroom_serialized.data)



        

        





        
        

        
