import requests
import datetime
import hashlib
import hmac
import json

# 🔹 Replace with your actual credentials
ACCESS_KEY = "amzn1.application-oa2-client.90ccdf0ae0da4ee38ab5e4302c626922"
SECRET_KEY = "amzn1.oa2-cs.v1.cc7c9b4ad17797e10889bf049b0a6ddb6b1619e65675fc198b1a7bb8b0658a5e"
SESSION_TOKEN = "Atza|IwEBIJ2k_CTYO4AtYccqbsbvwtqLLVNWfWb6lnVh9ozd0iVDoZmZlQ3cP6P1oK_c1SuDJlIm4dPlhBnmA3XKevCXQB0sVDHoUqb4YfCiaxeP43XjtHRFM2kmxtkMOUQK1VBljZ8I7Ud08xYGyWIDVuj4KZEOhRMLAiwkB5DKKXMnKVIRXwJ2jZBqEwCcL-FvYI0QNIHqEUPL2L2YUPF46CWZXrIOSMje2_vIRp_S4uAYvBaqqwGZ4zLfgXEYlvvCScAlleD279ctEBnwcreuoLYbBDibaIP7Ap1wz5C7mn83CD_fnsDiXGwyRAdp1iDv8VwsA99zi15slml9pnmFVzc04BYa"  # If using temporary credentials
ACCESS_TOKEN = "Atzr|IwEBIIhwKGrBjo800-9IvHqfSIMbJ1eM3ewV6HzvXBJMDgW5jEQ6u4Y-T2qNTf_huPQkpF-EDC2QK2NUTPhWVyOnRj6YN6j1wT4tHV9onzOXGFsp_l0Qkh2DjNi03chFBD92ACXYMuIoMF9bPMXBZKtKfDAeTLg7veVCb2IBdNT4R5XYnj1qgZKsuRgLkfp8XQs55F4ULof0vbylv1AtYfQNc14sCj00f9rf6_rjFetLJWqSf4e1xX0sfHRUZNWLeV_lAwB5uRHtWwzlIbbv_zmKRAn3cGSv7UXJ31UXTKbKcJkAS07gyDjUlOL31w3v1wZgbBA"

# 🔹 Amazon Region & API Endpoint
REGION = "us-east-1"  # Change based on your marketplace (NA, EU, FE)
SERVICE = "execute-api"
BASE_URL = "https://sellingpartnerapi-na.amazon.com"  # Use correct endpoint
ASIN = "B009VBSSAS"

# 🔹 API URL
URL = f"{BASE_URL}/catalog/2022-04-01/items/{ASIN}?includedData=attributes"

# 🔹 Generate Timestamp
from datetime import datetime, timezone
timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
date_stamp = datetime.now(timezone.utc).strftime('%Y%m%d')


# 🔹 AWS Signature Version 4 - Create Canonical Request
canonical_uri = f"/catalog/2022-04-01/items/{ASIN}"
canonical_querystring = "includedData=attributes"
canonical_headers = f"host:sellingpartnerapi-na.amazon.com\nx-amz-date:{timestamp}\nx-amz-security-token:{SESSION_TOKEN}\n"
signed_headers = "host;x-amz-date;x-amz-security-token"

payload_hash = hashlib.sha256("".encode("utf-8")).hexdigest()
canonical_request = f"GET\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

# 🔹 Create String to Sign
algorithm = "AWS4-HMAC-SHA256"
credential_scope = f"{date_stamp}/{REGION}/{SERVICE}/aws4_request"
string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

# 🔹 Generate Signing Key
def get_signature_key(key, date_stamp, region_name, service_name):
    k_date = hmac.new(("AWS4" + key).encode("utf-8"), date_stamp.encode("utf-8"), hashlib.sha256).digest()
    k_region = hmac.new(k_date, region_name.encode("utf-8"), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service_name.encode("utf-8"), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()
    return k_signing

signing_key = get_signature_key(SECRET_KEY, date_stamp, REGION, SERVICE)

# 🔹 Create Signature
signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

# 🔹 Construct Authorization Header
authorization_header = (
    f"{algorithm} Credential={ACCESS_KEY}/{credential_scope}, "
    f"SignedHeaders={signed_headers}, Signature={signature}"
)

# 🔹 Final Headers
headers = {
    "x-amz-date": timestamp,
    "Authorization": authorization_header,
    "x-amz-security-token": SESSION_TOKEN,  # Required for temporary credentials
    "x-amz-access-token": ACCESS_TOKEN,  # SP-API Access Token
    "Content-Type": "application/json"
}

# 🔹 Make API Request
response = requests.get(URL, headers=headers)

# 🔹 Parse Response
if response.status_code == 200:
    data = response.json()
    attributes = data.get("attributes", {})
    manufacturer = attributes.get("manufacturer", [{"value": "Unknown"}])[0]["value"]
    brand = attributes.get("brand", [{"value": "Unknown"}])[0]["value"]

    print(f"✅ Manufacturer: {manufacturer}")
    print(f"✅ Brand: {brand}")
else:
    print(f"❌ Error: {response.status_code}, {response.text}")
