from Kryptan.celery import app

from toolkit.toolkit import response_creator, validate_error

from tickets.models import TicketText, TicketRoom
from tickets.serializers import TicketRoomSerializer


@app.task(bind=True)

def