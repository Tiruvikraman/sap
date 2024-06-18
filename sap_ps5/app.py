import re
import folium
from folium.plugins import MarkerCluster
import seaborn as sns
from flask import send_from_directory, Flask, render_template, request, redirect, flash, jsonify,send_file
from werkzeug.utils import secure_filename
import os
import threading
import shutil
import io
import matplotlib.pyplot as plt
from process_data import exchange_table,get_currency_conversion,vendor_details,process_upload_bill,perform_ocr
from scrap import get_exchange_rates,find_min_price_and_country
from slm_function import response
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key
UPLOAD_FOLDER = 'uploaded_files'  # Update this path
if os.path.exists(UPLOAD_FOLDER):
    shutil.rmtree(UPLOAD_FOLDER)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
countries=['Australia', 'Canada', 'China', 'France', 'Indonesia', 'Japan', 'Singapore', 'Thailand', 'United Kingdom', 'United States', 'India']
currency_symbols = ["$", "$", "¥", "€", "Rp", "¥", "$", "฿", "£", "$", "₹"]

recommendation_generated_event = threading.Event()

def exchange_rate_table():
    a= exchange_table()
    return a

def get_country_index(minimum_country):
    global country_index
    countries=['Australia', 'Canada', 'China', 'France', 'Indonesia', 'Japan', 'Singapore', 'Thailand', 'United Kingdom', 'United States', 'India']
    country_index=countries.index(minimum_country)
    return country_index

def identify_product(querry):
    global product_name
    product_name=response("Identify the product in the sentence.Sentence: "+ querry,10)
    return product_name

def image_link():
    return 'data:image/webp;base64,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'
exchange_rates=get_exchange_rates()
def identify_category(product_name):
    global category
    category=response("Find category of the given product. product: "+ product_name,10)
    return category
    
def find_minimum():
    global minimum_country,exchange_rates,product_full_name,prices,ratings,vendors,product_link,countries,image_link,min_values,country_price_inr,result_sentence,country_price_crt
    exchange_rates=get_exchange_rates()
    product_full_name,prices,ratings,vendors,product_link,countries,image_link,min_values=find_min_price_and_country(product_name)
    country_price_inr,result_sentence,country_price_crt=get_currency_conversion(min_values,exchange_rates)
    print(country_price_inr)
    minimum_country=response("Find the cheapest country among "+ result_sentence,10)
    minimum_country=minimum_country.replace(' ','')
    return minimum_country

def get_recommendation():
    global recommentaion,minimum_country_value,country_index,minimum_country,recommendation_generated
    minimum_country=find_minimum()
    if minimum_country=='UnitedStates':
        minimum_country='United States'
    minimum_country=minimum_country.replace(' ','')
    country_index=get_country_index(minimum_country)
    c_price=min_values[country_index]
    inr=country_price_inr[minimum_country]
    
    minimum_country_value=min_values[country_index]
    inr=minimum_country_value*exchange_rates[country_index]
    recommendation_generated=True
    c_price=currency_symbols[country_index]+str(c_price)
    recommentaion=response(f"Recommend the cheapest country based on the given input to buy the product.Product={product_name},price:'{c_price}',Inr: {inr} INR, Country={minimum_country},others={list(country_price_inr.keys())[1:3]}.",100).replace('<unk>',currency_symbols[country_index]).replace(' 1.Sign','<br>1.Sign').replace('2.Bu','<br>2.Bu').replace('3.Oth','<br>3.Oth')
    
    recommendation_generated_event.set()
    return recommentaion



def get_product_link():
 
    return product_link[country_index][prices[country_index].index(minimum_country_value)]
    

def delivery_details():
    global delivery_detail
    countries=['Australia', 'Canada', 'China', 'France', 'Indonesia', 'Japan', 'Singapore', 'Thailand', 'United Kingdom', 'United States', 'India']
    exchange_rate=exchange_rates[country_index]            
    delivery_charge = round(minimum_country_value * 0.1, 2)
    tax = round(minimum_country_value * 0.17, 2)
    total_price_local=minimum_country_value+delivery_charge+tax
    total_price_inr=total_price_local*exchange_rate
    delivery_charge=currency_symbols[country_index]+str(delivery_charge)
    tax=currency_symbols[country_index]+str(tax)
    base_price=currency_symbols[country_index]+str(minimum_country_value)
    total_price_local=currency_symbols[country_index]+str(total_price_local)


    delivery_detail=response(f'Provide me the delivery details based on the input. Country={minimum_country}, base price= {minimum_country_value}, Delivery cost= {delivery_charge}, tax= {tax},total_price_local={total_price_local},total_price_inr={total_price_inr}',80).replace('<unk>',currency_symbols[country_index])
    print(f'Provide me the delivery details based on the input. Country={minimum_country}, base price= {minimum_country_value}, Delivery cost= {delivery_charge}, tax= {tax},total_price_local={total_price_local},total_price_inr={total_price_inr}',80)
 
    return delivery_detail

