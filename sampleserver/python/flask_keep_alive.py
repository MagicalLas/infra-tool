from flask import Flask

app = Flask(__name__)

@app.route('/sample')
def sample_endpoint():
    return 'simple is best'

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=8001)  # threaded=True는 여러 연결을 동시에 처리하도록 합니다.
