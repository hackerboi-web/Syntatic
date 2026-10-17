from flask import Flask
from Syntatic.Orbitix import orbitix_bp

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(orbitix_bp, url_prefix="/orbitix")

if __name__ == "__main__":
    app.run(debug=False, port=3447, host="127.0.0.1")
""" filePath">
/workspace/app/Syntatic/app.py