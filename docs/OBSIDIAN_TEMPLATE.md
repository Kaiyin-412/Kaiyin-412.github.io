---
title: "{{title}}"
date: {{date:YYYY-MM-DD}} {{time:HH:mm}}
platform: HTB
difficulty: Easy
os: Linux
tags: []
description: ""
cover:
draft: false
pin: false
---
%%
How tools/publish.py uses the properties above:
- title        Post title. Defaults to the note name.
- date         Post date. Keep it in the past, or the post stays hidden until the next build after it.
- platform     HTB, THM or CTF. Sets the category. Leave empty to use the vault folder.
- difficulty   Shown in the info table at the top of the post and added to the tags (Easy, Medium, Hard).
- os           Shown in the info table at the top of the post and added to the tags (Linux, Windows).
- tags         Extra tags, e.g. [web, sqli, privesc]. Lowercase, no spaces.
- description  One sentence shown on the home page and in search results.
- cover        Banner image: paste it into this note, then write its file name here, e.g. [[editor-cover.png]].
- draft        true = copied to the blog but hidden (published: false).
- pin          true = pinned to the top of the home page.

Anything between double percent signs (like this block) is never published.
Only use full https:// links. HackTheBox: only publish RETIRED machines.
%%

%% The Platform / Difficulty / OS table is added automatically from the properties above. %%

## Overview

**Skills:** %% e.g. enumeration, CVE exploitation, sudo abuse %%

%% Two or three sentences: what the box is about and the attack path. %%

## Reconnaissance

```bash
nmap -sCV -Pn <target-ip> -p-
```

```
%% paste the scan result %%
```

%% What you found and why it matters. %%

## Enumeration

## Initial Access

## Privilege Escalation

## Lessons Learned

> **Key takeaway:** %% one sentence you want to remember from this box %%
{: .prompt-tip }

- What worked:
- What I'd do differently:
- How to defend against it:
