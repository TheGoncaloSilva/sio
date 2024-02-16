from cryptography import x509
from cryptography.hazmat.primitives import serialization
from datetime import datetime
import os, sys

def read_certificate(fileName):
    with open(fileName, "rb") as f:
        return f.read()

def check_certificate(cert):
    if datetime.now() < cert.not_valid_before:
        return False
    elif datetime.now() > cert.not_valid_after:
        return False
    else:
        return True

def main(argv):
    certificate_file = "code.pem"
    if len(argv) >= 2:
        certificate_file = argv[1]

    pem_data = read_certificate(certificate_file)
    cert = x509.load_pem_x509_certificate(pem_data)
    valid = check_certificate(cert)
    
    if valid:
        print("The certificate is valid")
    else:
        print("The certificate is not valid")

main(sys.argv)