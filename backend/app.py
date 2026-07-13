from flask import Flask, request, jsonify
from flask_cors import CORS
from watson_service import generate_roadmap

app = Flask(__name__)
CORS(app)


@app.route("/api/generate-roadmap", methods=["POST"])
def roadmap():
    data = request.get_json()

    required_fields = ["email", "careerGoal", "domain", "skillLevel", "programmingSkills", "studyHours", "learningStyle"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400

    result = generate_roadmap(data)

    if "error" in result:
        return jsonify(result), 500

    return jsonify(result), 200


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
