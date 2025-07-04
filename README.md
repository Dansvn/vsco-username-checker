# VSCO Username Claimer

![image](https://github.com/user-attachments/assets/a3ea4e3f-de6d-4a16-86a1-d7ddc03d919b)


A fast, automated system to claim VSCO usernames using Selenium.  
Designed to create accounts and test availability of usernames efficiently.

---

## Features

- Automated VSCO account creation using Selenium  
- Human-like typing for birthday input to bypass bot detection  
- Avoids reusing emails and usernames 
- Automatically skips used usernames and emails  
- Stores created accounts in a clean, readable format  
- Clean exit when no emails are left to use

---

## Upcoming Improvements

⚠ *Currently, some suspended accounts may return a false 200 OK status, causing the script to treat them as taken.*  
This will be addressed in a future update using VSCO’s internal endpoint:

```
https://vsco.co/api/2.0/sites?subdomain=<username>
```

(No release date for this fix yet.)

---

## Requirements

- Python 3.7+  
- Google Chrome  
- ChromeDriver (matching your Chrome version)  
- `pip` installed libraries:
  - `selenium`
  - `requests`

Install with:

```bash
https://github.com/Dansvn/vsco-username-checker
```

---

## Setup & Installation

1. Clone the repository:

```bash
git clone https://github.com/Dansvn/vsco-username-checker
cd vsco-username-checker
```

2. Install the required libraries:

```bash
pip install -r requirements.txt
```

3. Make sure you have `ChromeDriver` installed and accessible in PATH.

---

## Usage

- Fill `emails.txt` with emails to use  
- Fill `available.txt` with usernames to try  

Then run:

```bash
python main.py
```

- Successfully created accounts will be saved in `accounts_created.txt` in the format:
```
username | email | password
```
- Used usernames are tracked in `usernames_used.txt`  
- Used emails are tracked in `emails_used.txt`  

---

## About

VSCO Username Claimer is a simple automation utility to help users secure VSCO usernames.  
This tool is experimental and not affiliated with VSCO in any way.  
No support or uptime guarantee is provided.

---

## Contact

Feel free to reach out if you have questions or suggestions!  
[https://ayo.so/dansvn](https://ayo.so/dansvn)
