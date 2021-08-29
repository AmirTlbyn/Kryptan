#Django libs
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.core.cache import cache

#Python libs
import uuid
import re
from datetime import date, datetime, timedelta
from time import mktime
from copy import deepcopy

#Internal libs
from apps.users.authentication import TokenAuthentication
from apps.users.models import Token, User, UserSystem, Wallet
from apps.users.serializers import UserSerializer, UserDeepSerializer,UserSystemSerializer, WalletSerializer, UserMiniSerializer
from apps.ideas.models import Image,Idea
from apps.ideas.serializers import ImageSerializer,IdeaDeepSerializer,IdeaTwoDeepSerializer
from repositories.permissions import IsPro
from apps.directs.models import Message,MessageBox, AutomaticMessage
from apps.directs.serializers import MessageBoxSerializer,MessageSerializer, AutomaticMessageSerializer
from toolkit.toolkit import existence_error, response_creator, validate_error
from toolkit.image import upload_image, delete_image
from toolkit.purge import purging
import repositories as repo


#CACHE VARIABLE
CACHE_TTL = getattr(settings, 'CACHE_TTL')


class SendSms(APIView):

    def post(self,request):
        phone_number = request.data.get("phone_number").strip()
        forget = request.data.get("forget")

        if not repo.users.mobile_number_validator(phone_number):
            return response_creator(
                data={
                    "errors":"phone number is not valid.",
                },
                status="fail",
                status_code=400,
            )
        user_obj = User.objects.filter(phone_number=phone_number).first()


        if (forget is None) or (forget is False):
            if err is not None:
                return response_creator(
                    data={
                        "errors":"This phone number is registerd",
                    },
                    status="fail",
                    status_code=400,
                )
        
        else:
            if err is None:
                return response_creator(
                    data={
                        "errors":"This phone number is not registerd",
                    },
                    status="fail",
                    status_code=400,
                )
            

        code = str(uuid.uuid4().int)[:4]
        if (request.data.get("developer_number") is not None) and (
            request.data.get("developer_number") in ["09111105055"]
        ):
            code = "1111"

        
        
        key_perfix = f"user_{phone_number}"

        cache_value = cache.get(key_perfix)

        if cache_value is not None:
            return response_creator(
                    data={
                        "errors":"we send you code you should wait a sec",
                    },
                    status="fail",
                    status_code=400,
                )

        value = {
            "phone" : phone_number,
            "code" : code,
            "is_valid" : False,
            "exp_date" : repo.users.add_minute(1),
        }

        cache.set(key_perfix,value,CACHE_TTL)
        
        #send sms

        return response_creator(value)



class OptValidator(APIView):
    
    def post(self, request):
        phone_number = request.data.get("phone_number").strip()
        if not repo.users.mobile_number_validator(phone_number):
            return response_creator(
                data={
                    "errors":"phone number is not valid.",
                },
                status="fail",
                status_code=400,
            )
        code = request.data.get("code")
        if not len(code) == 4:
            return response_creator(
                data={
                    "errors":"code is not 4-digit",
                },
                status="fail",
                status_code=400,
            )

        key_perfix = f"user_{phone_number}"
        
        value = cache.get(key_perfix)
        if value is None:
            return response_creator(
                data={
                    "cache": "code is deleted use SendSms Endpoint again",
                },
                status="fail",
                status_code=400,
            )
        
        if value["exp_date"] < repo.users.add_minute():
            return response_creator(
                data={
                    "errors":"code is expired use SendSms Endpoint again",
                },
                status="fail",
                status_code=400,
            )
        if value["code"] != code :
                    
            return response_creator(
                data={
                    "errors":"code is not match with phone number use SendSms Endpoint again",
                },
                status="fail",
                status_code=400,
            )
        #cache 
        value["is_valid"] = True
        cache.delete(key_perfix)
        cache.set(key_perfix,value)
        
        return response_creator(data=value,status_code=200)



