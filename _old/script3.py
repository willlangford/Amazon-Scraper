import requests
import json
import time
import csv
from creds import credentials

# Getting the LWA access token using the Seller Central App credentials.
token_response = requests.post(
    "https://api.amazon.com/auth/o2/token",
    data={
        "grant_type": "refresh_token",
        "refresh_token": credentials["refresh_token"],
        "client_id": credentials["lwa_app_id"],
        "client_secret": credentials["lwa_client_secret"],
    },
)
access_token = token_response.json()["access_token"]

# Amazon SP-API endpoint
endpoint = "https://sellingpartnerapi-na.amazon.com"

# US Amazon Marketplace ID
marketplace_id = "ATVPDKIKX0DER"

# Read ASINs from CSV
asins = []
with open("asins.csv", newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        asins.append(row[0])

print(f"Processing {len(asins)} ASINs...")

# Prepare CSV output
with open("results2.csv", mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ASIN", "Title", "Brand", "Manufacturer", "Sales Rank"])
    
    for index, asin in enumerate(asins, start=1):
        print(f"Processing {index}/{len(asins)}: {asin}")
        
        headers = {
            "x-amz-access-token": access_token,
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{endpoint}/catalog/v0/items/{asin}?MarketplaceId={marketplace_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            item_data = response.json()
            attributes = item_data.get("payload", {}).get("AttributeSets", [{}])[0]
            
            title = attributes.get("Title", "Not Found")
            brand = attributes.get("Brand", "Not Found")
            manufacturer = attributes.get("Manufacturer", "Not Found")
            sales_rankings = item_data.get("payload", {}).get("SalesRankings", [])
            if sales_rankings and isinstance(sales_rankings, list) and len(sales_rankings) > 0:
                sales_rank = sales_rankings[0].get("Rank", "Not Found")
            else:
                sales_rank = "Not Found"
        else:
            title, brand, manufacturer, sales_rank = "Error", "Error", "Error", "Error"
        
        writer.writerow([asin, title, brand, manufacturer, sales_rank])
        
        # Rate limiting to 5 requests per second
        time.sleep(0.05)

print("Processing complete. Results saved to results.csv.")
