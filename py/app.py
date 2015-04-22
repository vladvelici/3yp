from flask import Flask
from flask import jsonify, send_from_directory, url_for

app = Flask(__name__, static_url_path="")

index = None
edges = None
graph = None

def init(i, e, g):
    global index, edges, graph
    index = i
    edged = e
    graph = g
    app.run(debug=True)

@app.route("/graph")
def graph():
    return jsonify(graph.r())

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/w/<path:path>")
def w(path):
    return send_from_directory('static', path)
