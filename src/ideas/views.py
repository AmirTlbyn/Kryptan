from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from toolkit.toolkit import existence_error, response_creator, validate_error
from toolkit.image import upload_image, delete_image

from users.permissions import IsPremium,IsPro



class CreatePublicIdea(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPro,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        pass

class CreatePrivateIdea(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPremium,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        pass

class DeleteIdea(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def delete(self,request):
        pass

class Search(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self,request):
        pass

class Sort(APIView):
    permission_classes = (permissions.IsAuthenticated, IsPro,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        pass