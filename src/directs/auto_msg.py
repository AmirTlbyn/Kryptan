
from typing import Optional

from persiantools.jdatetime import JalaliDate
from datetime import datetime
from persiantools import characters, digits

from infrastructure.massage.models import AutomaticMessage
from infrastructure.massage.serializers import AutomaticMessageSerializer

from infrastructure.massage.models import MassageBox

import requests
import json


def get_day(time: float):
    date = JalaliDate(datetime.fromtimestamp(time))
    return {
        "day" : date.day,
        "month" : date.month,
        "year" : date.year,
        "day_name" : date.strftime("%A", locale="fa"),
    }



def push_notification(
                        title : str,
                        text : str, 
                        device_token : str,
                    ):

    serverToken = 'AAAAHxjZdtg:APA91bF2o2X39VXskVpnwWSjRMo4czRJ1GKNqR_hZuq4z-3_vZAhXwhcPIsrXu9GcPjeC83qRNcNS761467Of4aqivEXKgsup0AVkOIPJlzoOu8P_o6V4Q6PzTYHU1V4HkPtyEBE9RMs'
    deviceToken = device_token

    headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }

    body = {
            'notification': {
                                'title': title,
                                'body': text
                            },
            'to':
                deviceToken,
            'priority': 'high',
            }
    try:
        response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body), timeout=5)
    except Exception as e:
        pass
    # print(response.status_code)
    # print(response.json())




def send_massage(
    user_serialized= None,
    reserved_serialized = None,
    reserved_bool : bool = False,
    time : float= None,
    withdraw : bool = False,
    deposit : bool = False,
    price : Optional[float]= None,
    other : bool = False,
    msg_text : str = None,
    title : str = None,
):

    name_and_lname = user_serialized.data.get("name") # + ' ' + user_serialized.data.get("last_name")


    if reserved_bool:
        start_time = digits.en_to_fa(str(reserved_serialized.data.get("start_time")))
        end_time = digits.en_to_fa(str(reserved_serialized.data.get("end_time")))
        date = get_day(reserved_serialized.data.get("day"))

        title = "رزرو"

        text = characters.ar_to_fa('''
{0} عزیز
رزرو شما از ساعت {1} تا {2} در روز {3} مورخ {4} با موفقیت ثبت شد.
'''.format(
    name_and_lname,
    start_time,
    end_time,
    date.get("day_name"),
    "{0}/{1}/{2}".format(date.get("year"), date.get("month"), date.get("day")),
).strip())


    # variz
    elif deposit:
        start_time = digits.en_to_fa(str(reserved_serialized.data.get("start_time")))
        end_time = digits.en_to_fa(str(reserved_serialized.data.get("end_time")))
        date = get_day(reserved_serialized.data.get("day"))

#         text = characters.ar_to_fa('''
# {0} عزیز
# رزرو شما از ساعت {1} تا {2} در روز {3} مورخ {4} کنسل شد.
# مبلغ {5} به حساب کیف پول شما اضافه شد.
# '''.format(
#     name_and_lname,
#     start_time,
#     end_time,
#     date.get("day_name"),
#     "{0}/{1}/{2}".format(date.get("year"), date.get("month"), date.get("day")),
#     price,
# ).strip())

        title = "کنسل"

        text = characters.ar_to_fa('''
{0} عزیز
رزرو شما از ساعت {1} تا {2} در روز {3} مورخ {4} کنسل شد.
'''.format(
    name_and_lname,
    start_time,
    end_time,
    date.get("day_name"),
    "{0}/{1}/{2}".format(date.get("year"), date.get("month"), date.get("day")),
).strip())


    # bardasht
    # ...


    elif other:
        text = characters.ar_to_fa(msg_text)
    

    # create new automatic massage
    automatic_message_serialized = AutomaticMessageSerializer(data={
        "title" : title,
        "text" : text,
        "massage_box" : MassageBox.objects.filter(user=user_serialized.data.get("id")).first().id,
    })
    if not automatic_message_serialized.is_valid():
        raise Exception("massage not saved.")
    automatic_message_serialized.save()


    # send push notification
    if user_serialized.data.get("device_token") is not None:
        push_notification(
            title = "راکو اپ",
            text = text,
            device_token = user_serialized.data.get("device_token"),
        )
