#Django libs
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer

#Internal lib
from apps.users.models import (
    User,
    UserSystem,
    Plan,
    Wallet,
)

class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("username"))
    password = serializers.CharField(
        label=_("Password"), style={"input_type": "password"}
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                # From Django 1.10 onwards the `authenticate` call simply
                # returns `None` for is_active=False users.
                # (Assuming the default `ModelBackend` authentication backend.)
                if not user.is_active:
                    msg = _("User account is disabled.")
                    raise serializers.ValidationError(msg)
            else:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg)

        attrs["user"] = user
        return attrs

class UserMiniSerializer(DocumentSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
        ]


class UserSerializer(DocumentSerializer):
    class Meta:
        model = User
        fields =[
            "id",
            "phone_number",
            "username",
            "name",
            "email",
            "is_email_validate",
            "lastname",
            "biography",
            "role",
            "followings",
            "followers",
            "device_token",
            "followings_cnt",
            "followers_cnt",
            "watchlist",
            "avatar",
            "referral",
            "invited_by",
            "first_buy",
            "is_active",
        ]
        depth = 0

    def create(self, validated_data):

        user = User.create_user(
            password=validated_data.get("password"),
            phone_number=validated_data.get("phone_number"),
            username=validated_data.get("username"),
        )
        user.save()
        return user

class UserDeepSerializer(DocumentSerializer):
    followings = UserMiniSerializer(many=True)
    followers = UserMiniSerializer(many=True)
    invited_by = UserMiniSerializer()
    class Meta:
        model = User
        fields =[
            "id",
            "phone_number",
            "username",
            "name",
            "email",
            "is_email_validate",
            "lastname",
            "biography",
            "role",
            "followings",
            "followers",
            "followings_cnt",
            "followers_cnt",
            "watchlist",
            "avatar",
            "referral",
            "invited_by",
            "first_buy",
            "is_active",
        ]
        depth = 1 

class UserSystemSerializer(DocumentSerializer):

    class Meta:
        model = UserSystem
        fields = "__all__"
        depth = 0

class PlanSerializer(DocumentSerializer):
    
    class Meta:
        model = Plan
        fields = "__all__"
        depth = 0

class WalletSerializer(DocumentSerializer):

    class Meta:
        model = Wallet
        fields = "__all__"
        depth = 0

class AdminUserSerializer(DocumentSerializer):
    class Meta:
        model = User 
        fields = [
            "id",
            "phone_number",
            "username",
            "name",
            "email",
            "is_email_validate",
            "lastname",
            "biography",
            "role",
            "is_staff",
            "is_superuser",
            "followings_cnt",
            "followers_cnt",
            "watchlist",
            "referral",
            "invited_by",
            "first_buy",
            "is_active",
            "plan",
        ]
        depth = 0

class AdminUserDeepSerializer(DocumentSerializer):
    invited_by = UserMiniSerializer()
    
    class Meta:
        model=User 
        fields = [
            "id",
            "phone_number",
            "username",
            "name",
            "email",
            "is_email_validate",
            "lastname",
            "biography",
            "role",
            "is_staff",
            "is_superuser",
            "followings_cnt",
            "followers_cnt",
            "watchlist",
            "referral",
            "invited_by",
            "first_buy",
            "is_active",
            "plan",
        ]
        depth = 1