# https://mail.python.org/pipermail/cryptography-dev/2016-August/000676.html
# https://stackoverflow.com/questions/30700348/how-to-validate-verify-an-x509-certificate-chain-of-trust-in-python/70643492#70643492
# https://pypi.org/project/pyOpenSSL/
import base64
import PyKCS11
import OpenSSL
from datetime import datetime as datetime
import binascii
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend as db
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1, Hash

def check_certificate_date(cert):
    if datetime.now() < cert.not_valid_before:
        return False
    elif datetime.now() > cert.not_valid_after:
        return False
    else:
        return True

lib = '/usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so' # Citizen card library

pkcs11 = PyKCS11.PyKCS11Lib()
pkcs11.load(lib)
slots = pkcs11.getSlotList(tokenPresent=True)
slotPin = '1111' # Pin of slot 0

# Only needs to access slot 0
all_attr = list(PyKCS11.CKA.keys())

#Filter attributes
all_attributes = [e for e in all_attr if isinstance(e, int)]

session = pkcs11.openSession(0) # slot 0
session.login(slotPin) # DANGER!!! USE YOUR PINCODE!!

#### Search for objects and extract reference to private key and certificate

availableCertificates = session.findObjects([
        (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
        #(PyKCS11.CKA_LABEL, 'CITIZEN AUTHENTICATION CERTIFICATE')
    ])

certificateLabelOrder = [
                        'CITIZEN AUTHENTICATION CERTIFICATE',
                        'SIGNATURE SUB CA',
                        'AUTHENTICATION SUB CA',
                        'ROOT CA',
                        ]

certificateObjs: list = []
for i, certObj in enumerate(availableCertificates):
    attr = session.getAttributeValue(certObj, all_attributes)
    attrDict = dict(list(zip(all_attributes, attr)))
    #print("Type:", PyKCS11.CKO[attrDict[PyKCS11.CKA_CLASS]], "\tLabel:", attrDict[PyKCS11.CKA_LABEL])
    if (PyKCS11.CKO[attrDict[PyKCS11.CKA_CLASS]] != 'CKO_CERTIFICATE' 
        or attrDict[PyKCS11.CKA_LABEL] != certificateLabelOrder[i]):
        raise RuntimeError("Bad certificate values and/or order")

    cert_der_data = bytes(certObj.to_dict()['CKA_VALUE'])
    cert = x509.load_der_x509_certificate(cert_der_data, backend=db())
    if not check_certificate_date(cert):
        raise RuntimeError("Certificates aren't valid")

    #print("Issuer: ", cert.issuer)
    #print("Subject: ", cert.subject)
    #print("-------------------")
    certificateObjs.append(cert)


# Validate if the root certificate is self-signed
if certificateLabelOrder[i] == 'ROOT CA':
    # The subject name and the issuer name must match

    # The subject key identifier and the authority key identifier must match

    # The cert must contain a key usage extension with the KU_KEY_CERT_SIGN bit set
    pass

# Validate signature certificate
print("root: ", dir(certificateObjs[3].subject))
print("sign: ", certificateObjs[1].issuer.rfc4514_string())
if not certificateObjs[3].subject == certificateObjs[1].issuer:
    raise RuntimeError("Signature certificate is not trusted")

# Validate other certificates
startChain = OpenSSL.crypto.x509store()
startChain.add_cert(certificateObjs[3]) # root certificate

chain = OpenSSL.crypto.X509StoreContext(startChain, certificateObjs[0], [certificateObjs[1]])
try:
    chain.verify_certificate()
    print("Certificate chain is trusted")
except OpenSSL.crypto.X509StoreContextError:
    print("Certificate chain contains untrusted certificates")

