from flask import Flask, request, render_template
# test

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def hello_world():
    error = None
    if request.method == "POST":
        pass
    else:
        pass
    return render_template("base_template.html", active=True)
