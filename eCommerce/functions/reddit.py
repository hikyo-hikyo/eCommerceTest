import requests
import time
import random


'''def get_reddit_posts(subreddit="productreview", limit=10):
    """
    Fetch latest posts from a subreddit.
    """
    url = f"https://www.reddit.com/r/{subreddit}/new.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.reddit.com/",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        data = response.json()
        posts = []

        for post in data['data']['children'][:limit]:
            post_data = post['data']
            posts.append({
                'title': post_data['title'],
                'author': post_data['author'],
                'url': f"https://reddit.com{post_data['permalink']}",
                'score': post_data['score'],
                'created_utc': post_data['created_utc'],
                'selftext': post_data.get('selftext', '')[:300],
                'num_comments': post_data.get('num_comments', 0),
            })

        return posts

    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            print(
                "Reddit blocked the request (403). This method is increasingly unreliable.")
        else:
            print(f"HTTP Error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []'''


def get_reddit_posts(subreddit="productreview", limit=10):
    """
    Fetch latest posts from a subreddit.
    """
    url = f"https://www.reddit.com/r/{subreddit}/new.json"

    headers = {
        # Reddit requires this
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.10 Safari/605.1.1",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.reddit.com/",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes

        data = response.json()
        posts = []

        for post in data['data']['children']:
            post_data = post['data']
            posts.append({
                'title': post_data['title'],
                'author': post_data['author'],
                'url': f"https://reddit.com{post_data['permalink']}",
                'score': post_data['score'],
                'created_utc': post_data['created_utc'],
                # Short preview
                'selftext': post_data.get('selftext', '')[:200],
            })

        return posts

    except requests.exceptions.RequestException as e:
        print(f"Reddit API error: {e}")
        return []
