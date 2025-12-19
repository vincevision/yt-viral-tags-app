import os
import requests
from collections import Counter, defaultdict
from dotenv import load_dotenv

load_dotenv()  # loads .env file locally if present

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def search_video_ids(query: str, max_results: int = 25, order: str = "relevance"):
    """
    Search YouTube for videos matching the query and return a list of video IDs.
    'order' can be: date, rating, relevance, title, videoCount, viewCount
    """
    if not YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is not set.")

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": order,
        "key": YOUTUBE_API_KEY,
    }
    response = requests.get(SEARCH_URL, params=params)
    response.raise_for_status()
    data = response.json()

    video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
    return video_ids


def fetch_video_details(video_ids):
    """
    Given a list of video IDs, fetch their snippet (for tags) and statistics (for views).
    """
    if not YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is not set.")

    if not video_ids:
        return []

    params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY,
        "maxResults": 50,
    }
    response = requests.get(VIDEOS_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("items", [])


def rank_tags_from_query(query: str, max_results: int = 25, order: str = "relevance"):
    """
    - Search videos by query (with given order)
    - Collect tags from those videos
    - Rank tags by popularity (views + frequency)
    Returns a list of dicts: [{rank, tag, frequency, total_views}, ...]
    """
    video_ids = search_video_ids(query, max_results=max_results, order=order)
    videos = fetch_video_details(video_ids)

    tag_frequency = Counter()
    tag_view_score = defaultdict(int)  # total views for videos using this tag

    for video in videos:
        snippet = video.get("snippet", {})
        stats = video.get("statistics", {})
        tags = snippet.get("tags", [])  # may be missing on some videos
        view_count = int(stats.get("viewCount", "0"))

        for tag in tags:
            normalized = tag.strip().lower()
            if not normalized:
                continue
            tag_frequency[normalized] += 1
            tag_view_score[normalized] += view_count

    if not tag_frequency:
        return []

    ranked = []
    for tag, freq in tag_frequency.items():
        total_views = tag_view_score[tag]
        ranked.append((tag, freq, total_views))

    # Sort primarily by total_views, then by frequency
    ranked.sort(key=lambda x: (x[2], x[1]), reverse=True)

    result = []
    for i, (tag, freq, views) in enumerate(ranked, start=1):
        result.append(
            {
                "rank": i,
                "tag": tag,
                "frequency": freq,
                "total_views": views,
            }
        )
    return result


def get_viral_videos(query: str, max_results: int = 5):
    """
    Return the most 'viral' videos for a query (sorted by viewCount).
    Each item: {title, channel, views, url}
    """
    # Search ordered by viewCount (most-viewed first)
    video_ids = search_video_ids(query, max_results=max_results, order="viewCount")
    videos = fetch_video_details(video_ids)

    results = []
    for v in videos:
        snippet = v.get("snippet", {})
        stats = v.get("statistics", {})
        title = snippet.get("title", "No title")
        channel = snippet.get("channelTitle", "Unknown channel")
        views = int(stats.get("viewCount", "0"))
        vid_id = v.get("id")
        url = f"https://www.youtube.com/watch?v={vid_id}" if vid_id else None

        results.append(
            {
                "title": title,
                "channel": channel,
                "views": views,
                "url": url,
            }
        )

    # Just in case, sort again by views descending
    results.sort(key=lambda x: x["views"], reverse=True)
    return results