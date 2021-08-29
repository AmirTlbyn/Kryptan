#Django lib
from django.urls import path

#Internal libs
from views.tickets import (
    CreateTicket,
    SendText,
    ShowTicket,
    GetAllTickets,
    EndTicket
)

urlpatterns = [
    path("create_ticket", CreateTicket.as_view()),
    path("send_text", SendText.as_view()),
    path("show_ticket", ShowTicket.as_view()),
    path("get_all_tickets", GetAllTickets.as_view()),
    path("close_ticket", EndTicket.as_view()),
]