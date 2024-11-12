import requests
import pandas as pd

API_URL = 'https://api.openbrewerydb.org/breweries'

response = requests.get(API_URL)

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    
