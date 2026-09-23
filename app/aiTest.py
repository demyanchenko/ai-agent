import requests
import urllib3
import json

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # подавить предупреждение


# curl -sk \
# -X POST \
#     "https://alfagen.moscow.alfaintra.net/continue-dev/chat/completions" \
#     -H "Authorization: Bearer 04e8a51a-b5d8-4c55-ba3a-05632cde66b8" \
#        -H "Content-Type: application/json" \
#           -d '{
# "model": "DeepSeek-V4-Flash",
# "messages": [{"role": "user", "content": "Привет"}],
# "stream": false
# }'

url = "https://alfagen.moscow.alfaintra.net/continue-dev/v1/chat/completions"
headers = {
    "Authorization": "Bearer 04e8a51a-b5d8-4c55-ba3a-05632cde66b8",
    "Content-Type": "application/json"
}
payload = {
    "model": "DeepSeek-V4-Flash",
    "messages": [{"role": "user", "content": "Привет"}],
    "stream": False,
}

resp = requests.post(url, headers=headers, json=payload, verify=False)

with open('resp.txt', 'w') as file:
    print("STATUS:", resp.status_code, file=file)
    print("BODY:", resp.text, file=file)   # ← точная причина 400
    try:
        myJson = json.loads(resp.text)
        print("TEXT:", myJson["choices"][0]["message"]["content"], file=file)   # ← точная причина 400
    except json.JSONDecodeError as e:
        print(f"Ошибка при парсинге JSON: {e}")
file.close()
# getattr(resp.text, "choices").getattr(resp.text, "message").getattr(resp.text, "content")
# resp.text.get('choices', {}).get('message', {}).get('content', 'Не найдено')