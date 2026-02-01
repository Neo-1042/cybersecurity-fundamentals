# This script accepts 2 command-line parameters:
# URL
# Payload

import requests
import sys
import urllib3

# Whenever the script runs, it will pass the request throught these proxies
# using the Burp Suite
proxies = {'http': 'http://127.0.0.1:8080', 'https' : 'http://127.0.0.1:8043'}


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()
    except IndexError:
        print("[ - ] Usage: %s <url> <payload>" % sys.argv[0])
        print("[ - ] Example: %s www.example.com " 1=1)