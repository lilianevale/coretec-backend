from flask import Blueprint, request, jsonify
from app.utils.calculos import diagrama_magnel
import pandas as pd

magnel_bp = Blueprint('magnel', __name__)

resultado0, resultado1, resultado2, resultado3 = '', '', '', ''
response_data = {}


@magnel_bp.route('/magnel', methods=['POST', 'GET'])
def handle_magnel():
    global resultado0, resultado1, resultado2, resultado3, response_data

    if request.method == 'POST':
        data = request.get_json()

        areabruta = float(data.get('areabruta1'))
        distopo = float(data.get('distopo1'))
        disbase = float(data.get('disbase1'))
        inercia = float(data.get('inercia1'))
        tensmin = float(data.get('tensmin1'))
        tensmax = float(data.get('tensmax1'))
        fletor = float(data.get('fletor1'))

        resultado0, resultado1, resultado2, resultado3 = diagrama_magnel(
            areabruta, distopo, disbase, inercia, tensmax, tensmin, fletor
        )

        return jsonify({
            'equacao_reta_0': resultado0,
            'equacao_reta_1': resultado1,
            'equacao_reta_2': resultado2,
            'equacao_reta_3': resultado3
        })

    elif request.method == 'GET':
        return jsonify({
            'equacao_reta_0': resultado0,
            'equacao_reta_1': resultado1,
            'equacao_reta_2': resultado2,
            'equacao_reta_3': resultado3
        })
