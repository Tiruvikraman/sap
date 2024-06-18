import easyocr
import threading
import requests
from bs4 import BeautifulSoup
import io
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import random
countries=['Australia', 'Canada', 'China', 'France', 'Indonesia', 'Japan', 'Singapore', 'Thailand', 'United Kingdom', 'United States', 'India']
def get_currency_conversion(min_values,exchange_rates):
    
    prices_in_inr=[]
    n=len(countries)
    print(min_values,exchange_rates)
    min_values = [10000000 if x is None else x for x in min_values]
    print(min_values,exchange_rates)

    for i in range(n):

        prices_in_inr.append(round(exchange_rates[i]*min_values[i],1))
    country_price_inr={}
    for i in range(n):
        country_price_inr[countries[i]]=prices_in_inr[i]
    country_price_crt=list(country_price_inr.values())
    country_price_inr = dict(sorted(country_price_inr.items(), key=lambda item: item[1]))
    
    formatted_sentences = []

    for country, price in country_price_inr.items():
        formatted_sentence = f"{country}=₹{price}"
        
        formatted_sentences.append(formatted_sentence)
    result_sentence = ", ".join(formatted_sentences)
    print(result_sentence,country_price_inr,min_values)
    return country_price_inr,result_sentence,country_price_crt

def vendor_details(country,prices,vendors,ratings,currency_symbol):
    indx=countries.index(country)
    cp=prices[indx]
    p=prices[indx]
    max_value = max(cp)
    threshold = 0.6 * max_value
    ratings=ratings[indx]
    cp = [x for x in p if x > threshold]
    ratings=[float(ratings[x]) for x in range(len(ratings)) if p[x] in cp]
    vendors=vendors[indx]
    vendors=[vendors[x] for x in range(len(vendors)) if p[x] in cp]
    mi = min(cp)
    ma = max(cp)
    print(cp,ratings)
    scores = []
    for i in range(len(cp)):
        if len(cp)==1:
            score=10
        elif cp[i] == mi:
            score = -1000000000000000000000000 # Avoid division by zero
        else:
            score = round(abs(ratings[i] / ((cp[i] - mi) / mi-ma)), 2)
        scores.append(score)
    # Step 3: Assign random vendor names
    
    vendors = [{'vendor': vendors[i], 'score': scores[i], 'price': cp[i], 'rating': ratings[i]} for i in range(len(ratings))]
    vendors_sorted = sorted(vendors, key=lambda x: x['score'], reverse=True)
    vendor_detail = ", ".join([f"{vendor['vendor']}=({vendor['score']},{currency_symbol}{vendor['price']},{vendor['rating']})" for vendor in vendors_sorted])
    print(scores,vendors_sorted,cp,ratings)
    return vendor_detail