class SignUp(APIView):


    def post(self, request):

        phone_number = request.data.get("phone_number").strip()
        if not repo.users.mobile_number_validator(phone_number):
            return response_creator(
                data={
                    "errors":"phone number is not valid.",
                },
                status="fail",
                status_code=400,
            )
        #checking cache 
        key_perfix = f"user_{phone_number}"
        value = cache.get(key_perfix)
        
        if value is None:
            return response_creator(
                data={
                    "errors": "cache deleted sign up process is expired.",
                },
                status="fail",
                status_code=400,
            )
    
        if value["is_valid"] == False:
            return response_creator(
                data={
                    "errors": "this phone number is not validate by sms.",
                },
                status="fail",
                status_code=400,
            )
        
        username = request.data.get("username")

        if not repo.users.username_validator(username):
            return response_creator(
                data={"error":"username only can have lower case alphabetic and number and underscore"},
                status="fail",
                status_code=400
                )
        
        if not repo.users.is_available(username):
            return response_creator(
                data={"error":"username is taken."},
                status="fail",
                status_code=400
            )
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if password != confirm_password:
            return response_creator(
                data={"error":"passwords are not match"},
                status="fail",
                status_code=400
            )
        #check ther is a user with this phone number
        user_obj, err = repo.users.get_user_object_by_phone_number(phone_number=phone_number)
        if err is not None:
            return response_creator(
                data={"error":"this phone number is registerd"},
                status="fail",
                status_code=400
            )

        refferal_code = request.data.get("referral_code")
        inviter_obj = User.objects.filter(referral=refferal_code).first()

        #create user
        user_obj = User.create_user(password=password, phone_number=phone_number, username=username,role="u", invited_by=inviter_obj)
        user_obj.save()
        user_serialized = UserSerializer(user_obj)


        #Deleting cache 
        cache.delete(key_perfix)

        #referral transaction
        if inviter_obj is not None:
            wallet_obj = Wallet.objects.filter(user=inviter_obj.id).first()
            wallet_obj.amount +=5
            wallet_obj.save()

        #send greeting message
        repo.auto_msg.send_message(user_serialized=user_serialized,greeting_bool=True)

        return response_creator(data=user_serialized.data)
        

class SignIn(APIView):

    authentication_classes = (TokenAuthentication,)

    def post(self, request):

        username = request.data.get("username")
        if not repo.users.username_validator(username):
            return response_creator(
                data={"error":"username only can have lower case alphabetic and number and underscore"},
                status="fail",
                status_code=400
            )
        password = request.data.get("password")
        user_obj, err =  repo.users.get_user_object_by_username(username)
        if err is not None:
            return err
        
        if user_obj.is_active() is False:
            return response_creator(
                data={
                    "error":"user is ban"
                },
                status_code=400,
                status="fail"
            )
        
        if user_obj.check_password(password):
            token, created = Token.objects.get_or_create(user=user_obj)

            exp_data = {"token": "Token {}".format(token.key)}
            return response_creator(
                data=exp_data,
                status_code=201,
            )

        else:
            return response_creator(
                data={"errors": "password is wrong."},
                status="fail",
                status_code = 400
            )



class ShowProfile(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):

        user_id = request.GET.get("user_id")

        user_obj, err = repo.users.get_user_object_by_id(user_id)
        if err is not None:
            return err

        user_serialized = UserDeepSerializer(user_obj)

        exp_data = purging(
            input_data=user_serialized.data,
            equivalence_list=[("avatar","image")],
        )

        return response_creator(data=exp_data)


