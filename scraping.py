import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from tqdm import tqdm

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
