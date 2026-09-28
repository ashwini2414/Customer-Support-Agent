import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=os.environ["HINDSIGHT_API_KEY"]
)

# Fake past customers with support history
past_tickets = [
    {"customer_id": "cust_priya", "content": "Priya Sharma reported her router disconnecting every evening. Root cause was outdated firmware. Fixed by updating the router firmware."},
    {"customer_id": "cust_priya", "content": "Priya Sharma later complained about slow WiFi speed in her bedroom. Fixed by suggesting a WiFi extender."},
    {"customer_id": "cust_ramesh", "content": "Ramesh Kumar's smart TV kept losing connection to the app. Fixed by clearing the app cache and reinstalling."},
    {"customer_id": "cust_ananya", "content": "Ananya Reddy was billed twice for her subscription. Refund was issued and duplicate charge reversed."},
    {"customer_id": "cust_ananya", "content": "Ananya Reddy asked how to downgrade her subscription plan. Guided her through account settings."},
]

for ticket in past_tickets:
    client.retain(
        bank_id=ticket["customer_id"],
        content=ticket["content"]
    )
    print(f"Stored memory for {ticket['customer_id']}")

print("Done seeding data!")