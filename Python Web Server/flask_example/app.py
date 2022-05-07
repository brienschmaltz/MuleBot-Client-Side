from flask import Flask, request

app = Flask(__name__)
app.config['DEBUG'] = True




@app.route("/data", method=("POST",))
def handle_data():
    return "Hello World - you sent me " + str(request.values)

if __name__ == '__main__':
    app.run()