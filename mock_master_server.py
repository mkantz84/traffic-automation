from flask import Flask, request

app = Flask(__name__)

@app.route('/results', methods=['POST'])
def results():
    data = request.get_json()
    print("Received result:", data)
    return {"status": "received"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000) 