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
from enum import Enum

class EnergyUnit(Enum):
    kWh = 1
    Wh = 2


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
    # See this file for getProcessdata input
    # https://github.com/ITTV-tools/homeassistant-kostalplenticore/blob/master/custom_components/kostal_plenticore/const.py
    ###
    # Battery
    def getBatteryPercent(self):
        response = self.getProcessdata("devices:local:battery", ['SoC'])
        value = response[0]['value']
        return int(value)

    def getBatteryCycles(self):
        response = self.getProcessdata("devices:local:battery", ['Cycles'])
        value =  response[0]['value']
        return int(value)

    # Power (W)
    def getPvPower(self):
        response1 = self.getProcessdata("devices:local:pv1", ['P'])
        response2 = self.getProcessdata("devices:local:pv2", ['P'])
        value = response1[0]['value'] + response2[0]['value'] 
        return int(value)

    def getGridPower(self):
        response = self.getProcessdata("devices:local", ['Grid_P'])
        value = response[0]['value']
        return int(value)

    def getBatteryPower(self):
        response = self.getProcessdata("devices:local:battery", ['P'])
        value = response[0]['value']
        return int(value)

    def getHomePowerConsumption(self):
        response = self.getProcessdata("devices:local", ['Home_P'])
        value = response[0]['value']
        return int(value)

    # Energy (Wh / kWh)

    def convertEnergyUnit(self, valueWh ,energyUnit:EnergyUnit):
        # if energyUnit is in kWh convert from wH
        if energyUnit == EnergyUnit.kWh:
            returnValue = valueWh / 1000 # Wh -> kWh
        else:
            returnValue = valueWh

        return int(returnValue)

    def getHomeConsumptionTotal(self, energyUnit:EnergyUnit=EnergyUnit.kWh):
        response = self.getProcessdata("scb:statistic:EnergyFlow", ['Statistic:EnergyHome:Total'])
        # if energyUnit is in kWh convert from wH
        return self.convertEnergyUnit(response[0]['value'], energyUnit)

    def getHomeConsumptionFromGridTotal(self, energyUnit:EnergyUnit=EnergyUnit.kWh):
        response = self.getProcessdata("scb:statistic:EnergyFlow", ['Statistic:EnergyHomeGrid:Total'])
        # if energyUnit is in kWh convert from wH
        return self.convertEnergyUnit(response[0]['value'], energyUnit)

    def getHomeConsumptionFromPVTotal(self, energyUnit:EnergyUnit=EnergyUnit.kWh):
        response = self.getProcessdata("scb:statistic:EnergyFlow", ['Statistic:EnergyHomePv:Total'])
        # if energyUnit is in kWh convert from wH
        return self.convertEnergyUnit(response[0]['value'], energyUnit)

    def getHomeConsumptionFromBatTotal(self, energyUnit:EnergyUnit=EnergyUnit.kWh):
        response = self.getProcessdata("scb:statistic:EnergyFlow", ['Statistic:EnergyHomeBat:Total'])
        # if energyUnit is in kWh convert from wH
        return self.convertEnergyUnit(response[0]['value'], energyUnit)


    # Voltage
    def getAcVoltage3pAvg(self):
        response1 = self.getProcessdata("devices:local:ac", ['L1_U'])
        response2 = self.getProcessdata("devices:local:ac", ['L2_U'])
        response3 = self.getProcessdata("devices:local:ac", ['L3_U'])
        value = (response1[0]['value'] + response2[0]['value'] + response3[0]['value'])/3
        return int(value)

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
