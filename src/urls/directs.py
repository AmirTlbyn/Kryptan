#Django lib
from django.urls import path

#Internal libs
from views.directs import (
    CreateRoom,
    GetAllRooms,
    SendMessage,
    GetRoom,
    GetUnreadMessagesNumber,
    GetAllMessageNumber,
    SearchRoomByUserID,
)

urlpatterns = [
    path("create_room",CreateRoom.as_view()),
    path("get_all_rooms", GetAllRooms.as_view()),
    path("send_message",SendMessage.as_view()),
    path("get_room",GetRoom.as_view()),
    path("get_room_unread_messages",GetUnreadMessagesNumber.as_view()),
    path("get_all_unread_messages", GetAllMessageNumber.as_view()),
    path("search_room_by_user",SearchRoomByUserID.as_view()),
]