#Django lib
from rest_framework.response import Response

#Internal libs
from toolkit.toolkit import existence_error, validate_error
from apps.admins.models import TetherToman
from apps.admins.serializers import TetherTomanSerializer

#_________________________GET______________________________
def get_tethertoman_obj() -> (object, Response):
    err = None

    tethertoman_obj = TetherToman.objects.filter(id=1).first()
    if tethertoman_obj is None:
        err = existence_error("TetherToman")
        return None, err

    return tethertoman_obj, err

def get_tethertoman_data_by_obj (tethertoman_obj) -> dict:
    tethertoman_serialized = TetherTomanSerializer(tethertoman_obj)

    return tethertoman_serialized.data

#_________________________UPDATE______________________________

def update_tethertoman(tethertoman_obj: object ,price: float) -> (dict, Response):
    err = None

    tethertoman_serialized = TetherTomanSerializer(
        tethertoman_obj,
        data= {"price":price},
        partial= True
    )
    if not tethertoman_serialized.is_valid():
        err = validate_error(tethertoman_serialized)

        return {}, err

    tethertoman_serialized.save()

    return tethertoman_serialized.data, err
