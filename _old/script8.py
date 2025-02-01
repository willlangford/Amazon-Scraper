import requests
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

# Read ASINs from CSV, skipping the first row (header)
asins = []
with open("bd_asins_leash_collar.csv", newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)  # Skip header row
    for row in reader:
        asin = row[0].strip()
        asins.append(asin)
print(f"Processing {len(asins)} ASINs...")

# Prepare CSV output
with open("results100.csv", mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ASIN", "Title", "Brand", "Manufacturer", "Sales Rank 1", "Sales Rank 2", "MPN", "Parent ASIN", "UPC", "EAN", "GTIN"])
    
    for index, asin in enumerate(asins, start=1):
        print(f"Processing ASIN {index}/{len(asins)}: {asin}...")
        
        # Refresh token if expired
        if time.time() >= token_expiry_time:
            access_token = refresh_access_token()
            token_expiry_time = time.time() + 1800  # Reset expiry timer
        
        headers = {
            "x-amz-access-token": access_token,
            "Content-Type": "application/json"
        }
        
        url = f"{endpoint}/catalog/2022-04-01/items/{asin}?marketplaceIds={marketplace_id}&includedData=identifiers,attributes,relationships,summaries,salesRanks"
        
        max_retries = 2
        for attempt in range(max_retries + 1):
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                break
            time.sleep(1)
        
        if response.status_code == 200:
            item_data = response.json()
            
            # Extract summaries (Title, Brand, Manufacturer)
            summaries = item_data.get("summaries", [{}])[0]
            title = summaries.get("itemName", "Not Found")
            brand = summaries.get("brand", "Not Found")
            manufacturer = summaries.get("manufacturer", "Not Found")
            mpn = summaries.get("partNumber", "Not Found")

            # Extract Sales Ranks
            sales_rank_1 = "Not Found"
            sales_rank_2 = "Not Found"
            sales_ranks = item_data.get("salesRanks", [])
            if sales_ranks:
                classification_ranks = sales_ranks[0].get("classificationRanks", [])
                if len(classification_ranks) > 0:
                    sales_rank_1 = classification_ranks[0].get("rank", "Not Found")
                if len(classification_ranks) > 1:
                    sales_rank_2 = classification_ranks[1].get("rank", "Not Found")

            # Extract Parent ASIN
            parent_asin = "Not Found"
            relationships = item_data.get("relationships", [])
            for rel in relationships:
                rel_details = rel.get("relationships", [])
                for r in rel_details:
                    if "parentAsins" in r:
                        parent_asin = r["parentAsins"][0]
                        break
            
            # Extract UPC, EAN, GTIN
            upc = ean = gtin = "Not Found"
            identifiers = item_data.get("identifiers", [])
            for identifier in identifiers:
                for id_entry in identifier.get("identifiers", []):
                    if id_entry.get("identifierType") == "UPC":
                        upc = id_entry.get("identifier")
                    elif id_entry.get("identifierType") == "EAN":
                        ean = id_entry.get("identifier")
                    elif id_entry.get("identifierType") == "GTIN":
                        gtin = id_entry.get("identifier")
            
        else:
            title = brand = manufacturer = sales_rank_1 = sales_rank_2 = mpn = parent_asin = upc = ean = gtin = "Error"
        
        writer.writerow([asin, title, brand, manufacturer, sales_rank_1, sales_rank_2, mpn, parent_asin, upc, ean, gtin])
        
        print(f"Completed ASIN {index}/{len(asins)}")
        
        # Rate limiting to 5 requests per second
        time.sleep(0.1)

print("Processing complete. Results saved to results60.csv.")
