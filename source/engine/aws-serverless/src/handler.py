#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import boto3


OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps('ok')
}


ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('Oops, something went wrong!')
}


# def send_sms(event, context):
#     ''' Send SMS
#     '''
#     sns = boto3.client("sns")
#     body = event.get("body")
#     if event.get("httpMethod") == "GET" and body:
#         phone = body.get("phone")
#         message = body.get("message")
#         if phone and message:
#             sns.publish(PhoneNumber=phone, Message=message)
#             return OK_RESPONSE
#         else:
#             return ERROR_RESPONSE
#     return ERROR_RESPONSE


def send_sms(event, context):
    ''' Send SMS
    '''
    sns = boto3.client("sns")
    data = json.loads(event['body'])
    phone = data.get("phone")
    message = data.get("message")
    if phone and message:
        sns.publish(PhoneNumber=phone, Message=message)
        return OK_RESPONSE
    else:
        return ERROR_RESPONSE
