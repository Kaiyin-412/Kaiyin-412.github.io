---
# Copy this file to _posts/YYYY-MM-DD-your-post-title.md (lowercase, hyphens, no spaces)
title: "Box Name — CTF Write-up"
date: 2026-10-19 12:00:00 +0800          # must not be in the future (UTC!), or the post won't show
categories: [CTF Write-ups]               # pick ONE: CTF Write-ups | Pentesting | Malware Analysis | Tools & Tutorials | Notes
tags: [web, linux, privesc]               # lowercase, as many as you like
description: One-sentence summary shown on the home page and in search results.
# image:                                  # optional cover image
#   path: /assets/img/posts/box-name/cover.png
#   alt: Box Name cover
---

## Overview

| | |
| --- | --- |
| **Platform** | HackTheBox / TryHackMe / picoCTF |
| **Difficulty** | Easy |
| **OS** | Linux |
| **Skills** | Enumeration, SQL injection, sudo abuse |

Short summary of the challenge and the attack path.

## Reconnaissance

```bash
nmap -sC -sV -oN nmap/initial <target-ip>
```

What you found and why it matters.

## Initial Access

Steps to get a foothold. Add screenshots like this:

![Login page](/assets/img/posts/box-name/login.png)

## Privilege Escalation

How you got root / admin.

## Lessons Learned

> Key takeaway from this challenge.
{: .prompt-tip }

- What worked
- What you'd do differently
- How to defend against it
