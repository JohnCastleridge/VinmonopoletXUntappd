import requests

API_KEY = "0803107360064be187d02eb284f7e146"
url = "https://apis.vinmonopolet.no/products/v0/details-normal?maxResults=5&start=0"
headers = {"Ocp-Apim-Subscription-Key": API_KEY}

print("Tester tilkobling til Vinmonopolet API...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status kode: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Fikk {len(data)} produkter tilbake.")
        if len(data) > 0:
            print("Eksempel på et produkt:")
            print(data[0])
            print("API fungerer som det skal!")
            exit(0)
    else:
        print("API returnerte feilkode:", response.text)
        exit(1)
except Exception as e:
    print(f"Feil under tilkobling: {e}")
    exit(1)
