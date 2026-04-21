from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "AI Task Planner API"})

@app.route('/api/ai/status')
def status():
    return jsonify({
        "status": "active",
        "message": "API работает",
        "is_mock": True
    })

if __name__ == '__main__':
    print("🚀 Запуск бэкенда на http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
