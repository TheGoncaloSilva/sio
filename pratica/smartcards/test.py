
from __future__ import print_function

from PyKCS11 import *
import binascii

lib = '/usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so'

pkcs11 = PyKCS11Lib()
pkcs11.load(lib)  # define environment variable PYKCS11LIB=YourPKCS11Lib

# get 1st slot
slot = pkcs11.getSlotList(tokenPresent=True)[0]

session = pkcs11.openSession(slot, CKF_SERIAL_SESSION | CKF_RW_SESSION)
session.login("1111")

# "Hello world" in hex
toSign = "48656c6c6f20776f726c640d0a"
mechanism = Mechanism(CKM_SHA1_RSA_PKCS, None)

# find first private key and compute signature
privKey = session.findObjects([(CKA_CLASS, CKO_PRIVATE_KEY)])[0]
signature = session.sign(privKey, binascii.unhexlify(toSign), mechanism)
print("\nsignature: {}".format(binascii.hexlify(bytearray(signature))))

# find first public key and verify signature
pubKey = session.findObjects([(CKA_CLASS, CKO_PUBLIC_KEY)])[0]
result = session.verify(pubKey, binascii.unhexlify(toSign), signature, mechanism)
print("\nVerified:", result)

# logout
session.logout()
session.closeSession()