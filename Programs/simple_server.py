from flask import Flask
app = Flask("My First Web Server")

@app.route('/', methods=['GET'])
def hello_world():
    return "Hello World"

app.run(host="0.0.0.0", port=8080)
