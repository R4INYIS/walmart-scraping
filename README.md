## 🛒 Walmart web scraper - Discount Monitor

This project is a bot designed to monitor product discounts on [Walmart México](https://www.walmart.com.mx). It scrapes product listings from specific categories and checks for discounts greater than 40%. When such deals are found, it sends the product information to a private Telegram channel. The bot runs continuously and is designed to avoid detection.

---

### 📦 Features

* Stealthy web scraping with undetected Chrome driver.
* Automatically checks prices and calculates discount percentages.
* Sends new deals to a Telegram channel.
* Refreshes periodically to detect new discounts.
* Handles pagination and multiple category URLs.

---

### ✅ Requirements

* Python 3.8+
* Google Chrome
* Chromedriver (compatible with your Chrome version)

#### Python Libraries

Install the required libraries using:

```bash
pip install requests beautifulsoup4 python-dotenv undetected-chromedriver pytz
```

---

### ⚙️ Setup

1. **Clone the repository:**

```bash
git clone https://github.com/R4INYIS/walmart-scraping/
cd walmart-discount-monitor
```

2. **Create a `.env` file** in the root directory with your Telegram bot credentials:

```
TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
```

3. **Prepare the input file:**

Create a `url.csv` file containing the product category URLs you want to monitor. Each row should follow this format:

```
https://www.walmart.com.mx/categoria?some-query-params|
```

---

### ▶️ How to Run

To start the bot, simply run:

```bash
python main.py
```

The script will:

* Load all URLs from `url.csv`
* Scrape products from each page
* Identify products with >40% discount
* Send them to the specified Telegram chat
* Wait and repeat based on the interval defined in the script (`SCRAPING_TIME`)

---

### 📝 Notes

* The script uses randomized sleep times and batch sending to avoid rate limiting or detection.
* Make sure Chrome and Chromedriver are installed and compatible.
* This bot is intended for educational or personal use—respect site terms of service.

---

