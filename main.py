import os
import smtplib
import threading
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import schedule
from exa_py import Exa
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

# Sumy imports
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

# ---------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TOPIC = os.getenv("TOPICS").split(",")  # supports multiple topics
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME")  # e.g. "08:00"
EXA_API_KEY = os.getenv("EXA_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------
DAYS_BACK = 1  # Number of days back to fetch news (e.g., 1 for yesterday)
SUMMARY_SENTENCES = 3  # Number of sentences for article summary

# ---------------------------------------------------------------------
# Initialize FastAPI app
# ---------------------------------------------------------------------
app = FastAPI(title="News Scraper API", description="Daily News Email Scheduler")

# ---------------------------------------------------------------------
# MongoDB setup
# ---------------------------------------------------------------------
client = MongoClient(MONGO_URI)
db = client["news_db"]
collection = db["subscribers"]

# ---------------------------------------------------------------------
# Initialize Exa API client
# ---------------------------------------------------------------------
exa = Exa(api_key=EXA_API_KEY)

# ---------------------------------------------------------------------
# Pydantic model for email input
# ---------------------------------------------------------------------
class Subscriber(BaseModel):
    email: str

# ---------------------------------------------------------------------
# Fetch news using Exa API
# ---------------------------------------------------------------------
def summarize_article(text):
    """Summarize the article text using Sumy LexRank"""
    try:
        if not text.strip():
            return "No summary available."
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        summary = summarizer(parser.document, SUMMARY_SENTENCES)
        summarized_text = " ".join(str(sentence) for sentence in summary)
        return summarized_text if summarized_text else text[:300] + "..."
    except Exception as e:
        print(f"Error summarizing article: {e}")
        return text[:300] + "..."


def fetch_news():
    """Fetch news using Exa API for each topic"""
    target_date = datetime.now() - timedelta(days=DAYS_BACK)
    day_start = target_date.replace(hour=0, minute=0, second=0)
    day_end = target_date.replace(hour=23, minute=59, second=59)

    start_date = day_start.isoformat() + "Z"
    end_date = day_end.isoformat() + "Z"

    all_articles = []

    for topic in TOPIC:
        try:
            result = exa.search_and_contents(
                topic,
                type="keyword",
                user_location="IN",
                start_published_date=start_date,
                end_published_date=end_date,
                num_results=5,
                text={"include_html_tags": True},
            )

            for article in result.results:
                summary = summarize_article(getattr(article, 'text', ""))
                all_articles.append({
                    "title": getattr(article, 'title', "No Title"),
                    "url": getattr(article, 'url', "#"),
                    "summary": summary,
                    "topic": topic,
                })

        except Exception as e:
            print(f"Error fetching {topic}: {e}")

    return all_articles
# ---------------------------------------------------------------------
# Send email function
# ---------------------------------------------------------------------
def send_news_email():
    emails = [doc["email"] for doc in collection.find({})]
    if not emails:
        print("⚠️ No subscribers to send emails.")
        return

    news_list = fetch_news()
    if not news_list:
        print("⚠️ No news found for yesterday.")
        return

    topic_str = ", ".join([t.strip().capitalize() for t in TOPIC])
    body = ""
    for idx, article in enumerate(news_list, start=1):
        body += f"{idx}. {article['title']}\n{article['url']}\n\n"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)

        for email in emails:
            msg = MIMEMultipart()
            msg["From"] = EMAIL_USER
            msg["To"] = email
            msg["Subject"] = f"Yesterday's News on {topic_str} - {datetime.now().strftime('%d %b %Y')}"
            msg.attach(MIMEText(body, "plain"))
            server.sendmail(EMAIL_USER, email, msg.as_string())

        server.quit()
        print(f"✅ Emails sent successfully to {len(emails)} subscribers!")

    except Exception as e:
        print("❌ Failed to send email:", e)

# ---------------------------------------------------------------------
# Scheduler setup
# ---------------------------------------------------------------------
def run_schedule():
    schedule.every().day.at(SCHEDULE_TIME).do(send_news_email)
    print(f"🕒 Scheduler started! Emails will be sent daily at {SCHEDULE_TIME}")

    while True:
        schedule.run_pending()
        time.sleep(60)

# Run scheduler on FastAPI startup
@app.on_event("startup")
def start_scheduler():
    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()

# ---------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "✅ News Scraper API is running!",
        "schedule_time": SCHEDULE_TIME,
        "topics": TOPIC,
    }

@app.post("/subscribe")
def subscribe_user(subscriber: Subscriber):
    email = subscriber.email.strip().lower()
    if collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already subscribed.")

    collection.insert_one({"email": email, "subscribed_on": datetime.now()})
    return {"message": f"✅ {email} successfully subscribed!"}

@app.post("/unsubscribe")
def unsubscribe_user(subscriber: Subscriber):
    email = subscriber.email.strip().lower()
    result = collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Email not found in subscribers.")

    return {"message": f"✅ {email} successfully unsubscribed!"}
