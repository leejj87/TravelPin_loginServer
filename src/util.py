from Crypto.Cipher import AES
import json
import os
import datetime
from . import ini_path
def jsonFileToDict(jsonPath):
    with open(jsonPath, 'r') as f:
        abi_file = json.load(f)
    return abi_file
def jsonFileDump(jsonPath,data):
    with open(jsonPath,'w') as f:
        json.dump(data,f)
def log(msg,path=os.path.join(os.getcwd(),'log.log')):
    with open(path,'a',encoding='utf-8') as f:
        msg=datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')+'\t'+msg+'\n'
        f.write(msg)
def keyMaker(key):
    return "{: <32}".format(key).encode("utf-8")
def encryped(pure_string):
    key=jsonFileToDict(ini_path).get('DB_PASSWORD_KEY')
    if key is None or key=="": raise Exception("DB PASSWORD KEY is MISSING. PLEASE CHECK YOUR INI.JSON")
    obj = AES.new(keyMaker(key), AES.MODE_CFB, 'This is an IV456')
    message = pure_string
    ciphertext = obj.encrypt(message)

    result=ciphertext.decode('utf-8','backslashreplace')
    return result
def decryped(encryped_string):
    key = jsonFileToDict(ini_path).get('DB_PASSWORD_KEY')
    if key is None or key == "": raise Exception("DB PASSWORD KEY is MISSING. PLEASE CHECK YOUR INI.JSON")
    if isinstance(encryped_string,str):
        encryped_string=bytes(encryped_string, 'utf-8')
    obj2 = AES.new(keyMaker(key), AES.MODE_CFB, 'This is an IV456')
    return obj2.decrypt(encryped_string)

