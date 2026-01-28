#!/usr/bin/env python3
"""
Direct URL test for AbraFlexi
"""
import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://demo.flexibee.eu:5434/c/demo_de.json"
user = "winstrom"
password = "winstrom"

print(f"Testing URL: {url}")
print(f"User: {user}")
print()

try:
    response = requests.get(
        url,
        auth=HTTPBasicAuth(user, password),
        verify=False,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Connection successful!")
        data = response.json()
        print(f"Response keys: {list(data.keys())[:10]}")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
