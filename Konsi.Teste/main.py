import requests
import json

documentos: list = ["08301972572", "87366274534", "10381350525", "08433933515", "11031980504", "08204055587", "16395182587", "09982795368", "11827866500", "06611834591"]

for doc in documentos:
    payload = json.dumps(f"{doc}")
    headers = {
        'Content-Type': 'application/json'
    }
    resp = requests.request("POST", "http://localhost:8000/enviar_dados/", headers=headers, data=payload)
    print(resp.content)
