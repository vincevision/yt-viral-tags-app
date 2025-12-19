import json

data = r.json()
items = data.get("items", [])
if not items:
    print("No videos returned in search.")
    exit()

# Get the first video ID
video_id = items[0]["id"]["videoId"]
print("First video ID:", video_id)

# 2) Fetch video details including tags
videos_url = "https://www.googleapis.com/youtube/v3/videos"
params2 = {
    "part": "snippet,statistics",
    "id": video_id,
    "key": API_KEY,
}
r2 = requests.get(videos_url, params=params2)
print("Videos status:", r2.status_code)
print("Videos response (first 400 chars):")
print(r2.text[:400])

data2 = r2.json()
items2 = data2.get("items", [])
if items2:
    snippet = items2[0].get("snippet", {})
    print("Tags field:", snippet.get("tags"))
else:
    print("No video details returned.")