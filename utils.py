import rsa

def tokenizer(data, encrypt = True):
    publicKey, privateKey = rsa.newkeys(512)
    if(encrypt):
        return rsa.encrypt(data.encode(),publicKey)
    else :
        return rsa.decrypt(data, privateKey).decode()