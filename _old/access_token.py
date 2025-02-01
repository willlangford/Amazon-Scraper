import requests

# 🔹 Replace with your actual credentials
CLIENT_ID = "amzn1.application-oa2-client.90ccdf0ae0da4ee38ab5e4302c626922"
CLIENT_SECRET = "amzn1.oa2-cs.v1.cc7c9b4ad17797e10889bf049b0a6ddb6b1619e65675fc198b1a7bb8b0658a5e"
REFRESH_TOKEN = "Atzr|IwEBIIhwKGrBjo800-9IvHqfSIMbJ1eM3ewV6HzvXBJMDgW5jEQ6u4Y-T2qNTf_huPQkpF-EDC2QK2NUTPhWVyOnRj6YN6j1wT4tHV9onzOXGFsp_l0Qkh2DjNi03chFBD92ACXYMuIoMF9bPMXBZKtKfDAeTLg7veVCb2IBdNT4R5XYnj1qgZKsuRgLkfp8XQs55F4ULof0vbylv1AtYfQNc14sCj00f9rf6_rjFetLJWqSf4e1xX0sfHRUZNWLeV_lAwB5uRHtWwzlIbbv_zmKRAn3cGSv7UXJ31UXTKbKcJkAS07gyDjUlOL31w3v1wZgbBA"

# 🔹 Amazon LWA Token URL
TOKEN_URL = "https://api.amazon.com/auth/o2/token"

# 🔹 Request Payload
payload = {
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}

# 🔹 Request New Token
response = requests.post(TOKEN_URL, data=payload)
token_data = response.json()

if "access_token" in token_data:
    print("✅ New Access Token:", token_data["access_token"])
else:
    print("❌ Error:", token_data)
