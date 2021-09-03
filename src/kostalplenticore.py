# -*- coding: utf-8 -*-

import sys
import random
import string
import base64
import json
import requests
import hashlib
import os
import hmac
from Crypto.Cipher import AES
import binascii


def randomString(stringLength):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))


def getPBKDF2Hash(PASSWD, bytedSalt, rounds):
    return hashlib.pbkdf2_hmac('sha256', PASSWD.encode('utf-8'), bytedSalt, rounds)


class connect:
    def __init__(self, ip, PASSWD):
        self.BASE_URL = "http://" + ip + "/api/v1"
        self.PASSWD = PASSWD

    def login(self):
        USER_TYPE = "user"
        AUTH_START = "/auth/start"
        AUTH_FINISH = "/auth/finish"
        AUTH_CREATE_SESSION = "/auth/create_session"
        ME = "/auth/me"

        u = randomString(12)
        u = base64.b64encode(u.encode('utf-8')).decode('utf-8')

        step1 = {
            "username": USER_TYPE,
            "nonce": u
        }
        step1 = json.dumps(step1)
        url = self.BASE_URL + AUTH_START
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        response = requests.post(url, data=step1, headers=headers, timeout=10)
        response = json.loads(response.text)

        i = response['nonce']
        e = response['transactionId']
        o = response['rounds']
        a = response['salt']
        bitSalt = base64.b64decode(a)

        r = getPBKDF2Hash(self.PASSWD, bitSalt, o)
        s = hmac.new(r, "Client Key".encode('utf-8'), hashlib.sha256).digest()
        c = hmac.new(r, "Server Key".encode('utf-8'), hashlib.sha256).digest()
        _ = hashlib.sha256(s).digest()
        d = "n=user,r="+u+",r="+i+",s="+a+",i="+str(o)+",c=biws,r="+i
        g = hmac.new(_, d.encode('utf-8'), hashlib.sha256).digest()
        p = hmac.new(c, d.encode('utf-8'), hashlib.sha256).digest()
        f = bytes(a ^ b for (a, b) in zip(s, g))
        proof = base64.b64encode(f).decode('utf-8')

        step2 = {
            "transactionId": e,
            "proof": proof
        }
        step2 = json.dumps(step2)

        url = self.BASE_URL + AUTH_FINISH
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        response = requests.post(url, data=step2, headers=headers, timeout=10)
        response = json.loads(response.text)

        token = response['token']
        signature = response['signature']

        y = hmac.new(_, "Session Key".encode('utf-8'), hashlib.sha256)
        y.update(d.encode('utf-8'))
        y.update(s)
        P = y.digest()
        protocol_key = P
        t = os.urandom(16)

        e2 = AES.new(protocol_key, AES.MODE_GCM, t)
        e2, authtag = e2.encrypt_and_digest(token.encode('utf-8'))

        step3 = {
            "transactionId": e,
            "iv": base64.b64encode(t).decode('utf-8'),
            "tag": base64.b64encode(authtag).decode("utf-8"),
            "payload": base64.b64encode(e2).decode('utf-8')
        }
        step3 = json.dumps(step3)

        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        url = self.BASE_URL + AUTH_CREATE_SESSION
        response = requests.post(url, data=step3, headers=headers, timeout=10)
        response = json.loads(response.text)
        sessionId = response['sessionId']

        # create a new header with the new Session-ID for all further requests
        self.headers = {'Content-type': 'application/json',
                        'Accept': 'application/json', 'authorization': "Session " + sessionId}
        url = self.BASE_URL + ME
        response = requests.get(url=url, headers=self.headers)
        response = json.loads(response.text)
        authOK = response['authenticated']
        if not authOK:
            return response
        else:
            return True

    def getInfo(self):
        url = self.BASE_URL + "/info/version"
        response = requests.get(url=url, headers=self.headers, timeout=10)
        response = json.loads(response.text)
        return response

    # Generic get process data request
    def getProcessdata(self, moduleid, processdata):
        url = self.BASE_URL + "/processdata"
        datareq = [{
            "moduleid": moduleid,
            "processdataids": processdata
        }]
        datareq = json.dumps(datareq)
        response = requests.post(
            url=url, data=datareq, headers=self.headers, timeout=10)
        response = json.loads(response.text)
        return response[0]['processdata']

    def getSettings(self, moduleid, settings):
        url = self.BASE_URL + "/settings"
        datareq = [{
            "moduleid": moduleid,
            "settingids": settings
        }]
        datareq = json.dumps(datareq)
        response = requests.post(
            url=url, data=datareq, headers=self.headers, timeout=10)
        response = json.loads(response.text)
        return response[0]['settings']

    ###
    # Get specific value functions from processdata
    ###
    def getBatteryPercent(self):
        response = self.getProcessdata("devices:local:battery", ['SoC'])
        return response[0]['value']

    def getPvPower(self):
        response = self.getProcessdata("devices:local", ['Dc_P'])
        return response[0]['value']

    def getHomePowerConsumption(self):
        response = self.getProcessdata("devices:local", ['HomeOwn_P'])
        return response[0]['value']

    ###
    # Set values
    ###
    def setBatteryMinSoc(self, value):
        url = self.BASE_URL + "/settings"
        datareq = [{"moduleid": "devices:local", "settings": [
            {"id": "Battery:MinSoc", "value": str(value)}]}]
        datareq = json.dumps(datareq)
        response = requests.put(url=url, data=datareq,
                                headers=self.headers, timeout=10)
        response = json.loads(response.text)
        return response

    def setBatteryDynamicSoc(self, value):
        url = self.BASE_URL + "/settings"
        datareq = [{"moduleid": "devices:local", "settings": [
            {"id": "Battery:DynamicSoc:Enable", "value": str(value)}]}]
        datareq = json.dumps(datareq)
        requests.put(url=url, data=datareq, headers=self.headers, timeout=10)
        return True

    ###
    # Get Events
    ###
    def getEvents(self):
        url = self.BASE_URL + "/events/latest"
        response = requests.get(url=url, headers=self.headers, timeout=10)
        response = json.loads(response.text)
        return response