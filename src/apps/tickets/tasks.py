#Python libs
from datetime import datetime, timedelta

#Internal libs
from Kryptan.celery import app
from toolkit.toolkit import response_creator, validate_error
from apps.tickets.models import TicketText, TicketRoom
from apps.tickets.serializers import TicketRoomSerializer
import repositories as repo


@app.task(bind=True)
def check_for_ticket_expireness(self, ticket_id):
    print("task is running!")

    ticket_obj, _ = repo.tickets.get_ticket_object_by_id(ticket_id)
    ticket_serialized = repo.tickets.get_ticket_data_by_obj(ticket_obj)

    check_time = datetime.timestamp(
        datetime.fromtimestamp(ticket_serialized.get("last_update")) + \
            timedelta(days = 7)
    )

    if ticket_serialized.get("status") == "a":
        if datetime.timestamp(datetime.now()) > check_time:

            ticket_serialized, err = repo.tickets.update_ticket(
                ticket_obj,
                data={
                    "status":"e",
            }) 
            if err is not None:
                return err 
            print(f'closed {ticket_serialized.get("id")}')
            return response_creator(data=ticket_serialized)
        else:
            check_for_ticket_expireness.apply_async(
                (ticket_id,),
                countdown = check_time - datetime.timestamp(datetime.now()),
            )
    elif ticket_serialized.get("status") == "i":
        if datetime.timestamp(datetime.now()) > check_time:
            check_for_ticket_expireness.apply_async(
                (ticket_id,),
                countdown = datetime.timestamp(datetime.now() + timedelta(days = 7)),
            )
        else:
            check_for_ticket_expireness.apply_async(
                (ticket_id,),
                countdown = check_time - datetime.timestamp(datetime.now()),
            )
    
    print(f'closed {ticket_serialized.get("id")}')
    return response_creator()
    
