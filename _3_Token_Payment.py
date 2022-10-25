import requests
import json
from requests.structures import CaseInsensitiveDict

url = "https://pay.beep.solutions/capturePhysicalTransactions"

headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
invoiceNumber = ""


def jsonData(details):
    print(details)
    global invoiceNumber
    data = {
        "order_id": str(details[2]),
        "order_amount": str(details[0]),
        "order_currency": "BND",
        "user": "7tlg5sv1093u1o6dzack6183",
        "apiToken": "5db686051c4cbfef43b7313833",
        "json_result": "",
        "pay_status": details[4]
        '''"device_id": 1, --> location
        "order_details": str(slots), ----> row
        "quantity": 1 ---> quantity bought'''
    }
    jsonDumps = json.dumps(data)
    resp = requests.post(url, headers=headers, data=jsonDumps)
    print(resp.status_code)
    print("data send to dashboard")
    '''invoiceNumber = str(details[2])
    if isPhoneNumber:
        smsSender.sendSMS(smsNo, tokens, amount, invoiceNumber)'''
