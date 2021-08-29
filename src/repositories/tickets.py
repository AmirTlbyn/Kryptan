#Django lib
from rest_framework.response import Response

#Internal libs
from toolkit.toolkit import validate_error, existence_error
from apps.tickets.models import (
    TicketRoom,
    TicketText,
)
from apps.tickets.serializers import (
    TicketRoomSerializer,
    TicketTextSerializer,
)

#_________________________CREATE______________________________

def create_text_obj (data) -> (dict, Response):
    err = None

    text_serialized = TicketTextSerializer(data=data)

    if not text_serialized.is_valid():
        err = validate_error(text_serialized)
        return {}, err

    text_serialized.save()

    return text_serialized.data, err

def create_ticket_obj (data) -> (dict, Response):
    err = None

    ticket_serialized = TicketRoomSerializer(data=data)
    
    if not ticket_serialized.is_valid():
        err = validate_error(ticket_serialized)
        return {}, err

    ticket_serialized.save()

    return ticket_serialized.data, err

#_________________________GET______________________________

def get_ticket_object_by_id (ticket_id: int) -> (object, Response):
    err = None

    ticket_obj = TicketRoom.objects.filter(id=ticket_id).first()

    if ticket_obj is None:
        err = existence_error("Ticket")
        return {}, err

    return ticket_obj, err

def get_ticket_data_by_obj (ticket_obj) -> dict:
    ticket_serialized = TicketRoomSerializer(ticket_obj)

    return ticket_serialized.data

def get_tickes_data_by_user(user_id: int) -> dict:

    ticket_objs = TicketRoom.objects.filter(user = user_id)

    tickets_serialized = TicketRoomSerializer(ticket_objs, many= True)

    return tickets_serialized.data


#_________________________UPDATE______________________________

def update_ticket (ticket_obj, data) -> (dict, Response):
    err = None

    ticket_serialized = TicketRoomSerializer(
        ticket_obj,
        data=data,
        partial=True
    )
    if not ticket_serialized.is_valid():
        err = validate_error(ticket_serialized)
        return {}, err
    
    ticket_serialized.save()

    return ticket_serialized.data, err
