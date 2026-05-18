from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://appuser:apppass@db:3306/recommenddb'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), unique=True, nullable=False)
    recommendation = db.Column(db.String(200), nullable=False)


with app.app_context():
    db.create_all()

    items = [
        {"keyword": "hot", "recommendation": "It's Summer"},
        {"keyword": "cold", "recommendation": "It's Winter"},
        {"keyword": "hungry", "recommendation": "Eat Pizza"},
        {"keyword": "tired", "recommendation": "Drink Coffee"}
    ]

    for item in items:
        existing = Recommendation.query.filter_by(
            keyword=item["keyword"]
        ).first()

        if existing:
            existing.recommendation = item["recommendation"]
        else:
            db.session.add(Recommendation(**item))

    db.session.commit()


@app.route("/")
def home():
    return """
    <h1>Recommendation System</h1>
    <form id="form">
        <input id="input" placeholder="Enter word">
        <button type="submit">Send</button>
    </form>

    <h3 id="result"></h3>

    <script>
    document.getElementById("form").onsubmit = async (e) => {
        e.preventDefault();
        const input = document.getElementById("input").value;

        const res = await fetch("/recommend", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({input})
        });

        const data = await res.json();
        document.getElementById("result").innerText = data.recommendation;
    };
    </script>
    """


@app.route("/recommend", methods=["POST"])
def recommend():
    user_input = request.json.get("input", "").strip().lower()

    item = Recommendation.query.filter_by(keyword=user_input).first()

    return jsonify({
        "recommendation": item.recommendation if item else "No recommendation found"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
