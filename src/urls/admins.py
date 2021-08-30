#Django lib
from django.urls import path

#Internal libs
from views.admins import (
    ShowUsers,
    ChangeRole,
    BanUser,
    ChangePlan,
    DeleteIdea,
    ChangeHideness,
    ShowAllIdeas,
    ShowAllTickets,
    SendText,
    EndTicket,
    SendBanWarn,
    SendNotif,
    SendNotif2All,
    SendNotif2Premiums,
    SendNotif2Pros,
    CreateSymbol,
    UpdateTetherToman,
)

urlpatterns = [
    path("show_users",ShowUsers.as_view()),
    path("change_role",ChangePlan.as_view()),
    path("ban_user",BanUser.as_view()),
    path("change_plan",ChangePlan.as_view()),
    path("delete_idea",DeleteIdea.as_view()),
    path("change_hidness",ChangeHideness.as_view()),
    path("show_all_ideas",ShowAllIdeas.as_view()),
    path("show_all_tickets",ShowAllTickets.as_view()),
    path("send_text",SendText.as_view()),
    path("end_ticket",EndTicket.as_view()),
    path("send_ban_warn",SendBanWarn.as_view()),
    path("send_notif",SendNotif.as_view()),
    path("send_notif_2_all", SendNotif2All.as_view()),
    path("send_notif_2_premiums",SendNotif2Premiums.as_view()),
    path("send_notif_2_pros",SendNotif2Pros.as_view()),
    path("create_symbol",CreateSymbol.as_view()),
    path("update_tether_toman_price",UpdateTetherToman.as_view()),
]