def get_vendor_details():
    global vendor_details
    vendor_data=vendor_details(minimum_country,prices,vendors,ratings,currency_symbols[country_index])
    vendor_details=response(f"Recommend the vendor based on given data. {vendor_data}",40).replace('<unk>',currency_symbols[country_index]).replace('1. Bes','<br>1. Bes').replace('2. Aff','<br>2. Aff').replace('3. Fa','<br>3. Fa')
    print(f"Recommend the vendor based on given data. {vendor_data}",40)
    return vendor_details

def generate_bot_response(message):
    answer=response(message+"The price of "+ result_sentence,20)
    return answer


def generate_graph():
    recommendation_generated_event.wait()

    prices = country_price_crt
    countries = ['Australia', 'Canada', 'China', 'France', 'Indonesia', 'Japan', 'Singapore', 'Thailand', 'United Kingdom', 'United States', 'India']
    prices=[int(x) for x in prices]    
    plt.figure(figsize=(10, 6))
    realistic_prices = [x for x in prices if x < 1000000000]
    norm = plt.Normalize(min(realistic_prices), max(realistic_prices))
    cmap = plt.cm.RdYlGn_r 
    colors = [cmap(norm(value)) if value < 1000000000 else 'gray' for value in prices]
    min_value = min(prices)
    min_index = prices.index(min_value)
    average_value = sum(realistic_prices) / len(realistic_prices)
    bar_width = 0.6  # Adjust the width of the bars
    for index, (value, country) in enumerate(zip(prices, countries)):
        if value >= 1000000000:
            plt.bar(index, 0, color='gray')  # Plot a zero-height bar
            plt.text(index, 0, "Data NA", ha='center', va='bottom', fontsize=8, color='black')
        else:
            plt.bar(index, value, color=colors[index])
            plt.text(index, value + 0.2, f"₹{value}", ha='center', va='bottom', fontsize=8)    
    plt.annotate('Best Deal', xy=(min_index, min_value), xytext=(min_index, min_value + 20000),
                 arrowprops=dict(facecolor='green', arrowstyle='->'),
                 ha='center', va='center', fontsize=10,color='green')    
    closest_to_average_index = min(range(len(prices)), key=lambda i: abs(prices[i] - average_value))    
    plt.annotate('Average Price', xy=(closest_to_average_index, prices[closest_to_average_index]), xytext=(closest_to_average_index, prices[closest_to_average_index] + 20000),
                 arrowprops=dict(facecolor='blue', arrowstyle='->'),
                 ha='center', va='center', fontsize=10, color='blue')    
    plt.gcf().patch.set_facecolor((1.0, 1.0, 1.0, 0.8))
    cbar = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), ax=plt.gca(), extend='both')
    cbar.set_label('Price')
    cbar.ax.text(0.5, 1.1, 'High', transform=cbar.ax.transAxes, ha='center', va='center', fontsize=10)
    cbar.ax.text(0.5, -0.1, 'Low', transform=cbar.ax.transAxes, ha='center', va='center', fontsize=10)    
    plt.xlabel('Countries')
    plt.ylabel('Price')
    plt.title('Prices in Different Countries')    
    plt.xticks(range(len(countries)), countries, rotation=45, ha='right')    
    plt.tight_layout()    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf


