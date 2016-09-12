"""This module provides views for application."""
from tof_server import app, versioning, mysql, randcoder
from tof_server import player_validator, map_validator, map_model
from flask import jsonify, request, abort

@app.route('/players', methods=['POST'])
def generate_new_id():
    """Method for generating new unique player ids"""
    validation = versioning.validate(request)
    if validation['status'] != 'ok':
        abort(validation['code'])

    cursor = mysql.connection.cursor()
    new_pin = randcoder.get_random_code(8)

    insert_sql = "INSERT INTO players (auto_pin) VALUES (%s)"
    id_sql = "SELECT LAST_INSERT_ID()"

    cursor.execute(insert_sql, (new_pin,))
    cursor.execute(id_sql)

    insert_data = cursor.fetchone()

    mysql.connection.commit()
    cursor.close()

    return jsonify({
        'id' : insert_data[0],
        'pin' : new_pin
    })

@app.route('/maps', methods=['POST'])
def upload_new_map():
    """Method for uploading new map"""
    validation = versioning.validate(request)
    if validation['status'] != 'ok':
        abort(validation['code'])

    cursor = mysql.connection.cursor()

    validation = player_validator.validate(request, cursor)
    if validation['status'] != 'ok':
        abort(validation['code'])

    validation = map_validator.validate(request.json['data'], cursor)
    if validation['status'] != 'ok':
        abort(validation['code'])

    if not validation['found']:
        map_model.persist_map(request.json['data'],
                              validation,
                              cursor,
                              request.json['player_id'])

    mysql.connection.commit()
    cursor.close()

    return jsonify({
        'code' : validation['code']
    })

@app.route('/maps/<string:map_code>.json', methods=['GET'])
def download_map(map_code):
    """Method for downloading a map"""
    validation = versioning.validate(request)
    if validation['status'] != 'ok':
        abort(validation['code'])

    cursor = mysql.connection.cursor()
    map_data = map_model.find_map(map_code, cursor)
    cursor.close()

    if map_data == None:
        abort(404)

    return jsonify({
        'code' : map_code,
        'data' : map_data
    })
