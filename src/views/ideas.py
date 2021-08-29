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
import repositories as repo

#VARIABELS
PAGE_CAPACITY = 20


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

        idea_serialized, err = repo.ideas.create_idea_object(data=data)

        if err is not None:
            return err

        return response_creator(
            data=idea_serialized,
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

        idea_serialized, err = repo.ideas.create_idea_object(data=data)

        if err is not None:
            return err

        return response_creator(
            data=idea_serialized,
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
        idea_obj, err = repo.ideas.get_idea_object_by_id(idea_id)

        if err is not None:
            return err
        
        idea_serialized = IdeaSerializer(idea_obj)

        create_date = idea_serialized.data.get("create_date")

        exp_date = get_7_days_later(create_date)

        if ((exp_date - create_date) > 604800.0):
            return response_creator(
                data={"error":"you can't delete an idea after 7 days"},
                status="fail",
                status_code=400
            )

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
        page_number = request.data.get("page_number", 0)
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)

        if err is not None:
            return err
        
        user_serialized = repo.users.get_user_data_by_obj(user_obj)
        
        tag_id = request.data.get("tag_id")
        
        tag_obj = Tag.objects.filter(id=tag_id).first()
        if tag_obj is None:
            return existence_error("Tag")

        if user_serialized.get("plan") is None:
            idea_objs = Idea.objects.filter(idea_type="2",tags__icontains=tag_id,is_hide=False)[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
            
        else:
            idea_objs = Idea.objects.filter(tags__icontains=tag_id,is_hide=False)[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
        

        ideas_serialized = IdeaSerializer(idea_objs,many=True)

        return response_creator(data={"ideas":ideas_serialized.data})


class SearchBySymbol(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        page_number = request.data.get("page_number", 0)
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)

        if err is not None:
            return err
        
        user_serialized = repo.users.get_user_data_by_obj(user_obj)

        symbol_id = request.data.get("symbol_id")

        symbol_obj = Symbol.objects.filter(id=symbol_id).first()
        if symbol_obj is None:
            return existence_error("Symbol")

        if user_serialized.get("plan") is None:
            idea_objs = Idea.objects.filter(idea_type="2",symbol=symbol_id,is_hide=False)[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
            
        else:
            idea_objs = Idea.objects.filter(symbol=symbol_id,is_hide=False)[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
        

        ideas_serialized = IdeaSerializer(idea_objs,many=True)

        return response_creator(data={"ideas":ideas_serialized.data})
    


class SubmitRate(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        idea_id = request.data.get("idea_id")
        rate = request.data.get("rate")

        idea_obj, err = repo.ideas.get_idea_object_by_id(idea_id)
        if err is not None:
            return err
        
        idea_serialized = repo.ideas.get_idea_data_by_obj(idea_obj)

        mid_rate = idea_serialized.get("rate")
        rate_list = idea_serialized.get("rate_list")
        rate_objs = Rate.objects.filter(id__in=rate_list)


        for r_obj in rate_objs:
            r_serialized = RateSerializer(r_obj)

            if request.user.id == r_serialized.data.get("user"):
                sum_rate = mid_rate * len(rate_list) - r_serialized.data.get("rate")
                r_serialized, err = repo.ideas.update_rate(r_obj, {"rate":rate})

                if err is not None:
                    return err
                
                mid_rate = (sum_rate + rate) / len(rate_list)

                idea_serialized, err = repo.ideas.update_idea(
                    idea_obj,
                    data={"rate": mid_rate}
                )

                if err is not None:
                    return err
                
                return response_creator(idea_serialized)

        rate_serialized, err = repo.ideas.create_rate_object(
            data={
                "user":request.user.id,
                "rate":rate,
        })

        if err is not None:
            return err

        rate_list.append(rate_serialized.get("id"))

        mid_rate= ((mid_rate * (len(rate_list)-1) + rate )/len(rate_list))
    
        exp_data = {
            "rate_list":rate_list,
            "rate": mid_rate,
        }

        idea_serialized, err= repo.ideas.update_idea(idea_obj, exp_data)

        if err is not None:
            return err

        return response_creator(data=ideas_serialized)

class GetAllIdea(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        page_number = request.GET.get("page_number", 0)
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err
        
        user_serialized = repo.users.get_user_data_by_obj(user_obj)

        user_id = request.GET.get("user_id")

        if user_serialized.get("plan") is None:
            idea_objs = Idea.objects.filter(idea_type="2", user=user_id)[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]

        else:
            idea_objs = Idea.objects.filter(user=user_id)[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]

        ideas_serialized = IdeaSerializer(idea_objs, many=True)

        return response_creator(data={"ideas":ideas_serialized.data})



class ShowIdea(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        def get_2_mins_later(timestamp: float) -> float:
            dt_obj = datetime.fromtimestamp(timestamp)
            dt_obj = dt_obj + timedelta(minutes=2)
            t = datetime.timestamp(dt_obj)
            return t
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err
        
        user_serialized = repo.users.get_user_data_by_obj(user_obj)
    
        idea_id = request.GET.get("idea_id")

        idea_obj, err = repo.ideas.get_idea_object_by_id(idea_id)
        if err is not None:
            return err

        if user_serialized.get("plan") is None and \
            idea_serialized.get("idea_type") == "1":
            return response_creator(
                data={"error":"permission denid."},
                status="fail",
                status_code=403
            )
        
        if idea_serialized.get("is_hide") == True:
            return response_creator(
                data={"error":"data is not accessible"},
                status="fail",
                status_code=400
            )
        views = idea_serialized.get("views")

        query = Q()
        query &= Q(user=request.user.id)
        query &= Q(idea=idea_id)
        query &= Q(ip=request.META.get('REMOTE_ADDR'))

        view_obj, err = repo.ideas.get_view_object_by_query(query)

        if err is None:
            view_serialized = repo.ideas.get_view_data_by_obj(view_obj)
            if datetime.timestamp(datetime.now()) >= get_2_mins_later(view_serialized.get("last_view")):
                views += 1
                view_serialized, err = repo.ideas.update_view(
                    view_obj,
                    data={
                        "last_view": datetime.timestamp(datetime.now()),
                    })
                if err is not None:
                    return err
        else:
            view_serialized, err = repo.ideas.create_view_object(
                data={
                    "user":request.user.id,
                    "idea":idea_id,
                    "ip":request.META.get('REMOTE_ADDR'),
                    "last_view":atetime.timestamp(datetime.now()),
                }
            )
            if err is not None:
                return err
            views += 1

        idea_serialized, err = repo.ideas.update_idea(
            idea_obj,
            data={
                "views":views,
            })
        if err is not None:
            return err
        return response_creator(data=idea_serialzied)

class FeedIdeas(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        page_number = request.GET.get("page_number", 0)
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err
        
        user_serialized = repo.users.get_user_data_by_obj(user_obj)

        following_list = user_serialized.get("followings")
        if user_serialized.get("plan") is None:
            idea_objs = Idea.objects.filter(idea_type="2",user__in=following_list,is_hide=False).order_by('create_date')[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
        else:
            idea_objs = Idea.objects.filter(user__in=following_list,is_hide=False).order_by('create_date')[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]


class NewestIdeas(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        page_number = request.GET.get("page_number", 0)
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err
        
        user_serialized = repo.users.get_user_data_by_obj(user_obj)
        if user_serialized.get("plan") is None:
            idea_objs = Idea.objects.filter(idea_type="2",is_hide=False).order_by('create_date')[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
        else:
            idea_objs = Idea.objects.filter(is_hide=False).order_by('create_date')[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]

        ideas_serialized = IdeaSerializer(idea_objs,many=True)

        return response_creator(data={"ideas":ideas_serialized.data})

class ChangeEditorsPick(APIView):
    permission_classes = (permissions.IsAuthenticated, IsEditor, IsSuperUser, )
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        idea_id = request.data.get("idea_id")
        pick = request.data.get("pick")

        idea_obj, err = repo.ideas.get_idea_object_by_id(idea_id)
        if err is not None:
            return err
        
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
        
        idea_serialized, err = repo.ideas.update_idea(idea_obj, data=data)
        if err is not None:
            return err

        return response_creator(data=ideas_serialized)

class GetEditorsPickIdeas(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        page_number = request.GET.get("page_number", 0)
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err
        
        user_serialized = repo.users.get_user_data_by_obj(user_obj)
        if user_serialized.get("plan") is None:
            ideas_objs = Idea.objects.filter(is_editor_pick=True,idea_type="2",is_hide=False).order_by('pick_date')[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
        else:
            ideas_objs = Idea.objects.filter(is_editor_pick=True,is_hide=False).order_by('pick_date')[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]


        ideas_serialzied = IdeaSerializer(ideas_objs,many=True)

        return response_creator(data={"ideas":ideas_serialzied.data})


class GetTopIdeas(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        page_number = request.GET.get("page_number", 0)
        user_obj, err = repo.users.get_user_object_by_id(request.user.id)
        if err is not None:
            return err
        
        user_serialized = repo.users.get_user_data_by_obj(user_obj)
        if user_serialized.get("plan") is None:
            idea_objs = Idea.objects.filter(idea_type="2",is_hide=False).order_by('views')[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
        else:
            idea_objs = Idea.objects.filter(is_hide=False).order_by('views')[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]
        
        ideas_serialzied = IdeaSerializer(idea_objs,many=True)

        return response_creator(data={"ideas":ideas_serialzied.data})


class SaveScreenshot(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self,request):
        data = deepcopy(request.data)

        data["user"]=request.user.id

        screenshot_serialized, err = repo.ideas.create_screenshot_obj(data)
        if err is not None:
            return err

        return response_creator(data=screenshot_serialized,status_code=201)

class ShowScreenshot(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        screenshot_id = int(request.GET.get("screenshot_id"))

        screenshot_obj, err = repo.ideas.get_screenshot_object_by_id(screenshot_id)
        if err is not None:
            return err
        screenshot_serialized = repo.ideas.get_screenshot_data_by_object(screenshot_obj)

        return response_creator(data=screenshot_serialized)

class DeleteScreenshot(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def delete(self, request):
        screenshot_id = int(request.data.get("screenshot_id"))

        screenshot_obj, err = repo.ideas.get_screenshot_object_by_id(screenshot_id)
        if err is not None:
            return err
        screenshot_serialized = repo.ideas.get_screenshot_data_by_object(screenshot_obj)


        if screenshot_serialized.get("user") != request.user.id:
            return response_creator(
                data={"error":"Permission denied"},
                status="error",
                status_code=403
                )
        delete_image(file_dir=screenshot_serialized.get("screenshot"))

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
