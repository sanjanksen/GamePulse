import requests
import json
import threading  # <- this was missing

# Your deployed Edge Function URL
FUNCTION_URL = "https://xtyufkrsudoktgxyharf.supabase.co/functions/v1/hello"
FUNCTION_URL2 = "https://xtyufkrsudoktgxyharf.supabase.co/functions/v1/update_current_question"

# The game code you want to send
payload = {
    "gameCode": "FGR736"
}

# Make the POST request with the Supabase Service Role key
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0eXVma3JzdWRva3RneHloYXJmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODk0NDExNCwiZXhwIjoyMDc0NTIwMTE0fQ.nfM55AufUJkDernamKuRabkquGi1yGlOatUgLjAAsLo"
}

response = requests.post(
    FUNCTION_URL,
    headers=headers,
    data=json.dumps(payload)
)

print(response.status_code)
print(response.json())

def send_request():
    response = requests.post(FUNCTION_URL2, headers=headers, data=json.dumps(payload))
    print("Status code:", response.status_code)
    try:
        print("Response:", response.json())
    except json.JSONDecodeError:
        print("Non-JSON response:", response.text)

    # Schedule the function to run again in 5 seconds
    threading.Timer(5, send_request).start()

send_request()

