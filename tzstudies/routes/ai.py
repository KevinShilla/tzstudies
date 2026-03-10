from flask import Blueprint, current_app, jsonify, request
from openai import OpenAI

from tzstudies.extensions import csrf, limiter

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/ask", methods=["POST"])
@limiter.limit("20 per hour")
@csrf.exempt  # API endpoint uses JSON, not form submission
def ask():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "No query provided."}), 400

    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"error": "AI service is not configured."}), 503

    try:
        client = OpenAI(api_key=api_key)
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

    except Exception as exc:
        current_app.logger.error("OpenAI API error: %s", exc)
        return jsonify({"error": "Failed to get a response. Please try again."}), 502
