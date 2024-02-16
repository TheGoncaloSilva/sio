"""
    `asymmetric` module, focused on asymmetric encryption handling
"""
import base64
import cryptography
import PyKCS11
from datetime import datetime as datetime
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa , padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.backends import default_backend as db
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.exceptions import InvalidSignature
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.backends.openssl import backend
from cryptography.hazmat.primitives.hashes import SHA1, Hash
from cryptography import x509

def save_key(fileName: str, key: rsa.RSAPrivateKeyWithSerialization | RSAPublicKey) -> None:
    """
    Write key into a file

    Args:
        - fileName: a string representing the file where the key will be saved. 
        - key: An rsa.RSAPrivateKeyWithSerialization or RSAPublicKey object.
    Returns:
        Nothing (None)

    Raises:
        - TypeError: If any of the parameters don't match their expected instance
    """

    if not isinstance(fileName , str):
        raise TypeError('fileName argument must be string')


    if isinstance(key, rsa.RSAPrivateKeyWithSerialization):
        pem_bytes = key.private_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PrivateFormat.PKCS8,
            encryption_algorithm = serialization.NoEncryption()
        )
    elif isinstance(key, RSAPublicKey):
        pem_bytes = key.public_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo
        )
    else:
        raise TypeError("provided key is not an rsa.RSAPrivateKeyWithSerialization or RSAPublicKey object")
    
    with open(fileName, "wb") as f:
        f.write(pem_bytes)

def public_key_to_string(key: rsa.RSAPublicKey) -> str:
    """
    Transform an rsa.RSAPublicKey object into a str object (format: utf-8)

    Args:
        - key: the key is an rsa.RSAPublicKey object.
    Returns:
        - string: String representation of the key (PEM format)

    Raises:
        - TypeError: If any of the parameters don't match their expected instance
    """

    if not isinstance(key,rsa.RSAPublicKey):
        raise TypeError("key should be a rsa.RSAPublicKey object")

    sendKey : bytes = key.public_bytes(encoding = serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo)
    return sendKey.decode("utf-8")


def public_key_from_string(key: str) -> rsa.RSAPublicKey:
        """
        Transform a string representation of an rsa.RSAPublicKey (PEM format) into a rsa.RSAPublicKey object.

        Args:
            - key: the key is the string representing the public key.
        Returns:
            rsa.RSAPublicKey object.

        Raises:
            - TypeError: If key argument is not a string
            - ValueError: If the conversion failed
        """

        if not isinstance(key,str):
            raise TypeError(f"key argument must be a string, received {type(key)}")

        keyBytes : bytes = key.encode('utf-8')
        try:
            public_key = serialization.load_pem_public_key(keyBytes)
        except TypeError as e:
            raise ValueError("Invalid Format: " + str(e))
        except UnsupportedAlgorithm as e:
            raise ValueError("Serialized key is not supported: " + str(e))

        if isinstance(public_key , rsa.RSAPublicKey):
            return public_key
        else:
            raise ValueError("key should be a RSAPublicKey object")


def generate_private_key(keySize: int) -> rsa.RSAPrivateKeyWithSerialization:
    """
    Generate a private key given her size.

    Args:
        - keySize: Size of the key produced.
    Returns:
        rsa.RSAPublicKey object.

    Raises:
        - TypeError: If keySize is not an integer
        - ValueError: If key generation fails.
    """
    if not isinstance(keySize , int):
        raise TypeError("keySize argument should be of type 'int'")

    try:
        private_key = rsa.generate_private_key(
            public_exponent = 65537,
            key_size = keySize
        )
    
    except Exception as e:
        raise ValueError("Error ocurred while generating key: " + e.__str__())

    return private_key

def generate_public_key(private_key: rsa.RSAPrivateKeyWithSerialization) -> rsa.RSAPublicKey:
    """
    Generate a public key based on a private key
    """
    return private_key.public_key()

