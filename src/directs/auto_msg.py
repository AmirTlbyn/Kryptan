
from typing import Optional

from persiantools.jdatetime import JalaliDate
from datetime import datetime
from persiantools import characters, digits

from directs.models import AutomaticMessage, MessageBox
from directs.serializers import AutomaticMessageSerializer, MessageBoxSerializer

from massage.models import MassageBox

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




def send_message(
    user_serialized = None,
    greeting_bool : bool = False,
    plan_bool : bool = False,
    plan_serialized = None,
    ban_bool : bool = False,
    other : bool = False,
    msg_text : str = None,
    title : str = None,
):

    username = user_serialized.data.get("username")
    name_and_lname = user_serialized.data.get("name") + " " + user_serialized.data.get("lastname")

    if greeting_bool:
        title = "خوش‌آمد گویی"

        text = characters.ar_to_fa('''
        کاربر گرامی {0} عزیز، ورود شما به سایت کریپتان را خوش آمد می‌گوییم
        '''.format(
            username,
        ).strip())

    
    elif plan_bool:
        start_date = get_day(plan_serializer.data.get("buy_date"))
        end_date = get_day(plan_serialized.data.get("expire_date"))

        title = "ارتقای اکانت"

        text = characters.ar_to_fa('''
        کاربر گرامی {0} عزیز،
        .اکانت شما در روز {1} مورخ {2} با موفقیت ارتقا یافت و تا روز {3} مورخ {4} اعتبار دارد 
         '''.format(
            username,
            start_date.get("day_name"),
            "{0}/{1}/{2}".format(start_date.get("year"), start_date.get("month"), start_date.get("day")),
            end_date.get("day_name"),
            "{0}/{1}/{2}".format(end_date.get("year"), end_date.get("month"), end_date.get("day")),
        ).strip())


    elif ban_bool:
        title ="اخطاریه مسدود سازی"

        text = characters.ar_to_fa('''
        کاربر گرامی {0} عزیز،
        نقض قوانین سایت از طرف شما توسط ادمین مشاهده گردید.
        لطفا توجه داشته باشید که در صورت نقض دوباره‌ی قوانین اکانت شما به صورت موقت از دسترس خارج خواهد شد.
        برای خواندن قوانین سایت به صفحه سوالات متدوال رجوع کنید
        '''.format(
            username,
        ).strip())

    elif other:
        title = title
        text = characters.ar_to_fa(msg_text)
    

    # create new automatic massage
    automatic_message_serialized = AutomaticMessageSerializer(data={
        "title" : title,
        "text" : text,
    })
    if not automatic_message_serialized.is_valid():
        raise Exception("massage not saved.")
    automatic_message_serialized.save()
    messagebox_obj = MessageBox.objects.filter(user=user_serialized.data.id).first()
    if messagebox_obj is None:
        raise Exception("message box doesn't exist.")
    msgbox_serialized = MessageBoxSerializer(messagebox_obj)
    automsg_list = msgbox_serialized.data.get("automatic_messages")
    automsg_unread = msgbox_serialized.data.get("automatic_msg_unread")

    automsg_list.append(automatic_message_serialized.data.id)
    automsg_unread += 1

    msgbox_serialized = MessageBoxSerializer(
        messagebox_obj,
        data={
            "automatic_messages": automsg_list,
            "automatic_msg_unread": automsg_unread,
        },
        partial=True
    )

    if not msgbox_serialized.is_valid():
        raise Exception("messagebox is not valid")

    # send push notification
    if user_serialized.data.get("device_token") is not None:
        push_notification(
            title = "کریپتان",
            text = text,
            device_token = user_serialized.data.get("device_token"),
        )
