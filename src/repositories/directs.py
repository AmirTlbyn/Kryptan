#Django libs
from mongoengine.queryset.visitor import Q
from rest_framework.response import Response

#Python libs
from copy import deepcopy

#Internal libs
from apps.directs.models import (
    MessageBox,
    Message,
    AutomaticMessage,
    ChatRoom,
)
from apps.directs.serializers import (
    MessageBoxSerializer,
    MessageBoxDeepSerializer,
    MessageSerializer,
    MessageDeepSerializer,
    AutomaticMessageSerializer,
    ChatRoomSerializer,
    ChatRoomDeepSerializer,
)
from toolkit.toolkit import existence_error, validate_error

#_________________________CREATE______________________________

def create_message_object(data :dict) -> (dict, Response):
    err = None

    message_serialized = MessageSerializer(data)

    if not message_serialized.is_valid():
        err = validate_error(message_serialized)
        return {}, err
    
    message_serialized.save()
    return message_serialized.data, err

def create_room_object (data : dict) -> (dict, Response):
    err = None

    chtroom_serialized = ChatRoomSerializer(data=data)

    if not chtroom_serialized.is_valid():
        err = validate_error(chtroom_serialized)
        return {}, err
    
    chtroom_serialized.save()

    return chtroom_serialized.data, err

def create_automatic_message_object (data :dict) -> (dict, Response):
    err = None

    automatic_msg_serialized = AutomaticMessageSerializer(data=data)

    if not automatic_msg_serialized.is_valid():
        err = validate_error(automatic_msg_serialized)
        return {}, err
    
    automatic_msg_serialized.save()

    return automatic_msg_serialized.data, err


#_________________________GET______________________________

def get_room_obj_by_users(users : list) -> (list):
    if len(users) == 0:
        chtroom_objs = ChatRoom.objects.all()
    elif len(users) == 1:
        chtroom_objs = ChatRoom.objects.filter(users__in = users)
    else:
        query = Q()
        query &= Q(users__in = [users[0],])
        query &= Q(users__in = [users[1],])

        chatroom_obj = ChatRoom.objects.filter(query)

    return chtroom_objs

def get_room_object_by_id(room_id :int) -> (object,Response):
    err = None

    chtroom_obj = ChatRoom.objects.filter(id=room_id).first()
    
    if chtroom_objs is None:
        err = existence_error("ChatRoom")
        return None, err

    return chtroom_obj,err
    
def get_room_data_by_obj (room_obj) -> dict:
    chtroom_serialized = ChatRoomSerializer(room_obj)

    return chtroom_serialized.data

def get_msgbox_object_by_user (user_id: int) -> (object, Response):
    err = None

    msgbox_obj = MessageBox.objects.filter(user= user_id).first()

    if msgbox_obj is None:
        err = existence_error("MessageBox")
        return None, err

    return msgbox_obj, err

def get_msgbox_data_by_obj (msgbox_obj) -> dict:
    msgbox_serialized = MessageBoxSerializer(msgbox_obj)

    return msgbox_serialized.data


#_________________________UPDATE______________________________

def update_room (room_obj, data) -> (dict, Response):
    err = None

    chatroom_serialized = ChatRoomSerializer(
        room_obj,
        data=data,
        partial = True
    )

    if not chatroom_serialized.is_valid():
        err = validate_error(chatroom_serialized)
        return {}, err
    
    chatroom_serialized.save()

    return chatroom_serialized.data, err

def update_automatic_msg (am_obj, data) -> (dict, Response):
    err = None

    automatic_msg_serialized = AutomaticMessageSerializer(
        am_obj,
        data=data,
        partial=True
    )

    if not automatic_msg_serialized.is_valid():
        err = validate_error(automatic_msg_serialized)
        return {}, err

    automatic_msg_serialized.save()

    return automatic_msg_serialized.data, err

def update_msgbox (msgbox_obj, data) -> (dict, Response):
    err = None

    msgbox_serialized = MessageBoxSerializer(
        msgbox_obj,
        data=data,
        partial=True
    )

    if not msgbox_serialized.is_valid():
        err = validate_error(msgbox_serialized)
        return {}, err

    msgbox_serialized.save()

    return msgbox_serialized.data , err

def update_message (msg_obj, data) -> (dict, Response):
    err = None

    msg_serialized = MessageBoxSerializer(
        msg_obj,
        data=data,
        partial=True
    )
    
    if not msg_serialized.is_valid():
        err = validate_error(msg_serialized)
        return {}, err

    msg_serialized.save()

    return msg_serialized.data, err



