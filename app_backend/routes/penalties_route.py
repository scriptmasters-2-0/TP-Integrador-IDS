import traceback
from database import obtener_conexion
import mysql.connector
from flask import Blueprint, jsonify, request
from validators import valid_id, valid_penalty_patch
from http_codes_and_messages import (
    HTTP_OK,
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND,
    HTTP_INTERNAL_SERVER_ERROR,
    MSG_DB_CONNECTION_FAILED,
    MSG_NOT_FOUND,
    MSG_BAD_REQUEST,
    MSG_INTERNAL_SERVER_ERROR,
)

penalties_bp = Blueprint("penalties", __name__)


@penalties_bp.route("/api/penalties/<int:penalty_id>", methods=["PATCH"])
def patch_penalty(penalty_id):

    conn = obtener_conexion()
    if conn is None:
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    if valid_id(penalty_id) is None:
        return jsonify({"error": MSG_BAD_REQUEST}), HTTP_BAD_REQUEST

    try:
        data = request.get_json()
    except Exception:
        data = None

    is_valid, error = valid_penalty_patch(data)
    if not is_valid:
        return jsonify({"error": MSG_BAD_REQUEST, "detail": error}), HTTP_BAD_REQUEST

    if "status" in data:
        data.update({"activa": 1 if data.get("status") == "Activa" else 0})
        data.pop("status")
        if not data.get("activa"):
            keysToUpdate.append("fecha_fin = NOW()")

    if "notes" in data:
        data.update({"motivo": data.get("notes")})
        data.pop("notes")

    keysToUpdate = data.keys()

    set_clause = ", ".join([f"{f} = %({f})s" for f in keysToUpdate])
    data.update({"penalty_id": penalty_id})

    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        sql = f"UPDATE penalizacion SET {set_clause} WHERE id = %(penalty_id)s"
        cursor.execute(sql, data)
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        cursor.execute(
            "SELECT id, id_usuario, motivo, fecha_inicio, fecha_fin, activa FROM penalizacion WHERE id = %(penalty_id)s",
            {"penalty_id": penalty_id},
        )

        row = cursor.fetchone()

        if not row:
            return jsonify({"message": MSG_NOT_FOUND}), HTTP_NOT_FOUND

        response = {
            "id": row.get("id"),
            "userId": row.get("id_usuario"),
            "loanId": None,
            "reason": row.get("motivo"),
            "status": "Activa" if row.get("activa") else "Levantada",
            "severity": None,
            "notes": row.get("motivo"),
            "createdAt": (
                row.get("fecha_inicio").isoformat() if row.get("fecha_inicio") else None
            ),
            "resolvedAt": (
                row.get("fecha_fin").isoformat() if row.get("fecha_fin") else None
            ),
        }

        return jsonify(response), HTTP_OK

    except mysql.connector.Error:
        traceback.print_exc()
        return jsonify({"error": MSG_DB_CONNECTION_FAILED}), HTTP_INTERNAL_SERVER_ERROR

    except Exception:
        traceback.print_exc()
        return jsonify({"error": MSG_INTERNAL_SERVER_ERROR}), HTTP_INTERNAL_SERVER_ERROR

    finally:
        try:
            cursor.close()

        except Exception:
            pass

        try:
            conn.close()

        except Exception:
            pass
