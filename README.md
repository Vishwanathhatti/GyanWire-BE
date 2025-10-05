
---

# 📰 GyanWire News Scraper - Backend

A **FastAPI-based backend** for fetching **India-focused news for competitive exam preparation** and sending **daily email summaries** to subscribers. The backend uses **Exa API** for news retrieval, **Sumy** for text summarization, and **MongoDB** for subscriber management.

---

## ⚡ Features

* Fetch **top Indian current affairs** and **government exam-related news** from Exa API.
* Summarize news articles using **Sumy** NLP library.
* Send **daily email digests** to subscribers at a scheduled time.
* REST API endpoints to **subscribe users**.
* Fully **configurable via environment variables**.
* **Scheduler runs on FastAPI startup** using threading.

---

## 🛠 Tech Stack

* **Backend Framework:** FastAPI
* **Database:** MongoDB
* **Scheduler:** Python `schedule` library
* **Email Sending:** SMTP via Gmail
* **News API:** Exa API
* **Text Summarization:** Sumy library (LexRank or LSA)
* **Environment Variables:** python-dotenv

---

## 🔧 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/Vishwanathhatti/GyanWire-BE.git
cd news-scraper-backend
```

2. **Create a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Create a `.env` file** in the project root:

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_email_password_or_app_password
TOPICS=Government & Policies,Economy & Business,Science, Technology & Innovation,International Relations & Diplomacy,Environment, Ecology & Sustainability
SCHEDULE_TIME=08:00
EXA_API_KEY=your_exa_api_key
MONGO_URI=mongodb://localhost:27017
```

---

## 🚀 Running the Backend

Start the FastAPI backend with Uvicorn:

```bash
uvicorn main:app --reload
```

* API will be available at: `http://127.0.0.1:8000`
* Scheduler automatically starts and sends emails daily at `SCHEDULE_TIME`.

---

## 📚 API Endpoints

### **GET /**

**Description:** Check if backend is running.

**Response:**

```json
{
  "message": "✅ News Scraper API is running!",
  "schedule_time": "08:00",
  "topics": ["Government & Policies", "Economy & Business", "Science, Technology & Innovation", "International Relations & Diplomacy", "Environment, Ecology & Sustainability"]
}
```

---

### **POST /subscribe**

**Description:** Subscribe a user to daily news emails.

**Request Body:**

```json
{
  "email": "student@example.com"
}
```

**Responses:**

* Success:

```json
{
  "message": "✅ student@example.com successfully subscribed!"
}
```

* Error (email already subscribed):

```json
{
  "detail": "Email already subscribed."
}
```

---

### **POST /unsubscribe**

**Description:** Unsubscribe a user from daily news emails.

**Request Body:**

```json
{
  "email": "student@example.com"
}
```

**Responses:**

* Success:

```json
{
  "message": "✅ student@example.com successfully unsubscribed!"
}
```

* Error (email not found):

```json
{
  "detail": "Email not found in subscribers."
}
```

---

## 📌 Scheduler

* Uses Python `schedule` library.
* Runs in a **separate thread** on FastAPI startup.
* Sends daily emails with **news summaries** for the configured topics.
* Summarization powered by **Sumy**.

---

## 🔑 Notes

* Ensure Gmail account allows **Less Secure Apps** or use **App Passwords** for email sending.
* Exa API is **paid**, limit your topics to **5 per subscription**.
* All fetched news is **India-focused** using topic keywords and search queries.

---

## 📝 Folder Structure

```
news-scraper-backend/
│
├─ main.py          # FastAPI app, scheduler, email sending
├─ requirements.txt # Python dependencies
├─ .env             # Environment variables
└─ README.md        # Project documentation
```

---

## ⚙️ Dependencies

Key dependencies:

* fastapi
* uvicorn
* pymongo
* exa-py
* schedule
* python-dotenv
* sumy
* nltk

**Note:** Make sure to download NLTK resources:

```python
import nltk
nltk.download('punkt')
```

---

## 💡 Future Enhancements

* Implement **daily email summaries in HTML format**.
* Add **news categorization** per topic.
* Use **Celery** for more robust scheduling and async email sending.

---

I can also **create a “Usage” section with example code for subscribing users and testing the API** to make it more developer-friendly.

Do you want me to add that too?
