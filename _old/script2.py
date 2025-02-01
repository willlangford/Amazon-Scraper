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
with open("results.csv", mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ASIN", "Manufacturer"])
    
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
            manufacturer = item_data.get("payload", {}).get("AttributeSets", [{}])[0].get("Manufacturer", "Not Found")
        else:
            manufacturer = "Error"
        
        writer.writerow([asin, manufacturer])
        
        # Rate limiting to 5 requests per second
        time.sleep(0.1)

print("Processing complete. Results saved to results.csv.")
