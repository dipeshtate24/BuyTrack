from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def get_amazon_product_details(product_id):
    # Set Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")

    # Set ChromeDriver path (update this)
    service = Service(executable_path="/chromedriver-win64"
                                      "/chromedriver-win64/chromedriver.exe")  # <-- CHANGE THIS
    driver = webdriver.Chrome(service=service, options=options)

    url = f"https://www.amazon.in/dp/{product_id}"

    def scrape():
        try:
            # Wait for product title to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "productTitle"))
            )

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            title_tag = soup.find(id='productTitle')
            price_tag = soup.find(class_='a-price-whole')
            rating_tag = soup.find('span', {'class': 'a-icon-alt'})
            img_tag = soup.find(id='imgTagWrapperId')


            title = title_tag.get_text(strip=True) if title_tag else 'Title not found'
            price = price_tag.get_text(strip=True) if price_tag else 'Price not found'
            rating = rating_tag.get_text(strip=True) if rating_tag else 'Rating not found'
            img = img_tag.img['src'] if img_tag and img_tag.img else 'Image not found'

            return {
                'title': title,
                'price': f"₹ {price}",
                'rating': rating,
                'img': img

            }

        except Exception as e:
            return {'error': str(e)}

    try:
        # First scrape
        driver.get(url)
        # print("Scraping first time...")
        first_scrape = scrape()

        # print("\nFirst Scrape Result:")
        # for k, v in first_scrape.items():
        #     print(f"{k.title()}: {v}")

        # Wait 15 minutes
        # print("\nWaiting for 15 minutes before refresh...\n")
        # time.sleep(60)

        # Refresh and scrape again
        # print("Refreshing and scraping again...")
        driver.refresh()
        second_scrape = scrape()

        # print("\nSecond Scrape Result:")
        # for k, v in second_scrape.items():
        #     print(f"{k.title()}: {v}")
        return first_scrape, second_scrape

    finally:
        driver.quit()

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     data = None
#     if request.method == 'POST':
#         product_id = request.form['product_id']
#         data = get_amazon_product_details(product_id)
#     # return render_template('index.html', data=data)
#
# if __name__ == '__main__':
#     app.run(debug=True)
