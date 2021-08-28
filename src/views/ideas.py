#Django libs
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from mongoengine.queryset.visitor import Q

#Python libs
from datetime import date, datetime, timedelta
from time import mktime
from copy import deepcopy

#Internal libs
from toolkit.toolkit import existence_error, response_creator, validate_error
from toolkit.image import upload_image, delete_image
from apps.users.authentication import TokenAuthentication
from repositories.permissions import IsPremium,IsPro, IsEditor, IsSuperUser
from apps.users.models import User, Plan
from apps.users.serializers import UserSerializer, PlanSerializer
from apps.ideas.models import Idea, Image, Rate, Screenshot,Tag
from apps.ideas.serializers import (
    IdeaSerializer,
    IdeaDeepSerializer,
    IdeaTwoDeepSerializer,
    ImageSerializer,
    RateSerializer,
    ScreenshotSerializer,
    TagSerializer,
)
from apps.symbols.models import Symbol


class CreatePublicIdea(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPro,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        data = deepcopy(request.data)

        if data.get("idea_type") is not None:
            data.pop("idea_type")
        if data.get("is_editor_pick") is not None:
            data.pop("is_editor_pick")
        if data.get("pick_date") is not None:
            data.pop("pick_date")
        if data.get("views") is not None:
            data.pop("views")
        if data.get("is_hide") is not None:
            data.pop("is_hide")
        data["idea_type"] = "2"

        idea_serialized = IdeaSerializer(data=data)

        if not idea_serialized.is_valid():
            return validate_error(idea_serialized)

        idea_serialized.save()
        return response_creator(
            data=idea_serialized.data,
            status_code=201
            )


class CreatePrivateIdea(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPremium,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        data = deepcopy(request.data)

        if data.get("idea_type") is not None:
            data.pop("idea_type")
        if data.get("is_editor_pick") is not None:
            data.pop("is_editor_pick")
        if data.get("pick_date") is not None:
            data.pop("pick_date")
        if data.get("views") is not None:
            data.pop("views")
        if data.get("is_hide") is not None:
            data.pop("is_hide")

        data["idea_type"] = "1"

        idea_serialized = IdeaSerializer(data=data)

        if not idea_serialized.is_valid():
            return validate_error(idea_serialized)

        idea_serialized.save()
        return response_creator(
            data=idea_serialized.data,
            status_code=201
            )


class DeleteIdea(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def delete(self, request):

        def get_7_days_later(timestamp: float) -> float:
            dt_obj = datetime.fromtimestamp(timestamp)
            dt_obj = dt_obj + timedelta(days=7)
            t = datetime.timestamp(dt_obj)
            return t
        
        idea_id = request.data.get("idea_id")
        idea_obj = Idea.objects.filter(id=idea_id).first()        

        if idea_obj is None:
            return existence_error("Idea")
        
        idea_serialized = IdeaSerializer(idea_obj)

        create_date = idea_serialized.data.get("create_date")

        exp_date = get_7_days_later(create_date)

        if ((exp_date - create_date) > 604800.0):
            return response_creator(data={"error":"you cant delete an idea after 7 days"},status="fail",status_code=400)

        if int(idea_serialized.data.get("user")) != request.user.id:
            return response_creator(
                data={"error":"permission denid."},
                status_code=403
                )
        idea_obj.delete()

        return response_creator()



class SearchByTag(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        user_serialized = UserSerializer(request.user)
        tag_id = request.data.get("tag_id")
        
        tag_obj = Tag.objects.filter(id=tag_id).first()
        if tag_obj is None:
            return existence_error("Tag")

        plan_obj = Plan.objects.filter(id = user_serialized.get("plan")).first()
        
        if plan_obj is None:
            idea_objs = Idea.objects.filter(idea_type="2",tags__icontains=tag_id,is_hide=False)
            
        else:
            idea_objs = Idea.objects.filter(tags__icontains=tag_id,is_hide=False)
        

        ideas_serialized = IdeaSerializer(idea_objs,many=True)

        return response_creator(data=ideas_serialized.data)


class SearchBySymbol(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        user_serialized = UserSerializer(request.user)

        symbol_id = request.data.get("symbol_id")

        symbol_obj = Symbol.objects.filter(id=symbol_id).first()
        if symbol_obj is None:
            return existence_error("Symbol")

        plan_obj = Plan.objects.filter(id = user_serialized.get("plan")).first()

        if plan_obj is None:
            idea_objs = Idea.objects.filter(idea_type="2",symbol=symbol_id,is_hide=False)
            
        else:
            idea_objs = Idea.objects.filter(symbol=symbol_id,is_hide=False)
        

        ideas_serialized = IdeaSerializer(idea_objs,many=True)

        return response_creator(data={"ideas":ideas_serialized.data})
    


class SubmitRate(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        idea_id = request.data.get("id")
        rate = request.data.get("rate")

        idea_obj = Idea.objects.filter(id=idea_id).first()

        if idea_obj is None:
            return existence_error("Idea")
        idea_serialized = IdeaSerializer(idea_obj)

        rate_list = idea_serialized.data.get("rate_list")
        rates_serialized = RateSerializer(rate_list,many=True)

        if request.user.id in rates_serialized.data.get("user"):
            return response_creator(
                data={"error":"you submited your rate before"},
                status="fail",
                status_code=400
                )

        
        rate_obj = Rate.create(user=request.user.id,rate=rate)
        rate_list.append(rate_obj)

        mid_rate = idea_serialized.data.get("rate")
        views = idea_serialized.data.get("views")

        mid_rate= ((mid_rate * (len(rate_list)-1) + rate )/len(rate_list))
        

        exp_data = {
            "views":views+1,
            "rate_list":rate_list,
            "rate": mid_rate
        }
        idea_serialized = IdeaSerializer(idea_obj,data=exp_data,partial=True)

        if not idea_serialized.is_valid():
            return validate_error(idea_serialized)

        idea_serialized.save()

        return response_creator(data=ideas_serialized.data)

class GetAllIdea(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_serialized = UserSerializer(request.user)

        user_id = request.GET.get("user_id")

        plan_obj = Plan.objects.filter(id = user_serialized.get("plan")).first()

        if plan_obj is None:
            idea_objs = Idea.objects.filter(idea_type="2", user=user_id)

        else:
            idea_objs = Idea.objects.filter(user=user_id)

        ideas_serialized = IdeaSerializer(idea_objs, many=True)

        return response_creator(data={"ideas":ideas_serialized.data})



class ShowIdea(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_serialized = UserSerializer(request.user)
        idea_id = request.GET.get("idea_id")

        idea_obj = Idea.objects.filter(id=idea_id,is_hide=False).first()
        if idea_obj is None:
            return existence_error("Idea")
        idea_serialized = IdeaSerializer(idea_obj)

        view_cnt = idea_serialized.data.get("views") + 1

        idea_serialized = IdeaSerializer(
            idea_obj,
            data={
                "views":view_cnt,
            },
            partial=True,
        )

        if not idea_serialized.is_valid():
            return validate_error(idea_serialzied)
        
        idea_serialized.save()

        plan_obj = Plan.objects.filter(id = user_serialized.get("plan")).first()
        if plan_obj in None:
            if idea_serialized.data.get("idea_type") =="2":

                return response_creator(data=idea_serialized.data)
            else:
                return response_creator(
                    data={"error":"you font have permission to acces"},
                    status="error",
                    status_code=403
                    )
        else:
            return response_creator(data=idea_serialzied.data)
        




class FeedIdeas(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_serialized = UserSerializer(request.user)
        following_lsit = user_serialized.data.get("followings")
        plan_obj = Plan.objects.filter(id = user_serialized.get("plan")).first()
        if plan_obj is None:
            idea_objs = Idea.objects.filter(idea_type="2",user__in=following_lsit,is_hide=False).order_by('create_date')
        else:
            idea_objs = Idea.objects.filter(user__in=following_lsit,is_hide=False).order_by('create_date')


class NewestIdeas(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_serialized = UserSerializer(request.user)
        plan_obj = Plan.objects.filter(id = user_serialized.get("plan")).first()
        if plan_obj is None:
            idea_objs = Idea.objects.filter(idea_type="2",is_hide=False).order_by('create_date')
        else:
            idea_objs = Idea.objects.filter(is_hide=False).order_by('create_date')

        ideas_serialized = IdeaSerializer(idea_objs,many=True)

        return response_creator(data={"ideas":ideas_serialized.data})

class ChangeEditorsPick(APIView):
    permission_classes = (permissions.IsAuthenticated, IsEditor, IsSuperUser, )
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        idea_id = request.data.get("idea_id")
        idea_obj = Idea.objects.filter(id = idea_id,is_hide=False).first()

        pick = request.data.get("pick")

        if idea_obj is None: 
            return existence_error("Idea")
        
        if pick == True:
            data = {
                "is_editor_pick":True,
                "pick_date": datetime.timestamp(datetime.now())
            }
        else: 
            data = {
                "is_editor_pick" : False,
                "pick_date": 0
            }
        
        idea_serialized = IdeaSerializer(idea_obj,data=data,partial=True)
        if not idea_serialized.is_valid():
            return validate_error(idea_serialized)

        idea_serialized.save()

        return response_creator(data=ideas_serialized.data)

class GetEditorsPickIdeas(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_serialized = UserSerializer(request.user)

        plan_obj = Plan.objects.filter(id = user_serialized.get("plan")).first()
        if plan_obj is None:
            ideas_objs = Idea.objects.filter(is_editor_pick=True,idea_type="2",is_hide=False).order_by('pick_date')

        ideas_objs = Idea.objects.filter(is_editor_pick=True,is_hide=False).order_by('pick_date')


        ideas_serialzied = IdeaSerializer(ideas_objs,many=True)

        return response_creator(data={"ideas":ideas_serialzied.data})


class GetTopIdeas(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user_serialized = UserSerializer(request.user)

        plan_obj = Plan.objects.filter(id=user_serialized.data.get("plan")).first()
        if plan_obj is None:
            idea_objs = Idea.objects.filter(idea_type="2",is_hide=False).order_by('views') 
        else:
            idea_objs = Idea.objects.filter(is_hide=False).order_by('views')
        
        ideas_serialzied = IdeaSerializer(idea_objs,many=True)

        return response_creator(data=ideas_serialzied.data)


class SaveScreenshot(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self,request):
        data = deepcopy(request.data)

        data["user"]=request.user.id

        file_path = upload_image(
            file=request.data.get("screenshot"),
            dir="screenshots",
            prefix_dir=[str(request.user.id)],
            limit_size=3000,
        )

        data["screenshot"] = file_path

        screenshot_serialized = ScreenshotSerializer(data=data)

        if not screenshot_serialized.is_valid():
            return validate_error(screenshot_serialized)

        screenshot_serialized.save()

        return response_creator(data=screenshot_serialized.data,status_code=201)

class DeleteScreenshot(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def delete(self, request):
        screenshot_id = int(request.data.get("screenshot_id"))
        screenshot_obj = Screenshot.objects.filter(id=screenshot_id).first()

        if screenshot_obj is None:
            return existence_error("Screenshot")

        screenshot_serialized = ScreenshotSerializer(screenshot_obj)


        if screenshot_serialized.data.get("user") != request.user.id:
            return response_creator(
                data={"error":"Permission denied"},
                status="error",
                status_code=403
                )
        delete_image(file_dir=screenshot_serialized.data.get("screenshot"))

        screenshot_obj.delete()

        return response_creator()

class SearchTag(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        text = request.data.get("text")

        tags_obj = Tag.objects.filter(tag__icontains=text)

        tags_serialized = TagSerializer(tags_obj,many=True)

        return response_creator(data=tags_serialized.data)

class CreateTag(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        tag = request.data.get("tag")

        tag_obj = Tag.objects.filter(tag=tag).first()

        if tag_obj is not None:
            return response_creator(
                data={"error":"tag is available"},
                status_code=400,
                status="fail"
                )
        
        tag_serialized = TagSerializer(data={"tag":tag})

        if not tag_serialized.is_valid():
            return validate_error(tag_serialized)

        tag_serialized.save()

        return response_creator(data=tag_serialized.data,status_code=201)
