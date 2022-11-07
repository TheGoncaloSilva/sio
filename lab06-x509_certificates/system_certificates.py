from cryptography import x509
from cryptography.hazmat.primitives import serialization
from datetime import datetime
import os, sys
from os import listdir
from os.path import isfile, join

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

def save_to_map(osPath):
    certificates = {}
    files = [f for f in listdir(osPath) if isfile(join(osPath, f))]
    for _file in files:
        with open(osPath+"/"+_file, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())
            if check_certificate(cert):
                certificates[cert.subject] = cert
    return certificates

def main2(argv):
    path = "/etc/ssl/certs"
    if len(argv) >= 2:
        path = argv[1]

    certificates = save_to_map(path)
    code_file = "code.pem"
    cert_code = x509.load_pem_x509_certificate(read_certificate(code_file))
    azure_file = "Azure.pem"
    azure_cert = x509.load_pem_x509_certificate(read_certificate(azure_file))
    path = [cert_code, azure_cert, certificates[azure_cert.issuer]]
    print(path)

main2(sys.argv)