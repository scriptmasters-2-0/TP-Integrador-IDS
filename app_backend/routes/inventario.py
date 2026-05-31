from flask import Blueprint, jsonify, request
from flask_login import login_required
from constants import HTTP_OK, HTTP_NOT_FOUND, HTTP_BAD_REQUEST
from database import obtener_conexion

blueprint_inventario = Blueprint("inventario", __name__)


# ISSUE #43: PATCH /api/items/{id}/condition


# pre:  item_id es un entero positivo. condicion es un string ('disponible', 'dañado', 'reparacion', 'dado de baja').
# post: actualiza el estado del ítem en la base de datos. Retorna True si se modificó, False si el ítem no existía.
def actualizar_condicion_db(item_id, condicion):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if condicion == "reparacion":
        necesita_rep_flag = True

    else:
        necesita_rep_flag = False

    cursor.execute(
        "UPDATE articulos SET estado = %s, necesita_reparacion = %s WHERE id = %s",
        (condicion, necesita_rep_flag, item_id),
    )
    conexion.commit()
    actualizado = cursor.rowcount > 0
    cursor.close()
    conexion.close()
    return actualizado


# pre:  el usuario está autenticado en el sistema. item_id es un entero positivo en la URL. El body contiene un JSON con el campo "estado".
# post: retorna 200 si se cambió la condición, 404 si el ítem no existe, 400 si el ID o el estado son inválidos.
@blueprint_inventario.route("/api/items/<int:item_id>/condition", methods=["PATCH"])
@login_required
def cambiar_condicion_item(item_id):
    if item_id <= 0:
        return jsonify({"error": "ID inválido"}), HTTP_BAD_REQUEST

    datos = request.get_json()
    if not datos or "estado" not in datos:
        return jsonify({"error": "Falta especificar el campo estado"}), HTTP_BAD_REQUEST

    nuevo_estado = datos.get("estado")
    estados_validos = ["disponible", "dañado", "reparacion", "dado de baja"]

    if nuevo_estado not in estados_validos:
        return jsonify({"error": "Estado no permitido"}), HTTP_BAD_REQUEST

    if actualizar_condicion_db(item_id, nuevo_estado):
        return jsonify({"mensaje": "Condición del ítem actualizada correctamente"}), HTTP_OK

    return jsonify({"error": "Artículo no encontrado"}), HTTP_NOT_FOUND


# ISSUE #44: DELETE /api/items/{id}


# pre:  item_id es un entero positivo.
# post: realiza la baja lógica del ítem cambiando su estado a 'dado de baja'. Retorna True si se modificó, False si no existía.
def dar_de_baja_item_db(item_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "UPDATE articulos SET estado = 'dado de baja' WHERE id = %s",
        (item_id,),
    )
    conexion.commit()
    actualizado = cursor.rowcount > 0
    cursor.close()
    conexion.close()
    return actualizado


# pre:  el usuario está autenticado en el sistema (Solo Admin). item_id es un entero positivo en la URL.
# post: retorna 200 si se dio de baja con éxito, 404 si el ítem no existe, 400 si el ID es inválido.
@blueprint_inventario.route("/api/items/<int:item_id>", methods=["DELETE"])
@login_required
def eliminar_item(item_id):
    if item_id <= 0:
        return jsonify({"error": "ID inválido"}), HTTP_BAD_REQUEST

    if dar_de_baja_item_db(item_id):
        return jsonify({"mensaje": "Artículo dado de baja con éxito"}), HTTP_OK

    return jsonify({"error": "Artículo no encontrado"}), HTTP_NOT_FOUND
