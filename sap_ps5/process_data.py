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

    for i in range(n):
        prices_in_inr.append(round(exchange_rates[i]*min_values[i],2))
    country_price_inr={}
    for i in range(n):
        country_price_inr[countries[i]]=prices_in_inr[i]
    formated_country_price_inr = dict(sorted(country_price_inr.items(), key=lambda item: item[1]))
    formated_country_price_inr
    formatted_sentences = []

    for country, price in formated_country_price_inr.items():
        formatted_sentence = f"{country}=₹{price}"
        
        formatted_sentences.append(formatted_sentence)
    result_sentence = ", ".join(formatted_sentences)
    return country_price_inr,result_sentence

def vendor_details(country,prices,vendors,ratings):
    indx=countries.index(country)
    cp=prices[indx]
    p=prices[indx]
    max_value = max(cp)
    threshold = 0.6 * max_value
    ratings=ratings[indx]
    cp = [x for x in cp if x > threshold]
    ratings=[float(ratings[x]) for x in range(len(ratings)) if p[x] in cp]
    cp = [x for x in cp if x > threshold]
    vendors=vendors[indx]
    mi = min(cp)
    ma = max(cp)
    print(cp,ratings)
    scores = []
    for i in range(len(cp)):
        if cp[i] == mi:
            score = -1000000000000000000000000 # Avoid division by zero
        else:
            score = round(abs(ratings[i] / ((cp[i] - mi) / mi-ma)), 2)
        scores.append(score)
    # Step 3: Assign random vendor names
    
    vendors = [{'vendor': vendors[i], 'score': scores[i], 'price': cp[i], 'rating': ratings[i]} for i in range(len(cp))]
    vendors_sorted = sorted(vendors, key=lambda x: x['score'], reverse=True)
    vendor_detail = ", ".join([f"{vendor['vendor']}=({vendor['score']},{vendor['price']},{vendor['rating']})" for vendor in vendors_sorted])
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

    html_table_with_colors = ''
    for i, row in enumerate(html_table.split('<tr>')[1:]):
        color = row_colors[i]
        if i == 0:
            html_table_with_colors += f'<tr>{row}'
        else:
            html_table_with_colors += f'<tr style="background-color: {color};">{row}'
    return html_table_with_colors


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


def generate_graph(prices):
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