class UploadAvatar(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):

        # serialized user for get avatar path
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err

        user_serialized = repo.users.get_user_data_by_obj(user_obj)

        # find previous image collection object
        if user_serialized.get("avatar") is not None:
            image_obj = Image.objects.filter(id=user_serialized.get("avatar"))
            image_serialized = ImageSerializer(image_obj)

        # use toolkit: upload image
        file_path = upload_image(
            file=request.data.get("image"),
            dir="users",
            prefix_dir=[str(request.user.id)],
            limit_size=2000,
            previous_file=(
                image_serialized.data.get("image") 
                if user_serialized.get("avatar") is not None 
                else None
            )
        )

        # delete previous image collection
        if user_serialized.get("avatar") is not None:
            image_obj.delete()
        
        # create new image collection
        image_serialized = ImageSerializer(data={"image" : file_path})
        if not image_serialized.is_valid():
            return validate_error(image_serialized)
        image_serialized.save()

        # update avatar of user
        user_serialized, err = repo.users.update_user(
            user_obj,
            data={"avatar" : image_serialized.data.get("id")})
        if err is not None:
            return err

        return response_creator(data={"avatar" : image_serialized.data.get("image")})



class RemoveAvatar(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):

        # serialized user for get avatar path
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err

        user_serialized = repo.users.get_user_data_by_obj(user_obj)

        # find previous image collection object
        image_obj = Image.objects.filter(id=user_serialized.data.get("avatar")).first()
        image_serialized = ImageSerializer(image_obj)

        # remove image file
        delete_image(file_dir=image_serialized.data.get("image"))

        # remove Image object
        image_obj.delete()

        # update user profile
        user_serialized, err = repo.users.update_user(
            user_obj,
            data={"avatar" : None})
        if err is not None:
            return err

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


