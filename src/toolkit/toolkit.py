from rest_framework.response import Response
from typing import Optional

def validate_error(serialized) -> Response:
    '''
    response validation error
    '''
    return Response(
        {
            "status" : "fail",
            "data" : serialized.errors,
        },
        status = 400
    )

def existence_error(object_name : str) -> Response:
    '''
    response existence error
    ''' 
    return Response(
        {
            "status" : "error",
            "message" : "Object {} does not exist!".format(object_name),
        },
        status = 400
    )

def response_creator(
    data : Optional[dict] = None,
    status_code : int = 200,
    json_type : bool = False,
    status : str = "success"
) -> Response:
    '''
    create response
    '''
    if json_type:
        return {
            "status" : status,
            "data" : data,
        }
    
    return Response(
        {
            "status" : status,
            "data" : data,
        },
        status = status_code
    )