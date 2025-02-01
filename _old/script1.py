import requests
import json
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

# ASIN to fetch manufacturer details for
asin = "B009VBSSAS"

# API request to fetch catalog item details
headers = {
    "x-amz-access-token": access_token,
    "Content-Type": "application/json"
}

response = requests.get(
    f"{endpoint}/catalog/v0/items/{asin}?MarketplaceId={marketplace_id}",
    headers=headers
)

# Parse response
if response.status_code == 200:
    item_data = response.json()
    manufacturer = item_data.get("payload", {}).get("AttributeSets", [{}])[0].get("Manufacturer", "Not Found")
    print(f"Manufacturer: {manufacturer}")
else:
    print(f"Error: {response.status_code}, {response.text}")
