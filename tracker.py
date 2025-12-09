import requests
from bs4 import BeautifulSoup
import datetime
import sqlite3

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# You can change this URL to any product you want to track
URL = 'https://www.amazon.in/Sony-WH-1000XM5-Cancelling-Headphones-Connectivity/dp/B09XS7JWHH'
DB_NAME = 'amazon_prices.db'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# ---------------------------------------------------------
# DATABASE FUNCTIONS
# ---------------------------------------------------------
def init_db():
    """
    Creates the database and the table if they don't exist.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                price REAL,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Database initialized.")
    except Exception as e:
        print(f"❌ Database Error: {e}")

def save_to_db(title, price):
    """
    Inserts a new row into the SQL database.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO prices (title, price, timestamp)
            VALUES (?, ?, ?)
        ''', (title, price, timestamp))
        conn.commit()
        conn.close()
        print(f"💾 Saved to SQL Database: ₹{price} at {timestamp}")
    except Exception as e:
        print(f"❌ Save Error: {e}")

# ---------------------------------------------------------
# SCRAPING FUNCTION
# ---------------------------------------------------------
def get_product_info(url):
    try:
        page = requests.get(url, headers=HEADERS)
        
        # Check if Amazon blocked us
        if page.status_code != 200:
            print(f"❌ Error: Amazon returned status code {page.status_code}")
            return None

        soup = BeautifulSoup(page.content, "html.parser")

        # Extract Title
        title_tag = soup.find(id='productTitle')
        if not title_tag:
            print("⚠️ Could not find product title. Check if the URL is valid.")
            return None
            
        title = title_tag.get_text().strip()

        # Extract Price
        # We try a few different classes because Amazon changes them often
        price_whole = soup.find(class_='a-price-whole')
        if price_whole:
            current_price = float(price_whole.get_text().replace(',', '').replace('.', '').strip())
        else:
            print("⚠️ Could not find price tag.")
            current_price = 0.0

        print(f"🔎 Found: {title[:30]}... | Price: {current_price}")
        return title, current_price

    except Exception as e:
        print(f"❌ Scraping Error: {e}")
        return None

# ---------------------------------------------------------
# MAIN EXECUTION (CLOUD READY)
# ---------------------------------------------------------
if __name__ == "__main__":
    # 1. Initialize the Database
    init_db()
    
    # 2. Run the Scraper
    print("🤖 Cloud Bot Checking Prices...")
    data = get_product_info(URL)
    
    # 3. Save Data if found
    if data:
        save_to_db(data[0], data[1])
        print("✅ Job Done.")
    else:
        print("❌ No data found or blocked.")
