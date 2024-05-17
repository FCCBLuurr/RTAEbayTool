import requests
import json
from datetime import date
import pandas as pd
from requests.auth import HTTPBasicAuth
from uszipcode import SearchEngine, SimpleZipcode
from tkinter import Tk
from tkinter.filedialog import *
from icecream import ic
Tk().withdraw()

csv_file = askopenfilename(title="Select Order Data", filetypes=[("CSV Files", "*.csv")])
df = pd.read_csv(csv_file, dtype={'Zip Code': str, 'SKU': str, 'Lot': str})

# Fill down 'NaN' values in the DataFrame for the relevant columns
filled_df = df.ffill()
print("filled df")
# Group the DataFrame by 'Winning Bidder' and 'Order Number' to consolidate items for each order
grouped_orders = filled_df.groupby(['Winning Bidder', 'Order Number'])
print("grouped df")
# Function to construct the order JSON payload
def construct_order_json(group):
    # Using .iloc with .index to get the first row of the group
    first_row_index = group.index[0]
    first_row = df.loc[first_row_index]
    country_code = first_row['country']
    
    if first_row['Phone Number'] is not None:
        phone = first_row['Phone Number']
    else:
        phone = first_row['Phone Number']
    
    sr = SearchEngine(
        simple_or_comprehensive=SearchEngine.SimpleOrComprehensiveArgEnum.simple
    )
    zip_info = sr.by_zipcode(first_row['Zip Code'])

    if (zip_info is not None) and country_code == 'US':
        city = zip_info.major_city
        country = 'US'
    elif first_row['country'] == 'CA':
        city = "Thunder bay"
        country = 'CA'
    else:
        print('No valid zip code: ', {first_row['country']})
    
    order_json = {
        "orderNumber": str(first_row['Order Number']),
        "orderDate": date.today().isoformat(),  # Replace with the actual order date if available
        "orderStatus": "awaiting_shipment",
        "customerUsername": first_row['Email'],
        "customerEmail": first_row['Email'],
        "billTo":{
            "name": first_row['Name'],
            "street1": first_row['Address'],
            "city": city,
            "state": first_row['State'],
            "postalCode": str(first_row['Zip Code'].strip()),
            "country": country,
            "phone": str(phone),
            "email": first_row['Email']
        },
        "shipTo": {
            "name": first_row['Name'],
            "street1": first_row['Address'],
            "city": city,
            "state": first_row['State'],
            "postalCode": str(first_row['Zip Code'].strip()),
            "country": country,
            "phone": str(phone),
            "email": first_row['Email']
        },
        "items": [
            {
                "lineItemKey": f"Lot:{row['Lot'].strip()}",
                "SKU": str(row['SKU'].strip()),
                "name": row['Title'],
                "quantity": int(row['Quantity']),
                "unitPrice": str(row['High Bid']) if pd.notnull(row['High Bid']) else "0",  # Replace NaN with "0"
                "taxAmount": 0.00,
                "shippingAmount": 0.00
            }
            for _, row in group.iterrows()
        ],
        "taxAmount": 0, #Placeholder until we figure out taxes
        "shippingAmount": 0, #Placeholder until we determine shipping dynamically
        "confirmation": "delivery",
        "shipDate": date.today().isoformat(),
    }
    return order_json

test_status = False

def upload_order_to_shipstation(order_json, test_mode=test_status):
    if test_mode:
        ic(order_json)
        return None

    # ShipStation API settings
    api_key = '3245cfc730304064b401fb9f5696d1e8'
    api_secret = 'e337d0d226d446dab24bf56110f51c10'
    
    # ShipStation API endpoint for creating orders
    url = 'https://ssapi.shipstation.com/orders/createorder'
    
    response = requests.post(url, auth=HTTPBasicAuth(api_key, api_secret), json=order_json)
    if response.status_code != 200:
        ic("Request failed with status code", response.status_code)
        ic("Response:", response.text)
    return response

# Iterate over each group, construct the order JSON, and upload to ShipStation
for _, group in grouped_orders:
    order_json = construct_order_json(group)
    try:
        # Attempt to serialize to JSON to check for errors
        serialized_json = json.dumps(order_json)
        response = upload_order_to_shipstation(order_json, test_mode=test_status)
        # Check the response status
        if response and response.status_code == 200:
            ic(group)
            ic("Order uploaded successfully!")
            
        else:
            ic("Failed to upload order.")
    except ValueError as e:
        ic(f"Error serializing order JSON: {e}")
        ic(f"Problematic order_json: {order_json}")
