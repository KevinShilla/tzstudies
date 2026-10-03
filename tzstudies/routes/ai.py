from flask import Blueprint, current_app, jsonify, request
from openai import OpenAI

from tzstudies.extensions import limiter

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/ask", methods=["POST"])
@limiter.limit("20 per hour")
def ask():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict) or not isinstance(data.get("query", ""), str):
        return jsonify({"error": "Please enter a text question."}), 400
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "No query provided."}), 400

    if len(query) > 4000:
        return jsonify({"error": "Please keep your question under 4,000 characters."}), 400

    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"error": "AI service is not configured."}), 503

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1", timeout=20.0, max_retries=1)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful exam tutor for Tanzanian students. "
                        "Answer questions clearly and concisely, focusing on the "
                        "Tanzanian national curriculum (Standard 4 through Form 6). "
                        "Provide step-by-step explanations when appropriate."
                    ),
                },
                {"role": "user", "content": query},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})

    except Exception:
        current_app.logger.error("Study assistant request failed")
        return jsonify({"error": "Failed to get a response. Please try again."}), 502
