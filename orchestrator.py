import requests
import json

class Orchestrator:

    def __init__(self, token_file):
        self.token = ''
        self.tenantName = ''
        with open(token_file) as f:
            tokens = json.loads(f.read())
            self.idToken = tokens['id_token']
            self.refresh_token = tokens['refresh_token']
        self.getLogicalAccountName()
        self.getServiceInstanceLogicalName()
        self.refreshToken()

    def refreshToken(self):
        url ='https://account.uipath.com/oauth/token'
        payload = {
            "grant_type": "refresh_token",
            "client_id": "5v7PmPJL6FOGu6RB8I1Y4adLBhIwovQN",
            "refresh_token":self.refresh_token 
        }
        resp = requests.request('POST', url, data=json.dumps(payload), headers={'Content-Type': 'application/json'}).json()
        self.token = resp['access_token']
        return resp

    def getLogicalAccountName(self):
        url = 'https://platform.uipath.com/cloudrpa/api/getAccountsForUser'
        hdr = {'Authorization': 'Bearer ' + self.idToken}
        resp = requests.request('GET', url, headers=hdr).json()
        self.accountLogicalName = resp['accounts'][0]['accountLogicalName']
        return resp['accounts'][0]['accountLogicalName']

    def getServiceInstanceLogicalName(self):
        url = "https://platform.uipath.com/cloudrpa/api/account/%s/getAllServiceInstances" %(self.accountLogicalName)
        hdr = {'Authorization': 'Bearer ' + self.idToken}
        resp = requests.request('GET', url, headers=hdr).json()
        #print(resp)
        self.tenantName = resp[0]['serviceInstanceLogicalName']
        self.url = 'https://platform.uipath.com/%s/%s/' %(self.accountLogicalName, self.tenantName)
        return resp[0]['serviceInstanceLogicalName']

    def request(self, type, extension, body=None):
        uri = self.url + extension
        hdr = self.__getHeaders(extension)
        #print(uri)
        #print(hdr)
        resp = requests.request(type.upper(), uri, data=body, headers=hdr).json()
        return resp

    def __getHeaders(self, extension):
        hdr = {'Authorization': 'Bearer ' + str(self.token),
                        'X-UIPATH-TenantName' : self.tenantName,
                       'Accept': 'application/json'}
        return hdr 


if __name__ == '__main__' : 
    orch = Orchestrator('token.json')
    resp = orch.request('GET', 'odata/Robots')
    print(resp)
