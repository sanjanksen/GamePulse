import requests
import json
import os

# URL of your deployed Supabase Edge Function
FUNCTION_URL = "https://xtyufkrsudoktgxyharf.supabase.co/functions/v1/update_finished"


# The game code you want to update
payload = {
    "gameCode": "8RFTMB",
    "isFinished": False  # Change to False if you want to mark it unfinished

}

# Headers including the Service Role Key
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0eXVma3JzdWRva3RneHloYXJmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODk0NDExNCwiZXhwIjoyMDc0NTIwMTE0fQ.nfM55AufUJkDernamKuRabkquGi1yGlOatUgLjAAsLo"
}

# Send the POST request
response = requests.post(FUNCTION_URL, json=payload, headers=headers)

# Print the response
print("Status code:", response.status_code)
print("Response JSON:", response.json())
