from flask import Blueprint, jsonify
from http_codes_and_messages import HTTP_OK

ping_bp = Blueprint("ping", __name__)


@ping_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"}), HTTP_OK
