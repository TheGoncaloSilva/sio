import base64
import PyKCS11
from datetime import datetime as datetime
import binascii
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend as db
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1, Hash

def check_certificate(cert):
    if datetime.now() < cert.not_valid_before:
        return False
    elif datetime.now() > cert.not_valid_after:
        return False
    else:
        return True

lib = '/usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so' # Citizen card library
#lib = '/usr/lib/pcsc/drivers/serial/libifdvpcd.so'

pkcs11 = PyKCS11.PyKCS11Lib()
pkcs11.load(lib)
slots = pkcs11.getSlotList(tokenPresent=True)
pins = ['1111', '1111', '1111']
for i, slot in enumerate(slots):
    print("slot: ", slot)
    all_attr = list(PyKCS11.CKA.keys())

    #Filter attributes
    all_attributes = [e for e in all_attr if isinstance(e, int)]

    session = pkcs11.openSession(slot)
    session.login(pins[i])

    # session.login('1111') # DANGER!!! USE YOUR PINCODE!!

    #### Search for objects and extract reference to private key and certificate

    for obj in session.findObjects():
        attr = session.getAttributeValue(obj, all_attributes)

        attrDict = dict(list(zip(all_attributes, attr)))
        print("Type:", PyKCS11.CKO[attrDict[PyKCS11.CKA_CLASS]], "\tLabel:", attrDict[PyKCS11.CKA_LABEL])
       
    if slot == 0:
        cert_obj = session.findObjects([
                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
                    (PyKCS11.CKA_LABEL, 'CITIZEN AUTHENTICATION CERTIFICATE')
                    ])[0]

        cert_der_data = bytes(cert_obj.to_dict()['CKA_VALUE'])
        cert = x509.load_der_x509_certificate(cert_der_data, backend=db())
        print("Valid: ", check_certificate(cert))
        print("Issuer: ", cert.issuer)
        print("Subject: ", cert.subject)

        """ Encrypting and decrypting """

        # get first public and private keys

        #private_key = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY)])[0]
        private_key = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                (PyKCS11.CKA_LABEL, "CITIZEN AUTHENTICATION KEY")
                ])[0]


        data_to_sign = b'text to sign'

        mechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, None)
        signature = bytes(session.sign(private_key, data_to_sign, mechanism))
        print(f"signature: {signature}")
        """
        public_key = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PUBLIC_KEY),
                (PyKCS11.CKA_LABEL, "CITIZEN AUTHENTICATION CERTIFICATE")
                ])[0]
        print(type(public_key))
        result = session.verify(public_key, data_to_sign, signature, mechanism)
        print("\nVerified: ", result)
        """

        md = Hash(SHA1(), backend=db())
        md.update(data_to_sign)
        digest = md.finalize()

        publicKey = cert.public_key()

        result = publicKey.verify(
            signature,
            digest,
            PKCS1v15(),
            SHA1()
        )
        print("status: ", result)

        

# logout
session.logout()
session.closeSession()
