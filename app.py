from flask import Flask, render_template, request, redirect, send_file, url_for, session
from amazon_product import get_amazon_product_details as ap
import json
import os
import threading
import time
from datetime import datetime
import pandas as pd
import zipfile

app = Flask(__name__)

DATA_FILES = {
    'amazon': 'scraped_data_amazon.json'
}


# ------------------- Persistent Storage -------------------

def load_data(site):
    if os.path.exists(DATA_FILES[site]):
        with open(DATA_FILES[site], 'r') as f:
            return json.load(f)
    return {}

def save_data(data, site):
    with open(DATA_FILES[site], 'w') as f:
        json.dump(data, f, indent=4)

scraped_data = {
    'amazon': load_data('amazon')
}

# ------------------- Background Continuous Scraper -------------------
def continuous_scraper(amazon_id, timer):
    while True:
        now = datetime.now()
        timestamp_date = now.strftime("%Y-%m-%d")
        timestamp_time = now.strftime("%H:%M")

        scrape, _ = ap(amazon_id)
        entry = {
            "date": timestamp_date,
            "time": timestamp_time,
            "price": scrape.get("price"),
            "rating": scrape.get("rating")
        }
        if amazon_id not in scraped_data['amazon']:
            scraped_data['amazon'][amazon_id] = {
                "history": [],
                "title": scrape.get("title", "")
            }
        scraped_data['amazon'][amazon_id]["history"].append(entry)
        save_data(scraped_data['amazon'], 'amazon')

        save_to_excel()
        time.sleep(timer * 60)

# ----------------- Save to Excel ------------------
def save_to_excel():
    site = 'amazon'
    json_file = DATA_FILES[site]

    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)

        for amazon_id, pdata in data.items():
            records = []
            for entry in pdata.get("history", []):
                records.append({
                    "product_id": amazon_id,
                    "title": pdata.get("title", ""),
                    "date": entry.get("date", ""),
                    "time": entry.get("time", ""),
                    "price": entry.get("price", ""),
                })

            if records:
                df = pd.DataFrame(records)
                file_path = f"{amazon_id}_data_amazon.xlsx"
                df.to_excel(file_path, index=False)

# ------------------- Controller -------------------
def choose_amazon_product(amazon_id, timer):
    now = datetime.now()
    timestamp_date = now.strftime("%Y-%m-%d")
    timestamp_time = now.strftime("%H:%M")

    if amazon_id not in scraped_data['amazon']:
        scrap, _ = ap(amazon_id)
        scraped_data['amazon'][amazon_id] = {
            "history": [{
                "date": timestamp_date,
                "time": timestamp_time,
                "price": scrap.get("price"),
            }],
            "title": scrap.get("title", ""),
            "rating": scrap.get("rating"),
            "img": scrap.get("img")
        }
        save_data(scraped_data['amazon'], 'amazon')

    thread = threading.Thread(target=continuous_scraper, args=(amazon_id, int(timer)), daemon=True)
    thread.start()

# ------------------- Routes -------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    amazon_id = request.args.get('amazon_id')
    timer = request.args.get('count') or 1
    amazon_data = {}

    if request.method == 'POST':
        amazon_id = request.form.get('amazon_id')
        timer = request.form.get('Minutes') or 1

        amazon_ids = [aid.strip() for aid in amazon_id.split(',') if aid.strip()]
        for aid in amazon_ids:
            choose_amazon_product(aid, timer)

        return redirect(f"/?amazon_id={amazon_id}&count={timer}")

    if amazon_id:
        amazon_ids = [aid.strip() for aid in amazon_id.split(',') if aid.strip()]
        for aid in amazon_ids:
            amazon_data[aid] = scraped_data['amazon'].get(aid)

    return render_template('file.html',
                           amazon_data=amazon_data,
                           amazon_id=amazon_id)


@app.route('/download_excel')
def download_excel():
    save_to_excel()

    zip_filename = 'amazon_excel_files.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for pid in scraped_data['amazon']:
            excel_file = f"{pid}_data_amazon.xlsx"
            if os.path.exists(excel_file):
                zipf.write(excel_file)

    return send_file(zip_filename, as_attachment=True)


@app.route('/redirect_main_page')
def redirect_main_page():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
