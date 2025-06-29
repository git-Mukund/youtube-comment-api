from flask import Flask, request, jsonify
from flask_cors import CORS
from googleapiclient.discovery import build
from textblob import TextBlob

app = Flask(__name__)
CORS(app)

API_KEY = "AIzaSyAEwAVFyDOpmev9V4rz_TWaK9WQGGvwycQ"

def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("/")[-1]
    return None

def get_comments(video_id):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )
    response = request.execute()
    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)
    return comments

def analyze_comments(comments):
    result = {"positive": 0, "neutral": 0, "negative": 0}
    for c in comments:
        sentiment = TextBlob(c).sentiment.polarity
        if sentiment > 0.1:
            result["positive"] += 1
        elif sentiment < -0.1:
            result["negative"] += 1
        else:
            result["neutral"] += 1
    return result

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    video_url = data.get("url")
    video_id = extract_video_id(video_url)
    comments = get_comments(video_id)
    sentiments = analyze_comments(comments)
    return jsonify(sentiments)

if __name__ == '__main__':
    app.run()
