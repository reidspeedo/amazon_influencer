import csv
import tkinter as tk
import json
from tkinter import messagebox
from config import load_config
from scraping import scrape_amazon

def scrape_button_click(keyword, search_history_text, page, min_reviews, min_price, max_price, min_ratings):
    # Update search history
    config = load_config()
    search_history = config.get('search_history', [])
    search_history.append(keyword)
    config['search_history'] = search_history
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)
    update_search_history(search_history_text, search_history)

    api_key = config['api_key']

    results = scrape_amazon(keyword, api_key, page, min_reviews, min_price, max_price, min_ratings)

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

    # Configure root window properties
    root.geometry("600x400")
    root.configure(bg="#F0F0F0")

    # Load config values
    config = load_config()
    keyword_value = config.get('keyword', '')
    search_history = config.get('search_history', [])
    page_value = config.get('page', '')
    min_reviews_value = config.get('min_reviews', '')
    min_price_value = config.get('min_price', '')
    max_price_value = config.get('max_price', '')
    min_ratings_value = config.get('min_ratings', '')

    # Create main frame
    main_frame = tk.Frame(root, bg="#F0F0F0")
    main_frame.pack(pady=20, padx=40, anchor="w")
    # Create menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Create File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)
    file_menu.add_command(label='Edit Configuration', command=edit_configuration)

    # Create keyword label and input field
    keyword_label = tk.Label(main_frame, text="Keyword:", bg="#F0F0F0", font=("Arial", 14), fg="#333333")
    keyword_label.grid(row=0, column=0, sticky="w")

    keyword_entry = tk.Entry(main_frame, font=("Arial", 12))
    keyword_entry.insert(0, keyword_value)
    keyword_entry.grid(row=0, column=1, padx=10)

    # Create page number label and input field
    page_label = tk.Label(main_frame, text="Page Number:", bg="#F0F0F0", font=("Arial", 14), fg="#333333")
    page_label.grid(row=1, column=0, sticky="w")

    page_entry = tk.Entry(main_frame, font=("Arial", 12))
    page_entry.insert(0, page_value)
    page_entry.grid(row=1, column=1, padx=10)

    # Create minimum reviews label and input field
    min_reviews_label = tk.Label(main_frame, text="Minimum Reviews:", bg="#F0F0F0", font=("Arial", 14), fg="#333333")
    min_reviews_label.grid(row=2, column=0, sticky="w")

    min_reviews_entry = tk.Entry(main_frame, font=("Arial", 12))
    min_reviews_entry.insert(0, min_reviews_value)
    min_reviews_entry.grid(row=2, column=1, padx=10)

    # Create price range labels and input fields
    price_label = tk.Label(main_frame, text="Price Range:", bg="#F0F0F0", font=("Arial", 14), fg="#333333")
    price_label.grid(row=3, column=0, sticky="w")

    min_price_entry = tk.Entry(main_frame, font=("Arial", 12))
    min_price_entry.insert(0, min_price_value)
    min_price_entry.grid(row=3, column=1, padx=10)

    max_price_entry = tk.Entry(main_frame, font=("Arial", 12))
    max_price_entry.insert(0, max_price_value)
    max_price_entry.grid(row=3, column=2, padx=10)

    # Create minimum ratings label and input field
    min_ratings_label = tk.Label(main_frame, text="Minimum Ratings:", bg="#F0F0F0", font=("Arial", 14), fg="#333333")
    min_ratings_label.grid(row=4, column=0, sticky="w")

    min_ratings_entry = tk.Entry(main_frame, font=("Arial", 12))
    min_ratings_entry.insert(0, min_ratings_value)
    min_ratings_entry.grid(row=4, column=1, padx=10)

    # Create scrape button
    scrape_button = tk.Button(root, text="Scrape Amazon",
                              command=lambda: scrape_button_click(keyword_entry.get(), search_history_text,
                                                                 int(page_entry.get()), int(min_reviews_entry.get()),
                                                                 float(min_price_entry.get()), float(max_price_entry.get()),
                                                                 float(min_ratings_entry.get())))
    scrape_button.pack(pady=10)

    # Save configuration button
    save_button = tk.Button(root, text="Save Parameters", command=lambda: save_parameters(page_entry.get(), min_reviews_entry.get(),
                                                                                          min_price_entry.get(), max_price_entry.get(),
                                                                                          min_ratings_entry.get()))
    save_button.pack(pady=10)


    # Create search history label and text widget
    search_history_label = tk.Label(root, text="Search History:", bg="#F0F0F0", font=("Arial", 14), fg="#333333")
    search_history_label.pack(anchor="w")

    search_history_text = tk.Text(root, height=5, width=50, font=("Arial", 12))
    search_history_text.pack(anchor="w")

    update_search_history(search_history_text, search_history)
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
    csv_file_label = tk.Label(top, text="CSV File:", bg="#F0F0F0", font=("Arial", 14), fg="#333333")
    csv_file_label.pack()

    csv_file_entry = tk.Entry(top, font=("Arial", 12))
    csv_file_entry.insert(0, csv_file_value)
    csv_file_entry.pack()

    # Create api key label and input field
    api_key_label = tk.Label(top, text="API Key:", bg="#F0F0F0", font=("Arial", 14), fg="#333333")
    api_key_label.pack()

    api_key_entry = tk.Entry(top, font=("Arial", 12))
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

    messagebox.showinfo('Configuration Saved', 'Configuration has been saved.')

def save_parameters(page, min_reviews, min_price, max_price, min_ratings):
    config = load_config()
    config['page'] = page
    config['min_reviews'] = min_reviews
    config['min_price'] = min_price
    config['max_price'] = max_price
    config['min_ratings'] = min_ratings
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

    messagebox.showinfo('Parameters Saved', 'Parameters has been saved.')