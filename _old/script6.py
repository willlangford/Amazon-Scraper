import requests
import json
import time
import csv
from creds import credentials

def refresh_access_token():
    """Refresh the LWA access token using the Seller Central App credentials."""
    token_response = requests.post(
        "https://api.amazon.com/auth/o2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": credentials["refresh_token"],
            "client_id": credentials["lwa_app_id"],
            "client_secret": credentials["lwa_client_secret"],
        },
    )
    return token_response.json().get("access_token")

# Initial access token
token_expiry_time = time.time() + 1800  # 30 minutes from now
access_token = refresh_access_token()

# Amazon SP-API endpoint
endpoint = "https://sellingpartnerapi-na.amazon.com"
marketplace_id = "ATVPDKIKX0DER"

# Read ASINs from CSV
asins = []
with open("asins.csv", newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        asins.append(row[0])
print(f"Processing {len(asins)} ASINs...")

# Prepare CSV output
with open("results60.csv", mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ASIN", "Title", "Brand", "Manufacturer", "Sales Rank", "MPN", "Parent ASIN"])
    
    for index, asin in enumerate(asins, start=1):
        # Refresh token if expired
        if time.time() >= token_expiry_time:
            access_token = refresh_access_token()
            token_expiry_time = time.time() + 1800  # Reset expiry timer
            print("Access token refreshed.")
        
        print(f"Processing {index}/{len(asins)}: {asin}")
        
        headers = {
            "x-amz-access-token": access_token,
            "Content-Type": "application/json"
        }
        
        max_retries = 2
        for attempt in range(max_retries + 1):
            response = requests.get(
                f"{endpoint}/catalog/v0/items/{asin}?MarketplaceId={marketplace_id}",
                headers=headers
            )
            if response.status_code == 200:
                break
            print(f"Attempt {attempt + 1} failed for ASIN {asin}, retrying...")
            time.sleep(1)
        
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
            mpn = attributes.get("PartNumber", "Not Found")
            parent_asin = item_data.get("payload", {}).get("Relationships", [{}])[0].get("ParentASIN", "Not Found")
        else:
            title, brand, manufacturer, sales_rank, mpn, parent_asin = "Error", "Error", "Error", "Error", "Error", "Error"
            
        writer.writerow([asin, title, brand, manufacturer, sales_rank, mpn, parent_asin])
        
        # Rate limiting to 5 requests per second
        time.sleep(0.1)

print("Processing complete. Results saved to results60.csv.")
