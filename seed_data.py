from qdrant_client import QdrantClient

client =  QdrantClient("localhost", port=6333)
COLLECTION_NAME = "enterprise_router"

#Notice the variety: Typos, different phrasings, specific technical terms.
training_data = [
    #INTENT: CRITICAL_TECHNICAL_INCIDENT (High Urgency)
    {"text": "Production is down, getting 502 Bad Gateway", "intent": "critical_incident"},
    {"text": "Database connection refused in us-east-1", "intent": "critical_incident"},
    {"text": "API latency is over 5000ms, this is an outage", "intent": "critical_incident"},
    {"text": "Users cannot log in, critical failure", "intent": "critical_incident"},
    {"text": "The entire dashboard is blank", "intent": "critical_incident"},

    #INTENT: SALES_ENTERPRISE (High Value)
    {"text": "We need SSO and SLA for 500 seats", "intent": "sales_enterprise"},
    {"text": "I want to talk to a rep about a custom contract", "intent": "sales_enterprise"},
    {"text": "Do you offer on-premise deployment for banks?", "intent": "sales_enterprise"},
    {"text": "Procurement needs a vendor risk assessment form", "intent": "sales_enterprise"},
    {"text": "Can we pay via invoice instead of credit card?", "intent": "sales_enterprise"},

    #INTENT: COMPLIANCE_LEGAL (Risk Management)
    {"text": "I need to exercise my GDPR right to be forgotten", "intent": "compliance"},
    {"text": "Where is your data residency located? EU or US?", "intent": "compliance"},
    {"text": "Are you SOC2 Type II compliant?", "intent": "compliance"},
    {"text": "Delete all my data immediately", "intent": "compliance"},
    {"text": "Is this HIPAA compliant?", "intent": "compliance"},

    #INTENT: BILLING_DISPUTE (Churn Risk)
    {"text": "Why was I charged $500? I cancelled last month.", "intent": "billing_dispute"},
    {"text": "Invoice #4432 is incorrect, please fix.", "intent": "billing_dispute"},
    {"text": "I did not authorize this transaction", "intent": "billing_dispute"},
    {"text": "Refund this immediately, it's a scam", "intent": "billing_dispute"},

    #INTENT: API_DOCUMENTATION (Self-Serve)
    {"text": "How do I paginate results in the /users endpoint?", "intent": "api_help"},
    {"text": "What is the rate limit for the free tier?", "intent": "api_help"},
    {"text": "Python SDK throws a validation error on update", "intent": "api_help"},
    {"text": "Where can I find the swagger file?", "intent": "api_help"},
]

def load_data():
    docs = [item["text"] for item in training_data]
    metas = [{"intent": item["intent"]} for item in training_data]
    ids = list(range(len(docs)))

    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=client.get_fastembed_vector_params() #Auto-config for FastEmbed
    )

    print(f"Uploading {len(docs)} enterprise examples...")
    client.add(
        collection_name=COLLECTION_NAME,
        documents=docs,
        metadata=metas,
        ids=ids
    )
    print("Data Loaded Successfully.")

if __name__ == "__main__":
    load_data()