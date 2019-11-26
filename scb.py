import requests
import random
import string
import json
import hashlib
import hmac
import hashlib
import binascii

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def getPBKDF2Hash(password, salt, rounds):
    key = hashlib.pbkdf2_hmac(
    'sha256', # The hash digest algorithm for HMAC
    password.encode('utf-8'), # Convert the password to bytes
    salt, # Provide the salt
    rounds # It is recommended to use at least 100,000 iterations of SHA-256
    )
    return key

def create_sha256_signature(byte_key, message):
    #byte_key = binascii.unhexlify(key)
    message = message.encode()
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()

def createClientProof(clientSignature, serverSignature):
    clientlength = len(clientSignature.encode('utf-8'))
    result = []
    #for i in range(clientlength):
    #    result[i] = (0xff & (bytes(clientSignature[i]) ^ bytes(serverSignature[i])))
    return result

username="user"
password= "A123456789"
url = 'http://192.168.1.23/api/v1/'
clientNonce = randomString(16)
reqstart = {"username": username, "nonce": clientNonce}

a = requests.post(url+'auth/start', json=reqstart)
anserstart = json.loads(a.text)

serverNonce = anserstart['nonce']
transactionId = anserstart['transactionId']
salt = anserstart['salt']
rounds = anserstart['rounds']

saltedpassword = getPBKDF2Hash(password, salt, rounds)
clientkey = create_sha256_signature(saltedpassword, "Client Key")
serverkey = create_sha256_signature(saltedpassword, "Server Key")
storedKey = hashlib.sha256(clientkey).hexdigest()
authMessage = "n={},r={},r={},s={},i={},c=biw,r={}"
authMessage.format(username, clientNonce, serverNonce, salt, rounds, serverNonce)
clientSignature = create_sha256_signature(storedKey, authMessage)
serverSignature = create_sha256_signature(storedKey, serverkey)

print(anserstart)
#print(saltedpassword)
#print(clientkey)
#print(serverkey)
#print(storedKey)
print(clientSignature)
print(serverSignature)
print(createClientProof(clientSignature,serverSignature))
#reqfinish = {"proof": "", "transactionId": transactionId}

#b = requests.post(url+'auth/start', json=reqfinish)
#answerfinish = json.loads(b.text)
#print(answerfinish)