def encrypt_values(values: bytes, key: rsa.RSAPublicKey) -> bytes:
    """
    Encrypt a message given a public key

    Args:
        - values: The Values to be encrypted
        - key: The rsa.RSAPublicKey to encrypt the values
    Returns:
        The encrypted values, in bytes

    Raises:
        TypeError: If the values are not in bytes format or if the key is not a rsa.RSAPublicKey object
    """
    if not isinstance(values , bytes):
        raise TypeError("values argument should be of type 'bytes'")
    if not isinstance(key, rsa.RSAPublicKey):
        raise TypeError("key argument should be of type 'rsa.RSAPublicKey'")
    
    return key.encrypt(
        values,padding.OAEP(
        mgf = padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label = None
        ))

def decrypt_values(values: bytes, key: rsa.RSAPrivateKeyWithSerialization) -> bytes:
    """
        Decrypt a message given a private key

        Args:
            - values: The values to be encrypted
            - key: The rsa.RSAPrivateKeyWithSerialization to decrypt the values
        Returns:
            The decrypted values, in bytes
        Raises:
            TypeError: If the values are not in bytes format or if the key is not a rsa.RSAPrivateKeyWithSerialization object
    """
    if not isinstance(values , bytes):
        raise TypeError("values argument should be of type 'bytes'")
    if not isinstance(key, rsa.RSAPrivateKeyWithSerialization):
        raise TypeError("key argument should be of type 'rsa.RSAPrivateKeyWithSerialization'")

    data: bytes = key.decrypt(values , padding.OAEP(
        mgf = padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label = None
    ))
    
    return data
    

def sign_message(message: bytes , key: rsa.RSAPrivateKeyWithSerialization) -> bytes:
    """
        Generate a signature of a message given a private key

        Args:
            - message: The message to be signed
            - key: The rsa.RSAPrivateKeyWithSerialization to sign the message

        Returns: 
            The message encrypted, in bytes
    """
    return key.sign(message , padding=padding.PKCS1v15(),
        algorithm=hashes.SHA256())


def verify_signature(message: bytes, signature: bytes, key: rsa.RSAPublicKey) -> bool:
    """
        Check if a signature is valid

        Args:
            - message: The original message
            - signature: The signature of the original message
            - key: the rsa.RSAPublicKey to verify the signature

        Returns:
            A boolean that is False if the signature is invalid, otherwise True

    """
    try:
        key.verify(
            signature,
            message,
            padding=padding.PKCS1v15()
            , algorithm=hashes.SHA256())
    except InvalidSignature:
        return False
    return True


def sign_message_cc(cardPin: str, dataToSign: bytes, label: str = 'CITIZEN AUTHENTICATION KEY') -> bytes:
    """
    Creates a digital signature using a Portuguese Citizen Card

    Args:
        - cardPin: Pin of the card given the associated slot
        - dataToSign: The values to be signed
        - label: Corresponding label of the key (optional)
    Returns:
        - The signature in a bytes object
    Raises:
        - ValueError: The connection to the card couldn't be established
        - PyKCS11.PyKCS11Error: Errors deriving from the card signing
    """
    session = create_connection(cardPin, 0)

    privateKey = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY), #type: ignore
                (PyKCS11.CKA_LABEL, label) #type: ignore
                ])[0]

    mechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, None) #type: ignore
    signature = bytes(session.sign(privateKey, dataToSign, mechanism))
    
    close_connection(session)
    return signature


def verify_signature_cc(certificate: x509.Certificate, 
        text: bytes, signature: bytes) -> bool:
    """
    Validates a digital signature from a Portuguese Citizen Card

    Args:
        - certificate: The certificate of the associated with the 
            RSA key pair used to sign
        - text: The original values
        - signature: The received signature to compare

    Returns:
        - True if the signature is valid, False otherwise
    """

    md = Hash(SHA1(), backend=db())
    md.update(text)
    digest = md.finalize()

    publicKey = get_public_key(certificate)

    try:
        publicKey.verify(
            signature,
            digest,
            PKCS1v15(),
            SHA1()
        )
    except cryptography.exceptions.InvalidSignature: #type: ignore
        return False

    return True

