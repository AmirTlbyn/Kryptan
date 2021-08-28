#Django lib
from rest_framework_mongoengine.serializers import DocumentSerializer

#Internal libs
from apps.users.serializers import UserMiniSerializer
from apps.ideas.models import (
    Image,
    Idea,
    Rate,
    Screenshot,
    Tag,
)

class ImageSerializer(DocumentSerializer):
    
    class Meta:
        model = Image
        fields = "__all__"
        depth=0

class IdeaSerializer(DocumentSerializer):
    
    class Meta:
        model = Idea
        fields = "__all__"
        depth = 0

class IdeaDeepSerializer(DocumentSerializer):
    user = UserMiniSerializer()

    class Meta:
        model = Idea
        fields = "__all__"
        depth = 1

class IdeaTwoDeepSerializer(DocumentSerializer):

    class Meta:
        model = Idea
        fields = "__all__"
        depth = 2

class RateSerializer(DocumentSerializer):

    class Meta:
        model = Rate
        fields = "__all__"
        depth = 0

class RateDeepSerializer(DocumentSerializer):

    class Meta:
        model = Rate
        fields = "__all__"
        depth =1

class ScreenshotSerializer(DocumentSerializer):

    class Meta:
        model=Screenshot,
        fields="__all__"
        depth=0

class TagSerializer(DocumentSerializer):

    class Meta:
        model = Tag
        fields = "__all__"
        depth = 0