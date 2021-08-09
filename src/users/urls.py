from django.urls import path

from users.views import (
    SendSms,
    ShowProfile,
    SignIn,
    SignUp,
    UploadAvatar,
    RemoveAvatar,
    CreateUserSystem,
    OptValidator,
    GetBalance,
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
]