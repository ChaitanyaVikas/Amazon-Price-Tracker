import requests
from bs4 import BeautifulSoup
import datetime
import csv
import time

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# The Product URL you want to track (Example: A Sony Headphone)
# You can replace this with ANY Amazon product link
URL = 'https://www.amazon.in/Sony-WH-1000XM5-Cancelling-Headphones-Connectivity/dp/B09XS7JWHH'

# The "ID Card" for our script. This makes Amazon think we are a browser.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_product_info(url):
    """
    Fetches the Amazon page and extracts Title and Price.
    """
    try:
        # 1. SEND REQUEST
        page = requests.get(url, headers=HEADERS)
        
        # Check if Amazon blocked us
        if page.status_code != 200:
            print(f"❌ Error: Amazon returned status code {page.status_code}")
            return None

        # 2. PARSE HTML
        soup = BeautifulSoup(page.content, "html.parser")

        # 3. EXTRACT TITLE
        # Amazon usually puts the title in a span with id="productTitle"
        title = soup.find(id='productTitle').get_text().strip()

        # 4. EXTRACT PRICE
        # Price is tricky. It's usually in a class like "a-price-whole"
        # We try a few common price locations
        price_whole = soup.find(class_='a-price-whole')
        
        if price_whole:
            # Get text and remove commas (e.g., "24,000" -> "24000")
            current_price = price_whole.get_text().replace(',', '').replace('.', '').strip()
            current_price = float(current_price)
        else:
            print("⚠️ Could not find price tag. Amazon might have changed the layout.")
            current_price = 0.0

        # 5. GET TIMESTAMP
        timestamp = datetime.datetime.now()

        print(f"✅ Found: {title[0:20]}...")
        print(f"💰 Price: ₹{current_price}")
        
        return [title, current_price, timestamp]

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None

def save_to_csv(data):
    """
    Appends the data to a CSV file (our database for now).
    """
    if data is None:
        return

    filename = 'price_history.csv'
    
    # Open file in 'append' mode ('a')
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the data [Title, Price, Date]
        writer.writerow(data)
    
    print(f"💾 Saved to {filename}")

# ---------------------------------------------------------
# ---------------------------------------------------------
# MAIN EXECUTION (CLOUD READY)
# ---------------------------------------------------------
if __name__ == "__main__":
    # 1. Setup DB
    init_db()
    
    # 2. Run Once
    print("🤖 Cloud Bot Checking Prices...")
    data = get_product_info(URL)
    
    if data:
        save_to_db(data[0], data[1])
        print("✅ Job Done.")
    else:
        print("❌ No data found or blocked.")