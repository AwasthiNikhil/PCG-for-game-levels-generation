import requests
import concurrent.futures
import random
import time

BASE_URL = "http://127.0.0.1:5000/generate/{}"
TOTAL_REQUESTS = 100
MAX_WORKERS = 10  # Number of concurrent threads
LEVEL_TYPE = 1    # Change from 1–6 for different generators

def send_request(index):
    level_type = LEVEL_TYPE
    seed = random.randint(1000, 9999)
    width = random.randint(20, 40)
    height = random.randint(20, 40)

    params = {
        'x': width,
        'y': height,
        'seed': seed,
    }

    try:
        response = requests.get(BASE_URL.format(level_type), params=params, timeout=10)
        print(f"[{index}] Status: {response.status_code}, Length: {len(response.text)}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[{index}] Request failed: {e}")
        return None

if __name__ == "__main__":
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]
        concurrent.futures.wait(futures)
    end = time.time()
    print(f"Completed {TOTAL_REQUESTS} requests in {end - start:.2f} seconds.")
