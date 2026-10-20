---
title: "Soulmate"
date: 2025-09-23 15:40:22 +0800
categories: [HackTheBox,redteam]
tags: [Linux , Easy]
description: "Linux machine"
image:
  path: /assets/img/posts/htb/soulomate/soulmate-cover.png
  alt: "Soulomate"
---

### Machine info
**Link : [soulmate](https://app.hackthebox.com/machines/Soulmate?sort_by=created_at&sort_type=desc)**

**Description : Linux machine**

**Difficulty : Easy**

1. first start with nmap scan 

![Soulomate screenshot 1](/assets/img/posts/htb/soulomate/soulomate-1.png)

2. let us access the webpage . 

3. At first i though is file upload vulnerability but until my friend found there is a subdomain . 

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/n0kovo_subdomains.txt -u http://10.10.11.86 -H "Host: FUZZ.soulmate.htb" -fs 154
```

![Soulomate screenshot 2](/assets/img/posts/htb/soulomate/soulomate-2.png)

4. let us access it . 
![Soulomate screenshot 3](/assets/img/posts/htb/soulomate/soulomate-3.png)

5. Nexti view the page source andfind the crushftp version use . 
![Soulomate screenshot 4](/assets/img/posts/htb/soulomate/soulomate-4.png)

version 11 

6. After myresearch it is related with CVE-2025-31161 is about authenticate bypassing . 
POC 
[0xgh057r3c0n/CVE-2025-31161: 🛡️ CVE-2025-31161 - CrushFTP User Creation Authentication Bypass Exploit](https://github.com/0xgh057r3c0n/CVE-2025-31161/tree/main)

```bash
python3 CVE-2025-31161.py --target_host ftp.soulmate.htb --port 80 --new_user hello --password hello123
```

7. After running we use the credential and enable us to login as admin . 

8. Now we navigate to the admin page and look at the user manager . we can change the password of the user and lets try with ben . Rmb to save it . 
![Soulomate screenshot 5](/assets/img/posts/htb/soulomate/soulomate-5.png)

9. Then we login in as ben with the credential . Then ifound the webProd dir is interesting . Lets have a look . 
![Soulomate screenshot 6](/assets/img/posts/htb/soulomate/soulomate-6.png)

10. ![Soulomate screenshot 7](/assets/img/posts/htb/soulomate/soulomate-7.png)
u see the directory is exactly same as domain of soulmate.htb . 
![Soulomate screenshot 8](/assets/img/posts/htb/soulomate/soulomate-8.png)

11. At the ftp page we can upload file , So we try a reverse shell file and execute it . 
 ![Soulomate screenshot 9](/assets/img/posts/htb/soulomate/soulomate-9.png)
![Soulomate screenshot 10](/assets/img/posts/htb/soulomate/soulomate-10.png)

12. We can execute it via 
```
http://soulmate.htb/shell1.php
```

rmb to setup a listener . 

13. After that i run linpeas and fun smtg malicious
![Soulomate screenshot 11](/assets/img/posts/htb/soulomate/soulomate-11.png)
the root is running smtg lets go to the directory . 
```bash
cd /usr/lib/erlang_login
```

14. Then i start to look at the content of the both escript file 

On the start.escript i found the cred for the ben 

![Soulomate screenshot 12](/assets/img/posts/htb/soulomate/soulomate-12.png)

15. so now we just ssh with the cred provided and we will get the user flag 
![Soulomate screenshot 13](/assets/img/posts/htb/soulomate/soulomate-13.png)

16. Now we need lookback the start.escript , u will foud that thr is another ssh service running on port 2222 but bind woith local host . 
![Soulomate screenshot 14](/assets/img/posts/htb/soulomate/soulomate-14.png)

explanation from gpt : 
![Soulomate screenshot 15](/assets/img/posts/htb/soulomate/soulomate-15.png)

17. so we just ssh into the port 2222
```bash
ben@soulmate:~$ ssh -p 2222 ben@localhost
```
![Soulomate screenshot 16](/assets/img/posts/htb/soulomate/soulomate-16.png)

18. check our priv 


![Soulomate screenshot 17](/assets/img/posts/htb/soulomate/soulomate-17.png)

19. then we can read root flag


![Soulomate screenshot 18](/assets/img/posts/htb/soulomate/soulomate-18.png)



![Soulomate screenshot 19](/assets/img/posts/htb/soulomate/soulmate-result.png)

### what i learn 
1. if can upload try reverse shell 
2. can ssh into local host service 
```
ssh -p 2222 ben@localhost
```