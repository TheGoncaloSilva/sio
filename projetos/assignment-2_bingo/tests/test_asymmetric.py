import pytest
import sys
import os

from common.asymmetric import *

def test_save_key():
    privateKey = rsa.generate_private_key(
        public_exponent = 65537,
        key_size = 2048
    )
    save_key('private.pem', privateKey)
    assert os.path.exists('private.pem')
    os.remove('private.pem')

    publicKey = privateKey.public_key()
    save_key('public.pem', publicKey)
    assert os.path.exists('public.pem')
    os.remove('public.pem')

def test_public_key_to_and_from_string():
    privateKey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    publicKey = privateKey.public_key()
    keyString = public_key_to_string(publicKey)
    assert isinstance(keyString, str)
    publicKeyFromString = public_key_from_string(keyString)
    assert publicKey.public_numbers() == publicKeyFromString.public_numbers()

def test_generate_private_and_public_key():
    privateKey = generate_private_key(2048)
    assert isinstance(privateKey, rsa.RSAPrivateKeyWithSerialization)
    publicKey = privateKey.public_key()
    assert isinstance(publicKey, rsa.RSAPublicKey)

def test_encrypt_and_decrypt_values():
    privateKey = rsa.generate_private_key(
        public_exponent=65537,
        key_size = 2048
    )
    publicKey = privateKey.public_key()
    encryptedValues = encrypt_values(b'random values', publicKey)
    assert isinstance(encryptedValues, bytes)
    decryptedValues = decrypt_values(encryptedValues, privateKey)
    assert decryptedValues == b'random values'

def test_sign_and_verify_message():
    privateKey = rsa.generate_private_key(
        public_exponent=65537,
        key_size = 2048
    )
    publicKey = privateKey.public_key()

    signature = sign_message(b'random values', privateKey)
    assert isinstance(signature, bytes)
    
    assert verify_signature(b'random values', signature, publicKey)== True
    assert verify_signature(b'invalid message', signature, publicKey) == False
    #verify_signature(b'random values', signature, publicKey)

    #with pytest.raises(InvalidSignature):
        #verify_signature(b'invalid message', signature, publicKey)

def test_signature_workflow():
    return # Uncomment this when sending to git
    pin = '1111'
    dataToSign = b'i am a big potato'
    
    cert = get_certificate(pin)

    valid = validate_certificate(cert)
    assert valid == True
    
    signature = sign_message_cc(pin, dataToSign)

    certStr = export_certificate(cert)
    cert2 = import_certificate(certStr)

    assert verify_signature_cc(cert2, dataToSign, signature)


    