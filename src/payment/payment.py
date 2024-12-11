import requests
import dotenv

url = "https://api.cryptocloud.plus/v2/invoice/create"
headers = {
    "Authorization": "Token eyJ0eXAi1iJKV1QiLCJhbGciOiJIAcI1NiJ9.eyJpZCI6MTMsImV4cCI6MTYzMTc4NjQyNn0.HQavV3z8dFnk56bX3MSY5X9lR6qVa9YhAoeTEH"
}

response = requests.post(url, headers=headers)

if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Fail:", response.status_code, response.text)