def get_public_key(certificate: x509.Certificate) -> rsa.RSAPublicKey: 
    """
    Get a public key from a certificate
    Args:
        - certificate: Certificate to retrieve the public key
    Returns:
        - The public key in rsa._RSAPublicKey format
    """

    publicKey = certificate.public_key()
    
    return publicKey # type: ignore


def export_certificate(cert: x509.Certificate) -> str:
    """
    Function to convert the certificate into str, in order fort
        it to be sent
    Args:
        - cert: Certificate in x509.Certificate format
    Returns:
        - The certificate in string format
    """
    certBytes : bytes = cert.public_bytes(encoding = serialization.Encoding.DER)
    return base64.b64encode(certBytes).decode("utf-8")


def import_certificate(certStr: str) -> x509.Certificate:
    """
    Function to transform the certificate in str format
        to a usable format
    Args:
        - certStr: Certificate in string format
    Returns:
        - The certificate in x509.Certificate format
    """

    certBytes : bytes = base64.b64decode(certStr)
    try:
        cert = x509.load_der_x509_certificate(certBytes, backend=db())
    except TypeError as e:
        raise ValueError("Invalid Format: " + str(e))
    except UnsupportedAlgorithm as e:
        raise ValueError("Serialized key is not supported: " + str(e))

    return cert


def get_certificate(cardPin: str, label: str = 'CITIZEN AUTHENTICATION CERTIFICATE') -> x509.Certificate: 
    """
    Returns a certificate for a Citizen Card key pair

    Args:
        - cardPin: Pin of the card given the associated slot
        - label: Corresponding label of the certificate (optional)
    Returns:
        The certificate of the given
    Raises:
        - ValueError: The connection to the card couldn't be established
        - PyKCS11.PyKCS11Error: Errors deriving from the card
    """ 

    session = create_connection(cardPin, 0)

    cert_obj = session.findObjects([
                (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE), #type: ignore
                (PyKCS11.CKA_LABEL, label) #type: ignore
                ])[0]

    cert_der_data = bytes(cert_obj.to_dict()['CKA_VALUE'])
    certificate = x509.load_der_x509_certificate(cert_der_data, backend=db())
    
    close_connection(session)
    return certificate


def validate_certificate(cert: x509.Certificate) -> bool: 
    """
    Function to validate a certificate
    Args:
        - cert: The certificate to be checked
    Returns:
        - True if the certificate is valid, False otherwise
    """
    if datetime.now() < cert.not_valid_before:
        return False

    if datetime.now() > cert.not_valid_after:
        return False
    
    # Maybe improve this
    if cert.issuer == None:
        return False

    if cert.subject == None:
        return False

    return True


def create_connection(cardPin: str, slot: int = 0) -> PyKCS11.Session:
    """
    Function to create a connection with the card
    Args:
        - cardPin: Pin of the card given the associated slot
        - slot: Desired slot to establish the session (default=0)
    Returns:
        - Session of the slot
    Raises:
        - ValueError: The connection couldn't be established
    """

    lib = '/usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so'
    
    try:
        pkcs11 = PyKCS11.PyKCS11Lib()
        pkcs11.load(lib)
    except PyKCS11.PyKCS11Error:
        raise ValueError("Error while loading the library")

    try:
        #slot = pkcs11.getSlotList(tokenPresent=True)[1]
        session = pkcs11.openSession(slot)
        session.login(cardPin)
    except PyKCS11.PyKCS11Error:
        raise ValueError("Couldn't open the session")

    return session


def close_connection(session: PyKCS11.Session) -> None:
    """
    Function to close a PyKCS11 session
    Args:
        - session: PyKCS11 session
    """
    session.logout()
    session.closeSession()
        
    