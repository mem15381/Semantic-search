from flask import Flask
import praw
import config

app = Flask(__name__)

@app.route('/') 
def index():
    reddit = praw.Reddit(client_id=config.client_id, client_secret=config.client_secret, user_agent="...")
    reddit_data = []

    for submission in reddit.subreddit('worldnews').controversial(limit=10):
        reddit_data.append(submission.title)

    return render_template("show_reddit.html", data=reddit_data)

if __name__ == "__main__":
    app.run(debug=True)