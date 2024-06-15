import threading
import requests
from bs4 import BeautifulSoup
countries=['Australia', 'Canada', 'China', 'France', 'Indonesia', 'Japan', 'Singapore', 'Thailand', 'United Kingdom', 'United States', 'India']
country_code=['AU', 'CA', 'CN', 'FR', 'ID', 'JP', 'SG', 'TH', 'uk', 'US','IN']
cc={}
for i in range(len(country_code)):
    cc[country_code[i]]=countries[i]
print(cc)
def scrap_price(product_name):
    global prices,ratings,vendors,product_links,countries,image_link
    product_full_name = None
    prices = None
    ratings = None
    vendors = None
    product_links = None
    countries = None
    image_link = None
    country_code=['AU', 'CA', 'CN', 'FR', 'ID', 'JP', 'SG', 'TH', 'uk', 'US','IN']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    ratings={}
    vendors={}
    prices={}
    product_links={}
    product_name=product_name
    product_full_name={}
    product=product_name.replace(' ','+')
    def web_scrap(country):
        url = f'https://www.google.com/search?q={product}&tbm=shop&gl={country}&ln=en&tbs=mr:1,new:1'
        print(url)
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')
        try:
            image_link = soup.find('div', class_='SirUVb sh-img__image').find('img')['src']
        except:
            0
        content_elements = soup.find_all('div', class_='sh-dgr__content')
        if content_elements==[]:
                    prices[cc[country]]=(['1000000000','1000000000','1000000000'])
                    vendors[cc[country]]=(['NA','NA','NA'])
                    product_links[cc[country]]=(['NA','NA','NA'])
                    ratings[cc[country]]=([0,0,0])
                    return   
        
        i=0
        orig_price=[]
        vendor1=[]
        product_link=[]
        rating=[]
        for content_element in content_elements:
            if content_element.find('span',class_='tD1ls')==None:
                link_element = content_element.find('a',class_='shntl')
                if link_element:
                    li = link_element['href']
                    li=li[li.index('http'):li.index('&rct=j&q')]
                    product_link.append(li)

                rating_element = content_element.find('span', class_='Rsc7Yb')
                if rating_element:
                    rating_value = rating_element.get_text(strip=True)
                    rating.append(rating_value)

                price_element = content_element.find('span',class_='a8Pemb')
                if price_element:
                    price = price_element.get_text(strip=True)
                    orig_price.append(price)
                    
                vendor = content_element.find('div',class_='aULzUe IuHnof')
                if vendor:
                    vendor_name = vendor.get_text(strip=True)
                    vendor1.append(vendor_name)

                
                i+=1
                if i==5:
                    title_element = content_element.find('h3')
                    if title_element:
                            Title = title_element.get_text(strip=True)
                    product_full_name[cc[country]]=(Title)
                    prices[cc[country]]=(orig_price)
                    vendors[cc[country]]=(vendor1)
                    product_links[cc[country]]=(product_link)
                    ratings[cc[country]]=(rating)
                    
                    break
    threads = []
    for country in country_code:
        thread = threading.Thread(target=web_scrap, args=(country,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    product_links=list(dict(sorted(product_links.items())).values())
    ratings=list(dict(sorted(ratings.items())).values())
    prices=list(dict(sorted(prices.items())).values())
    vendors=list(dict(sorted(vendors.items())).values())
    product_full_name=list(dict(sorted(product_full_name.items())).values())
    
    return product_full_name,prices,ratings,vendors,product_links,countries,image_link


def find_min_price_and_country(product_name):
    product_full_name,prices,ratings,vendors,product_link,countries,image_link=scrap_price(product_name)
    
    process=[   lambda orig_price:int(orig_price[1:].replace(',','').split('.')[0]) ,
                lambda orig_price:int(orig_price[2:].replace('\u202f', '').replace('\xa0', '').replace('.','').split(',')[0]),
                lambda orig_price:int(orig_price[:-1].replace('\u202f', '').replace('\xa0', '').split(',')[0]),
                lambda orig_price:int(orig_price),
                ]
    for i in range(len(prices)):
        if '$' in prices[i][0]:
            prices[i] = list(map(process[0], prices[i]))
        elif 'Rp' in prices[i][0]:
            prices[i] = list(map(process[1], prices[i]))
        elif '€' in prices[i][0]:
            prices[i] = list(map(process[2], prices[i]))
        elif '￥' in prices[i][0]:
            prices[i] = list(map(process[0], prices[i]))
        elif '฿' in prices[i][0]:
            prices[i] = list(map(process[0], prices[i]))
        elif '₹' in prices[i][0]:
            prices[i] = list(map(process[0], prices[i]))
        elif '£' in prices[i][0]:
            prices[i] = list(map(process[0], prices[i]))
        else:
            prices[i] = list(map(process[3], prices[i]))
    

    min_values = []

    for sublist in prices[:-1]:
        if len(sublist) > 0:
            max_value = max(sublist)
            threshold = 0.5 * max_value
            filtered_values = [value for value in sublist if value > threshold]
            if filtered_values:
                min_value = min(filtered_values)
                min_values.append(min_value)
            else:
                min_values.append(None)
        else:
            min_values.append(None)

    min_values.append(min(prices[-1]))
    return product_full_name,prices,ratings,vendors,product_link,countries,image_link,min_values

def get_exchange_rates():
    inr=[]
    response = requests.get('https://www.x-rates.com/table/?from=INR&amount=1')
    soup = BeautifulSoup(response.text, 'html.parser')
    currency_table = soup.find('table', class_='tablesorter ratesTable').find('tbody')
    currency_rows = currency_table.find_all('tr')
    for currency_row in currency_rows:
        columns = currency_row.find_all('td')
        currency = columns[0].get_text()
        inr_value = columns[1].get_text()
        value = columns[2].get_text()
        inr.append(round(float(value),4))
    indices = [1, 7,9, 13, 17, 20, 39, 45, 49, 50]
    exchange_rates = [inr[i] for i in indices]
    exchange_rates.append(1)
    print(exchange_rates)
    return exchange_rates

