import csv
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import json
import tkinter as tk
from tkinter import messagebox

def load_config():
    with open('config.json') as config_file:
        config = json.load(config_file)
    return config

def scrape_amazon(keyword, api_key):
    results = []
    for page in tqdm(range(1, 2), desc='Scraping Pages'):
        search_url = f"https://www.amazon.com/s?k={quote(keyword)}&rh=n%3A283155%2Cp_72%3A1250221011%2Cp_n_feature_browse-bin%3A2656022011&dc&{page}&crid=1H2GLYJD7OZRC&qid=1684906776&rnid=618072011&sprefix=scifi+book%2Cstripbooks%2C149&ref=sr_pg_2"
        response = requests.get(get_url(search_url, api_key))
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.select('[data-asin]')

        for product in products:
            asin = product['data-asin']
            if asin:
                product_url = f"https://www.amazon.com/dp/{asin}"
                name = get_product_name(product)
                price, num_ratings, rating = get_product_details(product)
                criteria_match = check_criteria(price, num_ratings, rating)
                results.append({
                    'asin': asin,
                    'product_url': product_url,
                    'name': name,
                    'price': price,
                    'num_ratings': num_ratings,
                    'rating': rating,
                    'criteria_match': criteria_match
                })

    return results

def get_product_name(product):
    name_element = product.select_one('.a-link-normal .a-size-base-plus')
    return name_element.get_text(strip=True) if name_element else 'N/A'

def get_product_details(product):
    price = product.select_one('.a-price-whole')
    price = price.get_text(strip=True) if price else 'N/A'

    num_ratings = product.select_one('div.a-row.a-size-small span.a-size-base.s-underline-text').text
    num_ratings = num_ratings if num_ratings else 'N/A'

    rating = product.select_one('.a-icon-star-small .a-icon-alt')
    rating = rating.get_text(strip=True) if rating else 'N/A'

    return price, num_ratings, rating

def check_criteria(price, num_ratings, rating):
    try:
        price_float = float(price.replace('$', '').replace(',', ''))
        num_ratings_int = int(num_ratings.replace(',', ''))
        rating_float = float(rating.split()[0])
        if price_float > 8 and num_ratings_int > 10000 and rating_float > 4:
            return 'Yes'
        else:
            return 'No'
    except ValueError:
        return 'No'

def get_url(url, api_key):
    payload = {'api_key': api_key, 'url': url}
    return f"http://api.scraperapi.com/?{requests.compat.urlencode(payload)}"

def scrape_button_click():
    config = load_config()
    keyword = config['keyword']
    api_key = config['api_key']

    results = scrape_amazon(keyword, api_key)

    messagebox.showinfo('Scraping Completed', f"Number of results: {len(results)}")

    csv_file = config['csv_file']
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    messagebox.showinfo('Results Saved', f"Results saved to {csv_file}")


def scrape_button_click(keyword, search_history_text):
    # Update search history
    config = load_config()
    search_history = config.get('search_history', [])
    search_history.append(keyword)
    config['search_history'] = search_history
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)
    update_search_history(search_history_text, search_history)

    api_key = config['api_key']

    results = scrape_amazon(keyword, api_key)

    messagebox.showinfo('Scraping Completed', f"Number of results: {len(results)}")

    csv_file = config['csv_file']
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    messagebox.showinfo('Results Saved', f"Results saved to {csv_file}")


def main():
    root = tk.Tk()
    root.title("Amazon Scraper")

    # Load config values
    config = load_config()
    keyword_value = config.get('keyword', '')
    search_history = config.get('search_history', [])

    # Create keyword entry label and input field
    keyword_label = tk.Label(root, text="Keyword:")
    keyword_label.pack()

    keyword_entry = tk.Entry(root)
    keyword_entry.insert(0, keyword_value)
    keyword_entry.pack()

    # Create search history label and text widget
    search_history_label = tk.Label(root, text="Search History:")
    search_history_label.pack()

    search_history_text = tk.Text(root, height=5, width=30)
    search_history_text.pack()

    update_search_history(search_history_text, search_history)

    # Create menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Create Configuration menu
    config_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Configuration', menu=config_menu)
    config_menu.add_command(label='Edit Configuration', command=edit_configuration)

    # Create scrape button
    scrape_button = tk.Button(root, text="Scrape Amazon", command=lambda: scrape_button_click(keyword_entry.get(), search_history_text))
    scrape_button.pack(pady=10)

    root.mainloop()

def update_search_history(search_history_text, search_history):
    search_history_text.delete(1.0, tk.END)
    for keyword in search_history:
        search_history_text.insert(tk.END, keyword + '\n')

def edit_configuration():
    top = tk.Toplevel()
    top.title("Edit Configuration")

    # Load config values
    config = load_config()
    csv_file_value = config.get('csv_file', '')
    api_key_value = config.get('api_key', '')

    # Create csv file label and input field
    csv_file_label = tk.Label(top, text="CSV File:")
    csv_file_label.pack()

    csv_file_entry = tk.Entry(top)
    csv_file_entry.insert(0, csv_file_value)
    csv_file_entry.pack()

    # Create api key label and input field
    api_key_label = tk.Label(top, text="API Key:")
    api_key_label.pack()

    api_key_entry = tk.Entry(top)
    api_key_entry.insert(0, api_key_value)
    api_key_entry.pack()

    # Save configuration button
    save_button = tk.Button(top, text="Save Configuration", command=lambda: save_configuration(csv_file_entry.get(), api_key_entry.get()))
    save_button.pack(pady=10)

def save_configuration(csv_file, api_key):
    config = load_config()
    config['csv_file'] = csv_file
    config['api_key'] = api_key
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)



if __name__ == '__main__':
    main()
