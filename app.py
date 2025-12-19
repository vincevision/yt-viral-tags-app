import os
from flask import Flask, render_template, request
from yt_tags import rank_tags_from_query, get_viral_videos

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    tags = []
    viral_videos = []
    suggested_title = ""
    tags_text = ""
    query = ""
    error_message = None

    if request.method == "POST":
        query = request.form.get("title", "").strip()
        if query:
            try:
                # 1) Get MOST VIRAL videos for this topic
                viral_videos = get_viral_videos(query, max_results=5)

                # Choose the top viral video's title as a suggested title
                if viral_videos:
                    suggested_title = viral_videos[0]["title"]

                # 2) Get TOP TAGS using videos ordered by view count
                tags = rank_tags_from_query(query, max_results=25, order="viewCount")

                # Create a single string of the top 20 tags for easy copy
                if tags:
                    top_tags = tags[:20]
                    tags_text = ", ".join(t["tag"] for t in top_tags)

            except Exception as e:
                error_message = str(e)
                print("Error:", e)

    return render_template(
        "index.html",
        tags=tags,
        viral_videos=viral_videos,
        suggested_title=suggested_title,
        tags_text=tags_text,
        query=query,
        error_message=error_message,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)