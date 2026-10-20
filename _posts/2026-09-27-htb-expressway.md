---
title: "Expressway"
date: 2025-09-27 15:40:22 +0800
categories: [HackTheBox,redteam]
tags: [Easy , Linux]
description: "Linux machine"
image:
  path: /assets/img/posts/htb/expressway/expressway-cover.png
  alt: "Expressway"
---

### Machine info
**Link : [Expressway](https://app.hackthebox.com/machines/Expressway?sort_by=created_at&sort_type=desc)**

**Description : Linux machine**

**Difficulty : Easy**


1. run nmap with udp scan
```bash
nmap -sU 10.10.11.87
```

2. found tftp is open 
![Expressway screenshot 1](/assets/img/posts/htb/expressway/expressway-1.png)

3. online search found there is smtg call tftp-enum with nmap[TFTP (Trivial File Transfer Protocol) Pentesting - Exploit Notes](https://exploit-notes.hdks.org/exploit/network/protocol/tftp/)
```bash
nmap -sU --script tftp-enum -p 69 10.10.11.87
```

4. Then i found a config file but it is useless 

5. Next i try to exploited the isakmp port and found smtg useful from this website [500/udp - Pentesting IPsec/IKE VPN - HackTricks](https://book.hacktricks.wiki/en/network-services-pentesting/ipsec-ike-vpn-pentesting.html)

6. So first letcheck the transformation using ike-scan
```bash
ike-scan -M 10.10.11.87
```

run the ike scan in Main mode then we can have a look what encryption use and hash , dh.
![Expressway screenshot 2](/assets/img/posts/htb/expressway/expressway-2.png)

7. So next we want to know the correct id thus at first we send a fake id first . 
```bash
ike-scan -P -M -A --id=he 10.10.11.87
```

we need to send in aggressive mode .
![Expressway screenshot 3](/assets/img/posts/htb/expressway/expressway-3.png)

This is only work when the server responsein aggresive mode (id and auth in plain text)

8. Ok next we can send with this id so we can get the correct psk hash and crack it .

```bash
ike-scan -P -M -A -n --id=ike@expressway.htb 10.10.11.87
```

![Expressway screenshot 4](/assets/img/posts/htb/expressway/expressway-4.png)

9. now we can get the hash and use hashcat to brute force it . 
```bash
hashcat psk.txt /usr/share/wordlists/rockyou.txt.gz
```

u also can use psk-crack
```bash
psk-crack -d /tmp/rockyou.txt hash.txt 
```

![Expressway screenshot 5](/assets/img/posts/htb/expressway/expressway-5.png)
```password
freakingrockstarontheroad
```

10. then we just ssh and get user.txt 
![Expressway screenshot 6](/assets/img/posts/htb/expressway/expressway-6.png)

11. Next run linpeash and u will found the sudo version is vuln to this CVE-2025-32463 . 
Then just search for poc . [CVE-2025-32463/vanda_sudo.sh at main · behnamvanda/CVE-2025-32463 · GitHub](https://github.com/behnamvanda/CVE-2025-32463/blob/main/vanda_sudo.sh)

12. ![Expressway screenshot 7](/assets/img/posts/htb/expressway/expressway-7.png)


![Expressway screenshot 8](/assets/img/posts/htb/expressway/expressway-result.png)



### what I learn
1. ISAKMP - just a framework to defined how the authenticates peers and managed SA.
2. IKE - definied the key exhange , authentication , encryption 
3. ike-scan tools (main mode and aggrressive mode)
4. only vuln if ike run in aggressive mode 
5. hashcat and psk-crack

### attack mindset
1. first run in main mode if it use preshared key nice 
2. next start with basic recon run in main mode (ike-scan)
3. next try with aggressive mode with a random id and see whether got the real id 
4. after get the real id resend again in aggressive mode to get the psk key 
5. decrypt it with hashcat or psk-crack