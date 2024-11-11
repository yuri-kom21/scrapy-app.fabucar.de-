import requests
import time
from requests.exceptions import RequestException, ConnectionError, Timeout

def api_get_items(cookie, limits=0, offset=0):
    # Define the URL and parameters
    url = "https://app.fabucar.de/api/posts/feed_v2"
    params = {
        'target': 'web',
        'limit': limits,
        'offset': offset,
        'showSurvey': 'false',
        'sorting': '',
        'period': '',
        'disableCache': 'true',
        'closed': 'true'
    }

    # Define the headers, including the cookies
    headers = {
        "accept": "application/json, text/plain, */*",
        "sec-ch-ua": "'Chromium';v='130', 'Google Chrome';v='130', 'Not?A_Brand';v='99'",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "'Windows'",
        "Cookie": cookie,
        "Referer": "https://app.fabucar.de/beitraege?post_type=question_closed"
    }

    # Make the GET request
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            break
        except (ConnectionError, Timeout) as e:
            print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
        except RequestException as e:
            print(f"Error: {e}")
            break

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        return response.json()
        
    else:
        return (f"Error: {response.status_code}, {response.text}")


def api_get_details(cookie, post_id):
    url = f"https://app.fabucar.de/api/posts/list_v2?reply_to_id={post_id}&disableCache=true"

    referrer = f"https://app.fabucar.de/beitraege/{post_id}/motor-ruckelt-im-kalten-zustand--bmw-5-"
    headers = {
        "accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Cookie": cookie,
        "referrer": referrer
    }

    # Make the GET request
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            break
        except (ConnectionError, Timeout) as e:
            print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
        except RequestException as e:
            print(f"Error: {e}")
            break

    # Print the response (JSON)
    if response.status_code == 200:
        return response.json()  # Process the JSON data
        
    else:
        return (f"Error: {response.status_code} - {response.text}")
    

def fetch_all_posts(cookies, items_per_request=100, callback=None):
    all_posts = []
    offset = 0
    
    while True:
        res = api_get_items(cookies, limits=items_per_request, offset=offset)
        if 'posts' in res and res['posts']:
            all_posts.extend(res['posts'])
            if callback:
                callback(res['posts'])
            offset += items_per_request
        else:
            break
        print(f"Fetched {len(all_posts)} posts")
    return all_posts