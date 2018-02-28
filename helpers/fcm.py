from django.contrib.auth.models import User
from fcm_django.models import FCMDevice


def notify_user(user, data, title=None, message=None, silent=True):
    '''
        Sends an FCM notification to a user
        If the message is silent, title and message are included in the data dictionary
    '''



    if not data:
        data = {}
    if not message and not title:
        silent = True
    if title and silent:
        data['title'] = title
    if message and silent:
        data['message'] = message

    print data

    device = FCMDevice.objects.filter(user=user).first()
    if device is None:
        return
    if silent:
        result = device.send_message(data=data)
    else:
        result = device.send_message(title=title, message=message, data=data)
    print result


def broadcast_notification(users=None, data=None, title=None, message=None, silent=True):
    '''
        Sends an FCM notification to a user
        If the message is silent, title and message are included in the data dictionary
    '''

    devices = FCMDevice.objects.all()
    if users is not None:
        devices.filter(user__in=users)

    if not data:
        data = {}
    if not message and not title:
        silent = True
    if title and silent:
        data['title'] = title
    if message and silent:
        data['message'] = message

    if silent:
        result = devices.send_message(data=data)
    else:
        result = devices.send_message(title=title, message=message, data=data)

    print result