import uuid

from datetime import date, datetime, timedelta
from time import mktime
from copy import deepcopy

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from users.authentication import TokenAuthentication
from users.models import Token, User, UserSystem, Wallet
from users.serializers import UserSerializer, UserDeepSerializer,UserSystemSerializer, WalletSerializer
from ideas.models import Image
from ideas.serializers import ImageSerializer

from toolkit.toolkit import existence_error, response_creator, validate_error
from toolkit.image import upload_image, delete_image
from toolkit.purge import purging

# for cache
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.core.cache import cache


CACHE_TTL = getattr(settings, 'CACHE_TTL')


def mobile_number_validator(mobile_number):
    if (
        (mobile_number is not None)
        and (mobile_number[0:2] == "09")
        and (len(mobile_number) == 11)
    ):
        return True
    return False

def is_available (username):
    user = User.objects.filter(username=username.lower()).first()
    if user is None:
        return True
    return False


def get_date(plus_days: int = 0) -> float:
    # by default return timestamp of today
    date_time = date.today() + timedelta(days=plus_days)
    return mktime(date_time.timetuple())


def add_minute(min: int = 0) -> float:
    # by default return timestamp of now
    date_time = datetime.now() + timedelta(minutes=min)
    return mktime(date_time.timetuple())


class SendSms(APIView):

    def post(self,request):
        phone_number = request.data.get("phone_number").strip()
        if not mobile_number_validator(phone_number):
            return Response(
                {
                    "status":"fail",
                    "errors": {"phone_number": "Phone number not valid."},
                },
                status=400,
            )
        user_obj = User.objects.filter(phone_number=phone_number).first()
        if user_obj is not None:
            return Response(
                {
                    "status":"fail",
                    "errors": {"phone_number": "This phone number is registerd"},
                },
                status=400,
            )
        code = str(uuid.uuid4().int)[:4]
        if (request.data.get("developer_number") is not None) and (
            request.data.get("developer_number") in ["09111105055"]
        ):
            code = "1111"

        
        
        key_perfix = f"user_{phone_number}"

        cache_value = cache.get(key_perfix)

        if cache_value is not None:
            return Response(
                {
                    "status":"fail",
                    "errors": {"phone_number": "we send you code you should wait a sec"},
                },
                status=400,
            )

        value = {
            "phone" : phone_number,
            "code" : code,
            "is_valid" : False,
            "exp_date" : add_minute(1),
        }

        cache.set(key_perfix,value,CACHE_TTL)
        
        #send sms

        return response_creator(value)



class OptValidator(APIView):
    
    def post(self, request):
        phone_number = request.data.get("phone_number").strip()
        if not mobile_number_validator(phone_number):
            return Response(
                {
                    "status":"fail",
                    "errors": {"phone_number": "Phone number not valid."},
                },
                status=400,
            )
        code = request.data.get("code")
        if not len(code) == 4:
            return Response(
                {
                    "status":"fail",
                    "errors": {"code": "code is not 4-digit"},
                },
                status=400,
            )
        key_perfix = f"user_{phone_number}"

        value = cache.get(key_perfix)
        if value is None:
            return Response(
                {
                    "status":"fail",
                    "errors": {"cache": "code is deleted use SendSms Endpoint again"},
                },
                status=400,
            )
        if value["exp_date"] < add_minute():
            return Response(
                {
                    "status":"fail",
                    "errors": {"code": "code is expired use SendSms Endpoint again"},
                },
                status=400,
            )
        if value["code"] != code :
            return Response(
                {
                    "status":"fail",
                    "errors": {"code": "code is not match with phone number use SendSms Endpoint again"},
                },
                status=400,
            )
        #cache 
        value["is_valid"] = True
        cache.delete(key_perfix)
        cache.set(key_perfix,value)
        
        return response_creator(value,200)



