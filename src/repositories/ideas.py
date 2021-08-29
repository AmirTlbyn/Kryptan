#Django lib
from rest_framework.response import Response
from mongoengine.queryset.visitor import Q

#Internal libs
from toolkit.image import upload_image, delete_image
from toolkit.toolkit import existence_error, validate_error
from apps.ideas.models import (
    Image,
    Idea,
    View,
    Screenshot,
)
from apps.ideas.serializers import (
    ImageSerializer,
    IdeaSerializer,
    RateSerializer,
    ViewSerializer,
    ScreenshotSerializer,
)

#_________________________CREATE______________________________

def create_image_object(image, dir, prefix_dir, limit_size, desc="") -> (dict, Response):
    err = None

    file_path = upload_image(
                file=image,
                dir=str(dir),
                prefix_dir=[str(prefix_dir)],
                limit_size=limit_size,
            )
    image_serialized = ImageSerializer(
        data={
            "image": file_path,
            "description" : desc,
        }
    )
    if not image_serialized.is_valid():
        err = validate_error(image_serialized)
        return {}, err
        
    image_serialized.save()

    return image_serialized.data, err

def create_idea_object (data) -> (dict, Response):
    err = None

    idea_serialized = IdeaSerializer(data=data)

    if not idea_serialized.is_valid():
        err = validate_error(idea_serialized)
        return {}, err

    idea_serialized.save()
    
    return idea_serialized.data, err

def create_rate_object(data) -> (dict, Response):
    err = None

    rate_serialized = RateSerializer(data=data)

    if not rate_serialized.is_valid():
        err = validate_error(rate_serialized)
        return {}, err
    
    rate_serialized.save()

    return rate_serialized.data, err

def create_view_object(data) -> (dict, Response):
    err = None

    view_serialized = ViewSerializer(data=data)

    if not view_serialized.is_valid():
        err = validate_error(view_serialized)
        return {}, err

    view_serialized.save()

    return view_serialized.data, err

def create_screenshot_obj(data: dict) ->(dict, Response):
    err = None
    file_path = upload_image(
        file=data.get("screenshot"),
        dir="screenshots",
        prefix_dir=[str(data.get("user"))],
        limit_size=3000,
    )
    data["screenshot"] = file_path

    screenshot_serialized = ScreenshotSerializer(data=data)
    if not screenshot_serialized.is_valid():
        err = validate_error(screenshot_serialized)
        return {}, err

    screenshot_serialized.save()
    return screenshot_serialized.data, err
    

#_________________________GET______________________________

def get_idea_object_by_id (idea_id: int) -> (object, Response):
    err = None

    idea_obj = Idea.objects.filter(id=idea_id).first()

    if idea_obj is None:
        err = existence_error("idea")
        return None, {}, err

    return idea_obj, err

def get_idea_data_by_obj (idea_obj) -> dict:
    idea_serialized = IdeaSerializer(idea_obj)

    return idea_serialized.data

def get_view_object_by_query (query: Q) -> (object, Response):
    err = None

    view_obj = View.objects.filter(query).first()

    if view_obj is None:
        err = existence_error("View")
        return None, err

    return view_obj, err

def get_view_data_by_obj (view_obj) -> dict:
    view_serialized = ViewSerializer(view_obj)

    return view_serialized.data

def get_screenshot_object_by_id (screenshot_id: int) -> (object, Response):
    err = None

    screenshot_obj = Screenshot.objects.filter(id=screenshot_id).first()
    if screenshot_obj is None:
        err = existence_error("Screenshot")
        return None, err

    return screenshot_obj, err

def get_screenshot_data_by_object (screenshot_obj) -> dict:
    screenshot_serialized = ScreenshotSerializer(screenshot_obj)

    return screenshot_serialized.data
#_________________________UPDATE______________________________

def update_idea (idea_obj, data) -> (dict, Response):
    err = None

    idea_serialized = IdeaSerializer(
        idea_obj,
        data=data,
        partial=True
    )

    if not idea_serialized.is_valid():
        err = validate_error(idea_serialized)
        return {}, err
    
    idea_serialized.save()

    return idea_serialized.data, err

def update_rate (rate_obj, data) -> (dict, Response):
    err = None

    rate_serialized = RateSerializer(
        rate_obj,
        data=data,
        partial=True
    )

    if not rate_serialized.is_valid():
        err = validate_error(rate_serialized)
        return {}, err

    rate_serialized.save()

    return rate_serialized.data, err

def update_view(view_obj, data) -> (dict,Response):
    err = None

    view_serialized = ViewSerializer(
        view_obj,
        data=data,
        partial = True
    )

    if not view_serialized.is_valid():
        err = validate_error(view_serialized)
        return {}, err

    view_serialized.save()
    return view_serialized.data, err