class Follow(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        """
            if user a want to follow user b

            a -> following 
            b -> followier

        """

        follower_id = request.data.get("user_id")

        #check id of folower id to not follow him/her self
        if int(follower_id) == int(request.user.id):
            return response_creator(
                data={"error":"you can't follow urself"},
                status_code=400,
                status="fail"
            )
        
        following_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err

        follower_obj, err = repo.users.get_user_object_by_id(follower_id)
        if err is not None:
            return err

        
        follower_serialized = repo.users.get_user_data_by_obj(follower_obj)
        following_serialized = repo.users.get_user_data_by_obj(following_obj)

        #adding to follwer list
        followers_list = follower_serialized.get("followers")

        if following_serialized.get("id") in followers_list:
            return response_creator(
                data={"error":"user is followed"},
                status_code=400,
                status="fail"
            )
        followers_list.append(following_serialized.get("id"))

        #adding to follower_cnt

        followers_cnt = int(follower_serialized.get("followers_cnt"))
        followers_cnt +=1

        #adding to following list
        followings_list = following_serialized.get("followings")
        followings_list.append(follower_serialized.get("id"))

        #adding to following_cnt

        followings_cnt = int(following_serialized.get("followings_cnt"))
        followings_cnt +=1

        follower_serialized, err = repo.users.update_user(
            follower_obj,
            data = {
                "followers" : followers_list,
                "followers_cnt" : followers_cnt,
            })
        if err is not None:
            return err

        following_serialized, err = repo.users.update_user(
            following_obj,
            data = {
                "followings" : followings_list,
                "followings_cnt" : followings_cnt,
            })
        if err is not None:
            return err
        
        return response_creator(
            data = {
                "follower" : follower_serialized.data,
                "following": following_serialized.data},
            status_code=200
        )

#Unfollow
class Unfollow(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        """
            if user a want to unfollow user b
            user a unfollower
            user b unfollowing
        """

        unfollowing_id = request.data.get("user_id")

        unfollower_obj, err = repo.users.get_user_object_by_id(int(request.user.id))
        if err is not None:
            return err

        unfollowing_obj, err = repo.users.get_user_object_by_id(unfollowing_id)
        if err is not None:
            return err

        unfollower_serialized = repo.users.get_user_data_by_obj(unfollower_obj)
        unfollowing_serialized = repo.users.get_user_data_by_obj(unfollowing_obj)

        unfollower_list = unfollower_serialized.get("followings")
        unfollower_cnt = unfollower_serialized.get("followings_cnt")

        unfollowing_list = unfollowing_serialized.get("followers")
        unfollowing_cnt = unfollowing_serialized.get("followers_cnt")

        if (unfollowing_id in unfollower_list) and \
            (request.user.id in unfollowing_list):
            unfollower_list.remove(unfollowing_id)
            unfollower_cnt -= 1
            unfollowing_list.remove(request.user.id)
            unfollowing_cnt -=1

            unfollower_serialized, err = repo.users.update_user(unfollower_obj, data = {
                    "followings" : unfollower_list,
                    "followings_cnt" : unfollower_cnt,}
            )
            if err is not None:
                return err

            unfollowing_serialized, err = repo.users.update_user(unfollowing_obj,data = {
                    "followers" : unfollowing_list,
                    "followers_cnt": unfollowing_cnt,}
            )
            if err is not None:
                return err
        
        return response_creator(data={
            "unfollower" : unfollower_serialized,
            "unfollowing": unfollowing_serialized}
        )

#UpdateProfile

class UpdateProfile(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err
        
        data = deepcopy(request.data)


        if data.get("password") is not None:
            data.pop("password")
        if data.get("phone_number") is not None:
            data.pop("phone_number")
        if data.get("username") is not None:
            data.pop("username")
        if data.get("followings") is not None:
            data.pop("followings")
        if data.get("followers") is not None:
            data.pop("followers")
        if data.get("followings_cnt") is not None:
            data.pop("followings_cnt")
        if data.get("followers_cnt") is not None:
            data.pop("followers_cnt")
        if data.get("plan") is not None:
            data.pop("plan")
        if data.get("referral") is not None:
            data.pop("referral")
        if data.get("invited_by") is not None:
            data.pop("invited_by")
        if data.get("first_buy") is not None:
            data.pop("first_buy")
        if data.get("email") is not None:
            data["is_email_validate"] = False
            
        
        user_serialized, err = repo.users.update_user(
            user_obj,
            data=data
        )
        if err is not None:
            return err

        return response_creator(data = user_serialized)


#change password

class ChangePassword(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):

        old_password = request.data.get("old_password")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if old_password is None or old_password == "":
            return response_creator(
                data={"error":"old password was empty"},
                status_code=400,
                status=fail
                )
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err

        if not user_obj.check_password(old_password):
            return response_creator(
                data={"error":"old password was not right"},
                status=fail,
                status_code=400
                ) 
        if password != confirm_password:
            return response_creator(
                data={"error":"new password and confirm password was not match"},
                status_code=400,
                status=fail,
                )
        user_obj.set_password(password)

        return response_creator(
            data={"succes":"password is changed"},
            status_code = 200
        )


#forgetpassword

class ForgetPassword(APIView):

    def patch(self, request):
        phone_number = request.data.get("phone_number").strip()
        if not repo.users.mobile_number_validator(phone_number):
            return response_creator(
                data={
                    "errors":"phone number is not valid.",
                },
                status="fail",
                status_code=400,
            )
        user_obj , err = repo.users.get_user_object_by_phone_number(phone_number=phone_number)
        if err is not None:
            return err
        
        key_perfix = f"user_{phone_number}"
        value = cache.get(key_perfix)
        
        if value is None:
            return response_creator(
                data={
                    "errors": "cache deleted sign up process is expired.",
                },
                status="fail",
                status_code=400,
            )
        if value["exp_date"] < repo.users.add_minute():
            return response_creator(
                data={
                    "errors":"code is expired use SendSms Endpoint again",
                },
                status="fail",
                status_code=400,
            )
        if value["code"] != code :
                    
            return response_creator(
                data={
                    "errors":"code is not match with phone number use SendSms Endpoint again",
                },
                status="fail",
                status_code=400,
            )
        
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        if password != confirm_password:
            return response_creator(
                data={
                    "errors":"passwords are not match.",
                },
                status="fail",
                status_code=400,
            )
           
        user_obj.set_password(password)
        user_obj.save()

        return response_creator(data={"message":"password changed succesfully"})




class GetAllMessages(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):

        page_number=request.GET.get("page_number", 0)

        message_box_obj, err = repo.directs.get_msgbox_object_by_user(request.user.id)
        if err is not None:
            return err
        
        message_box_serialized = repo.directs.get_msgbox_data_by_obj(message_box_obj)

        am_list = massage_box_serialized.get("automatic_messages")

        automatic_message_objs = AutomaticMessage.objects.filter(id__in = am_list)
        
        for am_obj in automatic_message_objs:
            if not am_obj.is_read:
                am_serialized, err = repo.directs.update_automatic_msg(
                    am_obj,
                    data={"is_read":True}
                )
                if err is not None:
                    return err
               
        
        un_read = massage_box_serialized.get("un_read")
        read = message_box_serialized.get("read")

        read = read+un_read

        un_read = 0

        massage_box_serialized, err = repo.directs.update_msgbox (
            message_box_obj,
            data={"read":read,
                "un_read":un_read,}
        )
        if err is not None:
            return err

        massage_box_serialized = MessageBoxDeepSerializer(message_box_obj)

        return response_creator(data=message_box_serialized.data)

#send confirm EMAIL

class SendConfimEmail(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):

        email = request.data.get("email")

        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err

        user_serialized = repo.users.get_user_data_by_obj(user_obj)

        if email != user_serialized.get("email"):
            return response_creator(
                data={"error":"email is not match with user email"},
                status="fail",
                status_code=400
            )
        if user_serialized.get("is_email_validate") == True:
            return response_creator(
                data={"error":"this email is validate"},
                status="fail",
                status_code = 400
            )
        code = str(uuid.uuid4().int)[:5]
        if (request.data.get("developer_number") is not None) and (
            request.data.get("developer_number") in ["09111105055"]
        ):
            code = "11111"
        
        key_perfix = f"user_{email}"

        cache_value = cache.get(key_perfix)

        if cache_value is not None:
            return response_creator(
                data={
                    "errors":"we send you code you should wait a sec",
                },
                status="fail",
                status_code=400
            )

        value = {
            "phone" : email,
            "code" : code,
            "is_valid" : False,
            "exp_date" : repo.users.add_minute(2),
        }

        cache.set(key_perfix,value,CACHE_TTL)
        
        #send email

        return response_creator(value)


#Confirm Email

class ConfirmEmail(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        user_obj, err = repo.users.get_plan_object_by_id(request.user.id)
        if err is not None:
            return err

        user_serialized = repo.users.get_user_data_by_obj(user_obj)

        if user_serialized.get("email") != email:
            return response_creator(
                data={"error":"email is not match with user email"},
                status="fail",
                status_code=400
            )
        if user_serialized.get("is_email_validate") == True:
            return response_creator(
                data={"error":"this email is validate"},
                status="fail",
                status_code = 400
            )

        key_perfix = f"user_{email}"

        value = cache.get(key_perfix)

        if value is None:
            return response_creator(
                data={
                    "cache": "code is deleted use Send Confirm Email Endpoint again",
                },
                status="fail",
                status_code=400,
            )
        
        if value["exp_date"] < repo.users.add_minute():
            return response_creator(
                data={
                    "errors":"code is expired use Send Confirm Email Endpoint again",
                },
                status="fail",
                status_code=400,
            )
        if value["code"] != code :
                    
            return response_creator(
                data={
                    "errors":"code is not match with username use Send Confirm Email Endpoint again",
                },
                status="fail",
                status_code=400,
            )
        
        is_validate = user_serialized.get("is_email_validate")
        is_validate = True

        exp_data = {
            "is_email_validate":is_validate
        }
        user_serialized, err = repo.users.update_user(user_obj,data = exp_data)
        if err is not None:
            return err

        return response_creator(user_serialized, status_code=200)
        
class GetWatchlist(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err

        user_serialized = repo.users.get_user_data_by_obj(user_obj)

        watchlist = user_serialized.get("watchlist")

        return response_creator(data={"watchlist":watchlist})

class Search(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        username = request.data.get("username")

        user_objs = User.objects.filter(username__icontains = username)

        users_serialized = UserMiniSerializer(user_objs,many=True)

        return response_creator(data=users_serialized.data)
        
        
