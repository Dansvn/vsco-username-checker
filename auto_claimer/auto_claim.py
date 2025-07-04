import os
import time
import random
import string
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def read_list_file(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def append_to_file(text, filename):
    with open(filename, "a") as f:
        f.write(text + "\n")

def append_account_pretty(username, email, password, filename="accounts_created.txt"):
    line = f"{username:40} | {email:35} | {password:15}"
    with open(filename, "a") as f:
        f.write(line + "\n")

def ensure_header(filename="accounts_created.txt"):
    if not os.path.exists(filename) or os.stat(filename).st_size == 0:
        with open(filename, "w") as f:
            f.write(f"{'User':40} | {'Email':35} | {'Password':15}\n")
            f.write("-" * 96 + "\n")

def slow_type(element, text, delay=0.15):
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

def clear_and_type_human_like(element, text):
    element.click()
    time.sleep(0.5)
    element.send_keys(Keys.CONTROL, "a")
    time.sleep(0.3)
    element.send_keys(Keys.BACKSPACE)
    time.sleep(0.5)
    slow_type(element, text)

def create_vsco_account(driver, email, password, username):
    driver.get("https://vsco.co/user/signup")
    time.sleep(3)

    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "email").send_keys(email)

    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys(password)

    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "username").send_keys(username)

    birthday_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "birthday")))
    clear_and_type_human_like(birthday_input, "10/10/2000")
    time.sleep(1)

    signup_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "signupButton")))
    signup_button.click()

def validate_success(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(lambda d: "/subscribe/start" in d.current_url)
        return True
    except TimeoutException:
        return False

def start_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")  # Remove this line if you want visible browser
    return webdriver.Chrome(options=options)

def main():
    default_password = "polarr2020"
    emails = read_list_file("emails.txt")
    usernames = read_list_file("available.txt")
    used_usernames = set(read_list_file("usernames_used.txt"))
    used_emails = set(read_list_file("emails_used.txt"))

    available_emails = [email for email in emails if email not in used_emails]

    if not available_emails:
        print("[END] All emails in the list have been used.")
        return

    ensure_header()

    for email in available_emails:
        print(f"\n[EMAIL] Using email: {email}")
        driver = start_driver()

        for username in usernames:
            if username in used_usernames:
                print(f"[SKIP] Username already used: {username}")
                continue

            try:
                print(f"[INFO] Trying username '{username}' with email '{email}'")
                create_vsco_account(driver, email, default_password, username)

                if validate_success(driver):
                    print(f"[SUCCESS] Account created: {username} | Email: {email}")
                    append_account_pretty(username, email, default_password)
                    append_to_file(username, "usernames_used.txt")
                    append_to_file(email, "emails_used.txt")

                    used_usernames.add(username)
                    used_emails.add(email)

                    driver.quit()
                    break
                else:
                    print(f"[FAIL] Failed with username '{username}', trying next...")
                    append_to_file(username, "usernames_used.txt")
                    used_usernames.add(username)
            except Exception as e:
                print(f"[ERROR] {e}")

        else:
            driver.quit()

    print("[END] All available emails have been processed.")

if __name__ == "__main__":
    main()
