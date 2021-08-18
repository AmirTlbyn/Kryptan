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
)

from ideas.models import Image
from ideas.serializers import ImageSerializer

from directs.serializers import (
    MessageBoxSerializer,
    MessageSerializer,
    AutomaticMessageSerializer,
)


class SendMessage(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        data = deepcopy(request.data)

        if data.get("title")  is not None:
            data.pop("title")
        if data.get("is_read") is not None:
            data.pop("is_read")
        if data.get("reciever_id") is None:
            return response_creator(
                data={"error":"message must have reciever_id"},
                status="fail",
                status_code=400
            )
        reciever_id = data.get("reciever_id")
        data.pop("reciever_id")

        sender_messagebox_obj = MessageBox.objects.filter(user = request.user.id).first()
        if sender_messagebox_obj is None:
            return response_creator(
                data={"error":"sender message box doesn't exist"},
                status_code=400,
                status="fail"
                )

        sender_msgbox_serialized = MessageBoxSerializer(sender_messagebox_obj)

        reciever_messagebox_obj = MessageBox.objects.filter(user = reciever_id).first()
        if reciever_messagebox_obj is None:
            return response_creator(
                data={"error":"reciever message box doesn't exist "},
                status="fail",
                status_code=400
                )

        reciever_msgbox_serialized = MessageBoxSerializer(reciever_messagebox_obj)


        file_path = upload_image(
            file=request.data.get("image"),
            dir="directs",
            prefix_dir=[str(request.user.id)],
            limit_size=2000,
        )
        data.pop("image")
        data["user"] = request.user.id

        image_serialized = ImageSerializer(image = file_path)
        if not image_serialized.is_valid():
            return validate_error(image_serialized)
        
        image_serialized.save()

        data["image"] = image_serialized.data.get("id")

        message_serialized = MessageSerializer(data=data)

        if not message_serialized.is_valid():
            return validate_error(message_serialized)

        message_serialized.save()

        sender_msg_list = sender_msgbox_serialized.data.get("messages")

        reciever_msg_list = reciever_msgbox_serialized.data.get("messages")
        reciver_unread = reciever_msgbox_serialized.data.get("unread")

        sender_msg_list.append(message_serialized.data.get("id"))
        reciever_msg_list.append(message_serialized.data.get("id"))

        reciver_unread +=1

        sender_msgbox_serialized = MessageBoxSerializer(
            sender_messagebox_obj,
            data={
                "messages":sender_msg_list,
            },
            partial=True,
        )
        if not sender_msgbox_serialized.is_valid():
            return validate_error(sender_msg_serialized)
        sender_msgbox_serialized.save()

        reciever_msgbox_serialized = MessageBoxSerializer(
            reciever_messagebox_obj,
            data={
                "messages":reciever_msg_list,
                "unread":reciver_unread,
            },
            partial=True
        )
        if not reciever_msgbox_serialized.is_valid():
            return validate_error(reciever_msgbox_serialized)
        
        return response_creator(data=message_serialized.data,status_code=201)


class ReadMessages(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        user_id = request.data.get("user_id")

        messagebox_obj = MessageBox.objects.filter(user=request.user.id).first()

        if messagebox_obj is None:
            return existence_error("MessageBox")
        
        messagebox_serialized = MessageSerializer(messagebox_obj)

        messages_list = messagebox_serialized.data.get("messages")

        message_objs = Message.objects.filter(
            id__in = messages_list,
            user=user_id,
        )

        messages_serialized = MessageSerializer(message_objs, many=True)



        



        
        

        