def exchange_table():
    exchange_rates = [55.1742, 60.6763, 11.5151, 89.2615, 0.0051, 0.5309, 61.6895, 2.2747, 105.8887, 83.5447, 1.0]
    price_changes = [round(random.uniform(-5, 5), 2) for _ in countries]

    data = {
        "Country": countries,
        "Exchange Rate": exchange_rates,
        "Price Change (%)": price_changes
    }

    df = pd.DataFrame(data)

    def add_arrows_and_color(price_change):
        color = 'rgba(0, 255, 0, .3)' if price_change > 0 else 'rgba(255, 0, 0, .3)'
        arrow = '▲' if price_change > 0 else '▼'
        return f'<span style="color: {"green" if price_change > 0 else "red"};">{arrow} {abs(price_change)}%</span>', color

    df['Price Change (%)'], row_colors = zip(*df['Price Change (%)'].apply(add_arrows_and_color))

    html_table = df.to_html(escape=False, index=False)
    html_table_with_styles = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        td:nth-child(1) {
            width: 30%;
        }
        td:nth-child(2) {
            width: 40%;
        }
        td:nth-child(3) {
            width: 30%;
        }
    </style>
    <table>
    """

    html_table_with_colors = ''
    for i, row in enumerate(html_table.split('<tr>')[1:]):
        color = row_colors[i]
        if i == 0:
            html_table_with_colors += f'<tr>{row}'
        else:
            html_table_with_colors += f'<tr style="background-color: {color};">{row}'
    return html_table_with_styles + html_table_with_colors + '</table>'

def generate_map(product_prices):

    country_coords = {
        "USA": [37.0902, -95.7129],
        "UK": [55.3781, -3.4360],
        "Germany": [51.1657, 10.4515],
        "France": [46.6034, 1.8883],
        "Canada": [56.1304, -106.3468],
        "Singapore": [1.3521, 103.8198],
        "China": [35.8617, 104.1954],
        "Japan": [36.2048, 138.2529],
        "Thailand": [15.8700, 100.9925],
        "Indonesia": [-0.7893, 113.9213]
    }
    sorted_prices = sorted(product_prices.items(), key=lambda x: x[1])
    top_5_countries = sorted_prices[:5]

    m = folium.Map(location=[20, 0], zoom_start=2)
    marker_cluster = MarkerCluster().add_to(m)

    for country, price in top_5_countries:
        folium.Marker(
            location=country_coords[country],
            popup=f'{country}: {price} INR',
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)

    return m._repr_html_()


def generate_graph(prices,recommendation_generated):
    if not recommendation_generated:
        return "Recommendation not generated yet", 400
    plt.figure(figsize=(10, 6))
    colors = sns.color_palette("RdYlGn_r", len(countries))
    barplot = sns.barplot(x=countries, y=prices, palette=colors)
    
    for index, value in enumerate(prices):
        plt.text(index, value + 0.2, str(value), ha='center', va='bottom')
    
    ax = plt.gca()
    normalize = plt.Normalize(vmin=min(prices), vmax=max(prices))
    sm = plt.cm.ScalarMappable(cmap='RdYlGn_r', norm=normalize)
    sm.set_array([])
    plt.gcf().patch.set_facecolor((1.0, 1.0, 1.0, 0.8))
    cbar = plt.colorbar(sm, ax=ax, extend='both')
    cbar.set_label('Price')
    cbar.ax.text(0.5, 1.1, 'High', transform=cbar.ax.transAxes, ha='center', va='center', fontsize=10)
    cbar.ax.text(0.5, -0.1, 'Low', transform=cbar.ax.transAxes, ha='center', va='center', fontsize=10)
    plt.xlabel('Countries')
    plt.ylabel('Price')
    plt.title('Prices in Different Countries')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf


def process_upload_bill(exchange_rates,invoice_dict):
    urls = []

    country_codes = ['AU', 'CA', 'CN', 'FR', 'ID', 'JP', 'SG', 'TH', 'UK', 'US', 'IN']
    search_terms = list(invoice_dict.keys())

    for search_term in search_terms:
        if search_term=='Total':
            continue
        for country_code in country_codes:
            url = f"https://www.google.com/search?q={search_term.replace(' ', '+')+'+cheap'}&tbm=shop&gl={country_code}&ln=en&tbs=mr:1,new:1,sales:1"
            urls.append(url)
    

    countries = ['Australia', 'Canada', 'China', 'France', 'Indonesia', 'Japan', 'Singapore', 'Thailand', 'United Kingdom', 'United States', 'India']
    country_code = ['AU', 'CA', 'CN', 'FR', 'ID', 'JP', 'SG', 'TH', 'UK', 'US', 'IN']
    cc = {country_code[i]: countries[i] for i in range(len(country_code))}
    # Define the proxy details
    proxy = {
        'http': 'http://192.168.134.40:5000',
        'https': 'http://192.168.134.40:5000'
    }
    def scrap_price(urls):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        prices = {}

        def web_scrap(url):
            print(url)
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'lxml')
            country = url[url.index('gl=') + len('gl='):url.index('gl=') + len('gl=') + 2]
            product = url[url.index('?q=') + len('?q='):url.index('+cheap&tb')].replace('+', ' ')

            if product not in prices:
                prices[product] = {}

            content_elements = soup.find_all('div', class_='sh-dgr__content')

            if not content_elements:
                prices[product][cc[country]] ='1000000000'
                return

            for content_element in content_elements[0]:
                if content_element.find('span', class_='tD1ls') is None:
                    price_element = content_element.find('span', class_='a8Pemb')
                    if price_element:
                        price = price_element.get_text(strip=True)

            prices[product][cc[country]] = price if price else '1000000000'

        threads = []
        for url in urls:
            thread = threading.Thread(target=web_scrap, args=(url,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        return prices
    a=scrap_price(urls)
    print(a)
    def process_upload_data(data):
        process=[   lambda orig_price:int(orig_price[1:].replace(',','').split('.')[0]) ,
                    lambda orig_price:int(orig_price[2:].replace('\u202f', '').replace('\xa0', '').replace('.','').split(',')[0]),
                    lambda orig_price:int(orig_price[:-1].replace('\u202f', '').replace('\xa0', '').split(',')[0]),
                    lambda orig_price:int(orig_price),
                    ]

        for product, countries in data.items():
            for country, price in countries.items():
                try:
                    if '$' in price:
                        data[product][country] = process[0](price)
                    elif 'Rp' in price:
                        data[product][country] = process[1](price)
                    elif '€' in price:
                        data[product][country] = process[2](price)
                    elif '￥' in price or '฿' in price or '₹' in price or '£' in price:
                        data[product][country] = process[0](price)
                    else:
                        data[product][country] = int(price)
                except ValueError:
                    data[product][country] = price  # retain the original price if conversion fails

        return data

    # Process the data
    processed_data = process_upload_data(a)
    total_prices = {}

    for product, countries in processed_data.items():
        for country, price in countries.items():
            if country in total_prices:
                total_prices[country] += price
            else:
                total_prices[country] = price
    print(total_prices)
    countries=['Australia', 'Canada', 'China', 'France', 'Indonesia', 'Japan', 'Singapore', 'Thailand', 'United Kingdom', 'United States', 'India']

    converted_price_dict = {}
    for country, price in total_prices.items():
        converted_price = price * exchange_rates[countries.index(country)]
        converted_price_dict[country] = round(converted_price,1)
    sorted_converted_price_dict = (dict(sorted(converted_price_dict.items(),key=lambda item: item[1])))
    print(sorted_converted_price_dict)
    min_country = (list(sorted_converted_price_dict.keys()))[1]
    print(min_country)
    d={}
    for i in list(processed_data.keys()):
        d[i]=round(processed_data[i][min_country]*exchange_rates[countries.index(min_country)],1)
    d['Purchase_total']=sum(d.values())
    d['delivery_charge']=round(d['Purchase_total']*.1,1)
    d['Import_tax']=round(d['Purchase_total']*.16,1)
    d['total']=round(d['Purchase_total']+d['delivery_charge']+d['Import_tax'],1)
    return d,search_terms,min_country,invoice_dict['Total'],d['total'],((invoice_dict['Total'] - d['total']) / invoice_dict['Total']) * 100

reader = easyocr.Reader(['en'])

def perform_ocr(image_path):
    try:
        result = reader.readtext(image_path)
        extracted_text = ''
        for (bbox, text, prob) in result:
            extracted_text += text + ' '
        return extracted_text.strip()  # Remove trailing space

    except Exception as e:
        print(f"Error during OCR: {e}")
        return ''