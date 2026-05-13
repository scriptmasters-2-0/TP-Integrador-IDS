from flask import jsonify

def respuesta_json(exito, mensaje, datos=None, codigo_estado=200):
    respuesta = {
        "exito": exito,
        "mensaje": mensaje,
        "datos": datos if datos is not None else []
    }
    return jsonify(respuesta), codigo_estado