def generate_map():
    recommendation_generated_event.wait()
    product_prices=country_price_inr
    country_coords = {
        "United States": [37.0902, -95.7129],
        "United Kingdom": [55.3781, -3.4360],
        "Germany": [51.1657, 10.4515],
        "France": [46.6034, 1.8883],
        "Canada": [56.1304, -106.3468],
        "Singapore": [1.3521, 103.8198],
        "China": [35.8617, 104.1954],
        "Japan": [36.2048, 138.2529],
        "Thailand": [15.8700, 100.9925],
        "Indonesia": [-0.7893, 113.9213],
        "India":[20.5937, 78.9629],
        "Australia":[25.2744, 133.7751]
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



def get_bill_dict(text):
    global result_dict
    bill_dict = response('Extract the product name and the price in the form of python dictionary from the given invoice. Invoice:' + text,50).replace('<unk>','').replace("</s>",'').replace('<pad>','')
    print(bill_dict)
    items = re.sub(r'[a-zA-Z](?=\d)', '', bill_dict)
    items = items.split(", ")

    # Initialize an empty dictionary
    result_dict = {}

    # Iterate over the key-value pairs
    for item in items:
        # Split each item into key and value
        key, value = item.split(": ")
        # Remove the single quotes around the key and strip any extra spaces
        key = key.strip("'")
        # Convert the value to a float
        value = float(value)
        result_dict[key] = value
    return result_dict

def generate_recommendations(result_dict):
    global bill_country
    d,products,bill_country,bill_india_price,bill_foreign_price,percentage=process_upload_bill(exchange_rates,result_dict)
    del d['total']
    rec=response(f"Recommend the best country to buy the products in the bill based on the data. Product Data: {products}, country={bill_country}, India price={bill_india_price}, country price={bill_foreign_price}, percentage difference={percentage}%.",50)
    return rec,d


@app.route('/')
def index():

    html_table_with_colors=exchange_rate_table()
    return render_template('index.html',html_table_with_colors=html_table_with_colors)

@app.route('/bill.html')
def bill():
    return render_template('bill.html')



@app.route('/uploaded_files/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    global bill_details
    if 'billInput' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['billInput']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Print file path for debugging
        print(f"File saved at: {file_path}")
        
        # Perform OCR on the uploaded file
        extracted_text = perform_ocr(file_path)
        
        # Extract bill details
        bill_details = get_bill_dict(extracted_text)
        dup_bill_details={}
        for i,j in bill_details.items():
            if i!='Total':
                dup_bill_details[i]=j

        # Return response with bill details (no recommendations here)
        return jsonify({'filename': filename, 'bill_details': dup_bill_details})
    else:
        flash('Allowed file types are png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/identify-product', methods=['POST'])
def identify_product_endpoint():
    data = request.json
    sentence = data.get('product', '')
    product = identify_product(sentence)
    image_url = image_link()
    return jsonify({"product": product, "image_url": image_url})

@app.route('/identify-category', methods=['POST'])
def identify_category_endpoint():
    data = request.json
    product = data.get('product', '')
    category = identify_category(product)
    return jsonify({"category": category})

@app.route('/get-recommendation', methods=['POST'])
def get_recommendation_endpoint():
    data = request.json
    sentence = data.get('product', '')
    recommendation = get_recommendation()
    return jsonify({"recommendation": recommendation})

@app.route('/get-product_link', methods=['POST'])
def get_product_link_endpoint():
    data = request.json
    product = data.get('product', '')
    product_link_url = get_product_link()
    return jsonify({"product_link": product_link_url})

@app.route('/delivery-details', methods=['POST'])
def delivery_details_endpoint():
    data = request.json
    product = data.get('product', '')
    delivery = delivery_details()
    return jsonify({"delivery": delivery})

@app.route('/vendor-details', methods=['POST'])
def vendor_details_endpoint():
    data = request.json
    product = data.get('product', '')
    vendor_detail = get_vendor_details()
    return jsonify({"vendor_details": vendor_detail})

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    message = data['message']  # Assuming 'message' is the key sent from frontend
    # Process the message and generate a response
    bot_response = generate_bot_response(message)  # Replace with your logic to generate response
    return jsonify({"bot_response": bot_response})

@app.route('/price-bar-graph')
def price_bar_graph():
    buf=generate_graph()
    
    if isinstance(buf, str):
        return buf, 400
    
    return send_file(buf, mimetype='image/png')

@app.route('/price-map')
def price_map():
    return generate_map()

@app.route('/bill_recommendation', methods=['POST'])
def bill_recommendation():
    
    dup_bil_2={}
    recommendations,bill_details2 = generate_recommendations(bill_details)
    for i,j in bill_details2.items():
        if i!='Purchase_total':
            dup_bil_2[i]=j

    return jsonify({'bill_recommendation': recommendations, 'bill_details2': dup_bil_2,'bill_country':bill_country})


if __name__ == '__main__':
    app.run()