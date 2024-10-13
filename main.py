from flask import Flask


app = Flask(__name__)

@app.route('/')
def index():
    return 'TA Kapita Selekta'

if __name__ == '__main__':
    app.run(debug=True, port=5000)