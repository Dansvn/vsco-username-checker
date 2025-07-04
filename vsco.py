import os
import time
import requests
import itertools
import string
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

request_counter = 0
counter_lock = threading.Lock()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_ascii_art(filename="ascii.txt"):
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("=== VSCO Username Checker ===")

def send_discord_batch(usernames, webhook_url, attempts=3, chunk_size=50):
    if not usernames or not webhook_url:
        return
    for i in range(0, len(usernames), chunk_size):
        batch = usernames[i:i+chunk_size]
        content = "Available VSCO usernames:\n" + "\n".join(f"`{u}`" for u in batch)
        data = {"content": content}
        for _ in range(attempts):
            try:
                r = requests.post(webhook_url, json=data, timeout=5)
                if r.status_code in (200, 204):
                    break
                elif r.status_code == 429:
                    wait = min(int(r.headers.get("Retry-After", 180)), 180)
                    print(f"[Discord] Rate limited, sleeping {wait}s...")
                    time.sleep(wait)
                else:
                    break
            except:
                time.sleep(2)

def check_username(username, delay=0):
    global request_counter

    if delay > 0:
        time.sleep(delay)

    with counter_lock:
        request_counter += 1
        if request_counter % 6000 == 0:
            print(f"[INFO] Reached {request_counter} requests, sleeping 180 seconds to respect rate limit...")
            time.sleep(180)

    url = f"https://vsco.co/{username}/gallery"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 404:
            return username, True, None
        elif r.status_code == 200:
            return username, False, None
        else:
            return username, None, f"Status {r.status_code}"
    except Exception as e:
        return username, None, str(e)

def generate_usernames(length, charset=string.ascii_lowercase + string.digits):
    for p in itertools.product(charset, repeat=length):
        username = ''.join(p)
        if not username.isdigit():
            yield username

def load_list(filename):
    if not os.path.isfile(filename):
        return set()
    with open(filename, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def menu():
    clear()
    print_ascii_art("ascii.txt")

    try:
        length = int(input("Username length: "))
        if length < 1 or length > 34:
            print("Please enter a length between 1 and 34")
            return
    except:
        print("Invalid input.")
        return

    use_webhook = input("Use Discord webhook? (y/n): ").strip().lower() == 'y'
    webhook_url = None
    batch_size = 50
    if use_webhook:
        webhook_url = input("Enter your Discord webhook URL: ").strip()
        try:
            batch_size = int(input("Send batch size? (default 50): "))
        except:
            batch_size = 50

    taken = load_list("taken.txt")
    available = load_list("available.txt")

    if not os.path.isdir("auto_claimer"):
        os.makedirs("auto_claimer")

    found_taken = 0
    found_available = 0
    buffer_available = []

    max_workers = 10
    max_futures = 100

    username_gen = (u for u in generate_usernames(length) if u not in taken and u not in available)

    with ThreadPoolExecutor(max_workers=max_workers) as executor, \
         open("available.txt", "a", encoding="utf-8") as f_available, \
         open("taken.txt", "a", encoding="utf-8") as f_taken, \
         open("auto_claimer/available.txt", "a", encoding="utf-8") as f_available_auto_claimer:

        futures = {}

        while True:
            try:
                while len(futures) < max_futures:
                    username = next(username_gen)
                    futures[executor.submit(check_username, username, 0)] = username
            except StopIteration:
                pass

            if not futures:
                break

            done_futures = []
            for future in as_completed(futures):
                username, status, data = future.result()
                done_futures.append(future)

                if status is True:
                    print(f"[AVAILABLE] {username}")
                    f_available.write(username + "\n")
                    f_available.flush()
                    f_available_auto_claimer.write(username + "\n")
                    f_available_auto_claimer.flush()
                    found_available += 1
                    buffer_available.append(username)
                    if use_webhook and len(buffer_available) >= batch_size:
                        send_discord_batch(buffer_available, webhook_url, chunk_size=batch_size)
                        buffer_available.clear()
                elif status is False:
                    print(f"[TAKEN] {username}")
                    f_taken.write(username + "\n")
                    f_taken.flush()
                    found_taken += 1
                else:
                    print(f"[ERROR] {username} - {data}")

            for done in done_futures:
                futures.pop(done, None)

        if use_webhook and buffer_available:
            send_discord_batch(buffer_available, webhook_url, chunk_size=batch_size)

    print(f"\nSummary:\n - Taken: {found_taken}\n - Available: {found_available}")

if __name__ == "__main__":
    menu()
