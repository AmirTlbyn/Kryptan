from rest_framework_mongoengine.serializers import DocumentSerializer

from ideas.models import (
    Image,
    Idea,
    Rate,
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

    class Meta:
        model = Idea
        fields = "__all__"
        depth = 1

class IdeaDeepDeepSerializer(DocumentSerializer):

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