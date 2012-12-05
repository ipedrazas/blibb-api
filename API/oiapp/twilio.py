



from twilio.rest import TwilioRestClient
import re


TWILIO_ACCOUNT = get_config_value('TWILIO_ACCOUNT')
TWILIO_TOKEN = get_config_value('TWILIO_TOKEN')
TWILIO_NUMBER = get_config_value('TWILIO_NUMBER')


client = TwilioRestClient(TWILIO_ACCOUNT, TWILIO_TOKEN)

def send_sms(msg, number):
    message = client.sms.messages.create(to=number, from_=TWILIO_NUMBER, body=msg)


def is_phone_number(number):
    p = r'^7(?:[1-4]\d\d|5(?:0[0-8]|[13-9]\d|2[0-35-9])|624|7(?:0[1-9]|[1-7]\d|8[02-9]|9[0-689])|8(?:[014-9]\d|[23][0-8])|9(?:[04-9]\d|1[02-9]|2[0-35-9]|3[0-689]))\d{6}$'
    mobile = number[-10:]
    pattern = re.compile(p)
    res = pattern.search(mobile)
    if res:
        return True
    return False
