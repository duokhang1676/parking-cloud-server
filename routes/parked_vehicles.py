from flask import Blueprint, request, jsonify
from db import get_db

parked_vehicle_bp = Blueprint("parked_vehicle", __name__)
db = get_db()
parked_vehicle_collection = db["parked_vehicles"]
parking_collection = db["parking"]

# get parked vehicles by parking_id
@parked_vehicle_bp.route('/get_parked_vehicles', methods=['POST'])
def get_parked_vehicles():
    data = request.get_json()
    parking_id = data.get('parking_id')

    if not parking_id:
        return jsonify({'error': 'parking_id is required'}), 400

    try:
        parked_vehicles = parked_vehicle_collection.find_one({'parking_id': parking_id}, {'list': 1, '_id': 0})

        if not parked_vehicles:
            return jsonify({'error': 'Parking ID not found'}), 404

        return jsonify({'parked_vehicles': parked_vehicles.get('list', [])}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# add vehicle to list
@parked_vehicle_bp.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    parking_id = data.get('parking_id')
    vehicle = data.get('vehicle')

    if not parking_id or not vehicle:
        return jsonify({'error': 'parking_id and vehicle data are required'}), 400

    try:
        result = parked_vehicle_collection.update_one(
            {'parking_id': parking_id},
            {'$push': {'list': vehicle}}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Parking ID not found'}), 404

        return jsonify({'message': 'Vehicle added successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# remove vehicle from list
@parked_vehicle_bp.route('/remove_vehicle', methods=['DELETE'])
def remove_vehicle():
    data = request.get_json()
    parking_id = data.get('parking_id')
    user_id = data.get('user_id')
    license_plate = data.get('license_plate')

    if not parking_id or not user_id or not license_plate:
        return jsonify({'error': 'parking_id, user_id, and license_plate are required'}), 400

    try:
        result = parked_vehicle_collection.update_one(
            {'parking_id': parking_id},
            {'$pull': {'list': {'user_id': user_id, 'license_plate': license_plate}}}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Parking ID not found'}), 404

        return jsonify({'message': 'Vehicle removed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# update slot_name and num_slot
@parked_vehicle_bp.route('/update_vehicle', methods=['PUT'])
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
        result = parked_vehicle_collection.update_one(
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
    
# update entire list
@parked_vehicle_bp.route('/update_vehicle_list', methods=['PUT'])
def update_vehicle_list():
    data = request.get_json()
    parking_id = data.get('parking_id')
    new_list = data.get('list')

    if not parking_id or not new_list:
        return jsonify({'error': 'parking_id and list are required'}), 400

    try:
        result = parked_vehicle_collection.update_one(
            {'parking_id': parking_id},
            {'$set': {'list': new_list}}
        )

        if result.matched_count == 0:
            return jsonify({'error': 'Parking ID not found'}), 404

        return jsonify({'message': 'List updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@parked_vehicle_bp.route("/get_user_parked_vehicles", methods=["POST"])
def get_user_parked_vehicles():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "Missing 'user_id'"}), 400

    # Lấy tất cả document có user_id trong list
    parked_docs = list(parked_vehicle_collection.find(
        {"list.user_id": user_id},
        {"_id": 0, "parking_id": 1, "list": 1}
    ))

    if not parked_docs:
        return jsonify({"status": "success", "data": []}), 200

    # Map parking_id -> thông tin bãi xe
    parking_ids = [doc["parking_id"] for doc in parked_docs]
    parking_info_map = {
        p["parking_id"]: {
            "parking_name": p["parking_name"],
            "address": p["address"],
            "status": p["status"]
        }
        for p in parking_collection.find(
            {"parking_id": {"$in": parking_ids}},
            {"_id": 0, "parking_id": 1, "parking_name": 1, "address": 1, "status": 1}
        )
    }

    # Gom dữ liệu trả ra
    result = []
    for doc in parked_docs:
        parking_id = doc["parking_id"]
        parking_info = parking_info_map.get(parking_id, {})

        for vehicle in doc["list"]:
            if vehicle["user_id"] == user_id:
                result.append({
                    "license_plate": vehicle["license_plate"],
                    "slot_name": vehicle["slot_name"],
                    "time_in": vehicle["time_in"],
                    "customer_type": vehicle["customer_type"],
                    "parking_id": parking_id,
                    "parking_name": parking_info.get("parking_name", "Unknown"),
                    "address": parking_info.get("address", "Unknown"),
                    "status": parking_info.get("status", "Unknown")
                })

    return jsonify({"status": "success", "data": result}), 200