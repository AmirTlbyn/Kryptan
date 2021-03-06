#Django lib
from django.urls import path

#Internal libs
from views.users import (
    SendSms,
    ShowProfile,
    SignIn,
    SignUp,
    UploadAvatar,
    RemoveAvatar,
    CreateUserSystem,
    OptValidator,
    GetBalance,
    Follow,
    Unfollow,
    UpdateProfile,
    ChangePassword,
    ForgetPassword,
    GetAllMessages,
    SendConfimEmail,
    ConfirmEmail,
    GetWatchlist,
    Search,
    GetTetherToman,
)

urlpatterns = [
    path("send_sms",SendSms.as_view()),
    path("show_profile",ShowProfile.as_view()),
    path("sign_in",SignIn.as_view()),
    path("sign_up",SignUp.as_view()),
    path("upload_avatar",UploadAvatar.as_view()),
    path("remove_avatar",RemoveAvatar.as_view()),
    path("create_usersystem",CreateUserSystem.as_view()),
    path("optvalidator",OptValidator.as_view()),
    path("get_balance",GetBalance.as_view()),
    path("follow",Follow.as_view()),
    path("unfollow",Unfollow.as_view()),
    path("update_profile",UpdateProfile.as_view()),
    path("change_password",ChangePassword.as_view()),
    path("forget_password",ForgetPassword.as_view()),
    path("get_messages",GetAllMessages.as_view()),
    path("send_confirm_email",SendConfimEmail.as_view()),
    path("confirm_email",ConfirmEmail.as_view()),
    path("get_watchlist",GetWatchlist.as_view()),
    path("search",Search.as_view()),
    path("get_tether_toman_price",GetTetherToman.as_view()),
]