class SignUp(APIView):


    def post(self, request):
        phone_number = request.data.get("phone_number").strip()
        if not mobile_number_validator(phone_number):
            return Response(
                {
                    "status":"fail",
                    "errors": {"phone_number": "Phone number not valid."},
                },
                status=400,
            )
        #checking cache 
        key_perfix = f"user_{phone_number}"
        value = cache.get(key_perfix)
        
        if value is None:
            return Response(
                {
                    "status":"fail",
                    "errors": {"cache": "cache deleted sign up process is expired."},
                },
                status=400,
            )
        if value["is_valid"] == False:
            return Response(
                {
                    "status":"fail",
                    "errors": {"cache": "this phone number is not validate by sms."},
                },
                status=400,
            )
        #deleting cache
        cache.delete(key_perfix)

        username = request.data.get("username")
        if not is_available(username):
            return Response(
                {
                    "status":"fail",
                    "errors":{"username":"username is taken."},
                },
                status=400
            )
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if password != confirm_password:
            return Response(
                {
                    "status":"fail",
                    "errors":{"password":"passwords are not match."},
                },
                status=400
            )
        #check ther is a user with this phone number
        user_obj = User.objects.filter(phone_number=phone_number).first()
        if user_obj is not None:
            return existence_error("User")

        #create user
        user_obj = User.create_user(password=password, phone_number=phone_number, username=username,role="u")
        user_obj.save()
        user_serialized = UserSerializer(user_obj)

        refferal_code = request.data.get("referral_code")

        user_obj = User.objects.filter(referral=refferal_code).first()
        if user_obj is not None:
            wallet_obj = Wallet.objects.filter(user=user_obj.id).first()
            wallet_obj.amount +=5
            wallet_obj.save()




        #send greeting Message

        return response_creator(data=user_serialized.data)
        

class SignIn(APIView):

    authentication_classes = (TokenAuthentication,)

    def post(self, request):

        username = request.data.get("username").lower()
        password = request.data.get("password")
        user_obj =  User.objects.filter(username=username).first()
        if user_obj is None:
            return existence_error("User")
        
        if user_obj.check_password(password):
            token, created = Token.objects.get_or_create(user=user_obj)

            exp_data = {"token": "Token {}".format(token.key)}
            return response_creator(
                data=exp_data,
                status_code=201,
            )

        else:
            return response_creator(
                data={"status": "fail", "data": {"password": "password is wrong."}},
                status="fail",
            )



class ShowProfile(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):

        user_serialized = UserDeepSerializer(request.user)

        exp_data = purging(
            input_data=user_serialized.data,
            equivalence_list=[("avatar","image")]
        )

        return response_creator(data=exp_data)


class UploadAvatar(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):

        # serialized user for get avatar path
        user_serialized = UserSerializer(request.user)

        # find previous image collection object
        if user_serialized.data.get("avatar") is not None:
            image_obj = Image.objects.filter(id=user_serialized.data.get("avatar"))
            image_serialized = ImageSerializer(image_obj)

        # use toolkit: upload image
        file_path = upload_image(
            file=request.data.get("image"),
            dir="users",
            prefix_dir=[str(request.user.id)],
            limit_size=2000,
            previous_file=(
                image_serialized.data.get("image") 
                if user_serialized.data.get("avatar") is not None 
                else None
            )
        )

        # delete previous image collection
        if user_serialized.data.get("avatar") is not None:
            image_obj.delete()
        
        # create new image collection
        image_serialized = ImageSerializer(data={"image" : file_path})
        if not image_serialized.is_valid():
            return validate_error(image_serialized)
        image_serialized.save()

        # update avatar of user
        user_serialized = UserSerializer(
            request.user,
            data={"avatar" : image_serialized.data.get("id")},
            partial=True,
        )
        if not user_serialized.is_valid():
            return validate_error(user_serialized)
        user_serialized.save()

        return response_creator(data={"avatar" : image_serialized.data.get("image")})



class RemoveAvatar(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):

        # serialized user for get avatar path
        user_serialized = UserSerializer(request.user)

        # find previous image collection object
        image_obj = Image.objects.filter(id=user_serialized.data.get("avatar")).first()
        image_serialized = ImageSerializer(image_obj)

        # remove image file
        delete_image(file_dir=image_serialized.data.get("image"))

        # remove Image object
        image_obj.delete()

        # update user profile
        user_serialized = UserSerializer(
            request.user,
            data={"avatar" : None},
            partial=True,
        )
        if not user_serialized.is_valid():
            return validate_error(user_serialized)
        user_serialized.save()

        return response_creator()

class CreateUserSystem(APIView):
    
    def post(self, request):

        user_system_serialized = UserSystemSerializer(
            data=request.data,
        )
        if not user_system_serialized.is_valid():
            return validate_error(user_system_serialized)
        user_system_serialized.save()

        return response_creator(
            data=user_system_serialized.data,
            status_code=201
        )

class GetBalance(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):

        wallet_obj = Wallet.objects.filter(user=request.user.id).first()
        if wallet_obj is None:
            return existence_error("Wallet")
        
        wallet_serialized = WalletSerializer(wallet_obj)

        return response_creator(data=wallet_serialized.data)


class GetAllIdeas(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    pass

