#Django lib
from rest_framework.response import Response

#Python libs
from datetime import date, datetime, timedelta
from time import mktime

#Internal libs
from toolkit.toolkit import existence_error, validate_error
from apps.users.models import (
    Plan,
    User,
)
from apps.users.serializers import (
    PlanSerializer,
    UserSerializer,
)

#_________________________GET______________________________

def get_plan_object_by_id (plan_id: int) -> (object, Response):
    err = None

    plan_obj = Plan.objects.filter(id = plan_id).first()

    if plan_obj is None:
        err = existence_error("Plan")
        return None, err

    return plan_obj, err

def get_user_object_by_phone_number(phone_number) -> (object, Response):
    err = None

    user_obj = User.objects.filter(phone_number=phone_number).first()

    if user_obj is None:
        err = existence_error("User")
        return None, err

    return user_obj, err

def get_user_object_by_username (username) -> (object, Response):
    err = None

    user_obj = User.objects.filter(username=username).first()

    if user_obj is None:
        err = existence_error("User")
        return None, err

    return user_obj, err

def get_user_object_by_id (user_id :int) -> (object, Response):
    err = None

    user_obj = User.objects.filter(id=user_id).first()

    if user_obj is None:
        err = existence_error("User")
        return None, err

    return user_obj, err

def get_user_data_by_obj (user_obj) -> dict:
    user_serialized = UserSerializer(user_obj)

    return user_serialized.data

#_________________________UPDATE______________________________

def update_user(user_obj, data) -> (dict, Response):
    err = None

    user_serialized = UserSerializer(
        user_obj,
        data=data,
        partial = True
    )

    if not user_serialized.is_valid():
        err = validate_error(user_serialized)
        return {}, err

    user_serialized.save()

    return user_serialized.data, err

#_________________________VALIDATOR______________________________

def mobile_number_validator(mobile_number) -> bool:
    if (
        (mobile_number is not None)
        and (mobile_number[0:2] == "09")
        and (len(mobile_number) == 11)
    ):
        return True
    return False

def username_validator(username) -> bool:
    pattern = "([a-z]*[0-9]*(_)*)*"

    matched =re.match(pattern, username)

    if (matched.start() == 0) and (matched.end() == len(username)):
        return True
    return False

def is_available (username):
    user = User.objects.filter(username=username).first()
    if user is None:
        return True
    return False

def add_minute(min: int = 0) -> float:
    # by default return timestamp of now
    date_time = datetime.now() + timedelta(minutes=min)
    return mktime(date_time.timetuple())
