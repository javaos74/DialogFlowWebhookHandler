import json
import requests
import pprint
from flask import Flask, jsonify, request, make_response

from orchestrator import Orchestrator

# --------------------------------------
# flask app 초기화
# --------------------------------------
app = Flask(__name__)
# --------------------------------------
# Orchestrator 객체 생성
# --------------------------------------
orch = Orchestrator('default', 'userid', 'password')
ID = None # job ID

fulfillment = {}
# --------------------------------------
# 응답처리
# --------------------------------------
def results():
    req = request.get_json(force=True)
    pprint.pprint(req)
    result = {}
    action = req.get('queryResult').get('action')
    display_name = req.get('queryResult').get('intent').get('displayName')
    global fulfillment, orch, ID
    if display_name == 'check.status':
        response = orch.request('get', orch.Jobs + '(%s)' % ID)
        if response['State'] == 'Pending' or response['State'] == 'Running':
            result["fulfillmentText"] = '아직 작업 중입니다. 조금만 더 기다려 주시겠어요?'
        if response['State'] == 'Successful':
            response = json.loads(response["OutputArguments"])
            result['fulfillmentText'] = response['out_Summary']
    if action == 'IDCheck.IDCheck-custom':
        fulfillment['Type'] = req.get('queryResult').get('parameters').get('Type')
        result["fulfillmentText"] = "주소를 알려주세요."
    if action == 'IDCheck.IDCheck-custom.IDCheck-custom-custom':
        fulfillment['Address'] = req.get('queryResult').get('queryText')
        payload = build_argument(fulfillment['Type'], fulfillment['Address'])
        response = orch.request('post', orch.startJobs, body=payload)
        print(response)
        ID = response["value"][0]["Id"]
        result["fulfillmentText"] = fulfillment['Type']+"등기부 등본을 확인 중입니다..."


    # jsonify the result dictionary
    # this will make the response mime type th application/json
    result = jsonify(result)

    # return a result json
    return make_response(result)

# --------------------------------------
# searching json data 생성
# --------------------------------------
def build_argument(rtype, address):
    inputArgs = {
        "in_Type": rtype,
        "in_Address": address,
    }
    startInfo = {
        'startInfo': {
            "ReleaseKey": "4539d299-69b1-4e9a-b955-9a6d335eb1cc",
            "Strategy": "Specific",
            "RobotIds": [
                9
            ],
            "NoOfRobots": 0,
            "Source": "Manual",
            "InputArguments": json.dumps(inputArgs)
        }
    }
    return json.dumps(startInfo)
  
# --------------------------------------
# dialogflow webhook
# --------------------------------------
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return results()


# --------------------------------------
# 메인함수
# --------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
