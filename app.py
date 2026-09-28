import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

load_dotenv()

app = Flask(__name__)

hindsight = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=os.environ["HINDSIGHT_API_KEY"]
)

groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    hindsight = Hindsight(
        base_url="https://api.hindsight.vectorize.io",
        api_key=os.environ["HINDSIGHT_API_KEY"]
    )
    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

    data = request.json
    customer_id = data.get("customer_id")
    message = data.get("message")

    # Recall past history for this customer
    try:
        recall_result = hindsight.recall(bank_id=customer_id, query=message)
        past_memories = [r.text for r in recall_result.results]
    except Exception:
        past_memories = []

    if past_memories:
        memory_context = "Past history with this customer:\n" + "\n".join(past_memories)
    else:
        memory_context = "This is a new customer with no past history."

    # Build the prompt for the LLM
    system_prompt = f"""You are a helpful customer support agent.
{memory_context}

If there is past history relevant to the customer's message, reference it directly and give a faster, more personalized answer.
If there is no history, give generic but helpful troubleshooting advice.
Keep your reply short and friendly."""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )

    reply = response.choices[0].message.content

    # Retain this new interaction for future memory
    hindsight.retain(
        bank_id=customer_id,
        content=f"Customer said: {message}. Agent replied: {reply}"
    )

    return jsonify({
        "reply": reply,
        "recalled_memories": past_memories
    })
@app.route("/briefing", methods=["POST"])
def briefing():
    hindsight = Hindsight(
        base_url="https://api.hindsight.vectorize.io",
        api_key=os.environ["HINDSIGHT_API_KEY"]
    )
    customer_id = request.json.get("customer_id")
    try:
        r = hindsight.reflect(
            bank_id=customer_id,
            query="Write a briefing for a support agent about this customer: past issues, what fixed them, and how best to help next. Use 3 short bullet points."
        )
        text = r.text
    except Exception:
        text = "No history yet for this customer."
    return jsonify({"briefing": text})
if __name__ == "__main__":
    app.run(debug=True)