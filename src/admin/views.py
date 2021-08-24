from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from toolkit.toolkit import existence_error, response_creator, validate_error

from toolkit.image import upload_image, delete_image
from users.permissions import IsSuperUser
from users.models import (
    User,
    Plan,
)
from users.serializers import(
    UserDeepSerializer,
    UserSerializer,
    AdminUserDeepSerializer,
    AdminUserSerializer,
    PlanSerializer,
)
from ideas.models import(
    Idea,
)

from ideas.serializers import IdeaDeepSerializer, IdeaSerializer

from copy import deepcopy

PAGE_CAPACITY = 50

#USER ADMIN MENU

class ShowUsers(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        order_by = request.data.get("order_by")
        page_number = request.data.get("page_number", 0)

        user_objs = User.objects.all().order_by(order_by)[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]

        users_serialized = AdminUserDeepSerializer(user_objs, many=True)

        return response_creator(data={"users":users_serialized.data})

class ChangeRole(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        user_id = request.data.get("user_id")
        role = request.data.get("role")


        user_obj = User.objects.filter(id = user_id).first()

        if user_obj is None:
            return existence_error("User")

        user_serialized = AdminUserSerializer(
            user_obj,
            data={
                "role":role
            },
            partial=True,
        )
        if not user_serialized.is_valid():
            return validate_error(user_serialized)

        user_serialized.save()

        return response_creator(data = user_serialized.data)

class BanUser(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        user_id = request.data.get("user_id")
        is_active = request.data.get("is_active")

        user_obj = User.objects.filter(id=user_id).first()

        if user_obj is None:
            return existence_error("User")

        user_serialized = AdminUserSerializer(
            user_obj,
            data={"is_active":is_active},
            partial=True,
        )

        if not user_serialized.is_valid():
            return validate_error(user_serialized)

        user_serialized.save()

        return response_creator(data=user_serialized.data)

class ChangePlan(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):

        user_id = request.data.get("user_id")

        plan_version = request.data.get("plan_version")
        expire_date = request.data.get("expire_date")

        user_obj = User.objects.filter(id = user_id).first()

        if user_obj is None:
            return existence_error("User")

        user_serialized = AdminUserSerializer(user_obj)

        plan_id = user_serialized.data.get("plan")

        plan_obj = Plan.objects.filter(id=plan_id).first()

        if plan_obj is None:

            plan_serialized = PlanSerializer(data={
                "plan_version":plan_version,
                "expire_date":expire_date,
            })

            if not plan_serialized.is_valid():
                return validate_error(plan_serialized)
            plan_serialized.save()
            return response_creator(data=plan_serialized.data)

        if plan_version == 0 :
            plan_obj.delete()
            return response_creator()

        plan_serialized = PlanSerializer(
            plan_obj,
            data={
                "plan_version":plan_version,
                "expire_date":expire_date,
            },
            partial=True,
        )

        if not plan_serialized.is_valid():
            return validate_error(plan_serialized)
        plan_serialized.save()

        return response_creator(data=plan_serialized.data)


#IDEA ADMIN MENU

class DeleteIdea(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def delete(self, request):
         
        idea_id = request.data.get("idea_id")
        idea_obj = Idea.objects.filter(id=idea_id).first()        

        if idea_obj is None:
            return existence_error("Idea")
        
        idea_serialized = IdeaSerializer(idea_obj)
        idea_obj.delete()

        return response_creator()

class ChangeHideness(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        idea_id = request.data.get("idea_id")
        is_hide = request.data.get("is_hide")
        idea_obj = Idea.objects.filter(id=idea_id).first()        

        if idea_obj is None:
            return existence_error("Idea")
        
        idea_serialized = IdeaSerializer(
            idea_obj,
            data={
                "is_hide":is_hide,
            },
            partial=True
        )

        if not idea_serialized.is_valid():
            return validate_error(idea_serialized)

        idea_serialized.save()

class ShowAllIdeas(APIView):
    permission_classes = (permissions.IsAuthenticated,IsSuperUser)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        order_by = request.GET.get("order_by")
        page_number = request.GET.get("page_number", 0)
        idea_objs = Idea.objects.all().order_by(order_by)[page_number*PAGE_CAPACITY:(page_number+1)*PAGE_CAPACITY]

        ideas_serialized = IdeaSerializer(idea_objs,many=True)

        return response_creator(data={"ideas":ideas_serialized.data})



#TICKET ADMIN MENU

#SEND NOTIF



