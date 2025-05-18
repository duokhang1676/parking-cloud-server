from flask import Blueprint, request, jsonify
from db import get_db

parked_vehicles_bp = Blueprint("parked_vehicle", __name__)
db = get_db()
parked_vehicle_collection = db["parked_vehicles"]
parking_collection = db["parkings"]


# get parked vehicles by parking_id
@parked_vehicles_bp.route('/get_parked_vehicles', methods=['POST'])
def get_parked_vehicles():
    data = request.get_json()
    parking_id = data.get('parking_id')

    if not parking_id:
        return jsonify({'error': 'parking_id is required'}), 400

    try:
        parked_vehicles = parking_collection.find_one({'parking_id': parking_id}, {'list': 1, '_id': 0})

        if not parked_vehicles:
            return jsonify({'error': 'Parking ID not found'}), 404

        return jsonify({'parked_vehicles': parked_vehicles.get('list', [])}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# add vehicle to list
@parked_vehicles_bp.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    parking_id = data.get('parking_id')
    vehicle = data.get('vehicle')

    if not parking_id or not vehicle:
        return jsonify({'error': 'parking_id and vehicle data are required'}), 400

    try:
        result = parking_collection.update_one(
            {'parking_id': parking_id},
            {'$push': {'list': vehicle}}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Parking ID not found'}), 404

        return jsonify({'message': 'Vehicle added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# remove vehicle from list
@parked_vehicles_bp.route('/remove_vehicle', methods=['DELETE'])
def remove_vehicle():
    data = request.get_json()
    parking_id = data.get('parking_id')
    user_id = data.get('user_id')
    license_plate = data.get('license_plate')

    if not parking_id or not user_id or not license_plate:
        return jsonify({'error': 'parking_id, user_id, and license_plate are required'}), 400

    try:
        result = parking_collection.update_one(
            {'parking_id': parking_id},
            {'$pull': {'list': {'user_id': user_id, 'license_plate': license_plate}}}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Parking ID not found'}), 404

        return jsonify({'message': 'Vehicle removed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# update slot_name and num_slot
@parked_vehicles_bp.route('/update_vehicle', methods=['PUT'])
def update_vehicle():
    data = request.get_json()
    parking_id = data.get('parking_id')
    user_id = data.get('user_id')
    license_plate = data.get('license_plate')
    slot_name = data.get('slot_name')
    num_slot = data.get('num_slot')

    if not parking_id or not user_id or not license_plate:
        return jsonify({'error': 'parking_id, user_id, and license_plate are required'}), 400

    try:
        result = parking_collection.update_one(
            {
                'parking_id': parking_id,
                'list.user_id': user_id,
                'list.license_plate': license_plate
            },
            {
                '$set': {
                    'list.$.slot_name': slot_name,
                    'list.$.num_slot': num_slot
                }
            }
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Vehicle not found'}), 404

        return jsonify({'message': 'Vehicle updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
