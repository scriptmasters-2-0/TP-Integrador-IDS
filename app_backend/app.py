import config
from flask import Flask
from routes.ping import ping_bp

app = Flask(__name__)

app.register_blueprint(ping_bp)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
