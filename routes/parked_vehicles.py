from flask import Blueprint, request, jsonify
from db import get_db
from datetime import datetime, timezone, timedelta

parked_vehicle_bp = Blueprint("parked_vehicles", __name__)
db = get_db()
parked_vehicle_collection = db["parked_vehicles"]
parking_collection = db["parkings"]
parking_slots_collection = db["parking_slots"]


# get parked vehicles by parking_id
@parked_vehicle_bp.route('/get_parked_vehicles', methods=['POST'])
def get_parked_vehicles():
    try:
        data = request.get_json()
        parking_id = data.get("parking_id")

        if not parking_id:
            return jsonify({"message": "Missing parking_id", "status": "fail"}), 400

        doc = parked_vehicle_collection.find_one({"parking_id": parking_id}, {"_id": 0})
        if not doc:
            return jsonify({"message": "No data found", "status": "not_found"}), 404

        return jsonify({"message": "Success", "status": "success", "data": doc}), 200

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

# insert parked vehicles
@parked_vehicle_bp.route('/add_parked_vehicle', methods=['POST'])
def add_parked_vehicle():
    try:
        data = request.get_json()
        parking_id = data.get("parking_id")
        user_id = data.get("user_id")
        customer_type = data.get("customer_type")
        license_plate = data.get("license_plate")
        slot_name = data.get("slot_name")
        num_slot = data.get("num_slot")

        # Kiểm tra bắt buộc
        if not all([parking_id, user_id, customer_type, license_plate, slot_name, num_slot]):
            return jsonify({"message": "Missing required fields", "status": "fail"}), 400

        # Kiểm tra parking tồn tại
        if not parking_collection.find_one({"parking_id": parking_id}):
            return jsonify({"message": "Parking lot not found", "status": "not_found"}), 404

        # Kiểm tra slot_name chưa bị chiếm
        slot_doc = parking_slots_collection.find_one({"parking_id": parking_id})
        if slot_doc and slot_name in slot_doc.get("occupied_list", []):
            return jsonify({"message": "Slot is already occupied", "status": "slot_occupied"}), 409

        # Kiểm tra xe đã vào chưa
        if parked_vehicle_collection.find_one({"parking_id": parking_id, "list.license_plate": license_plate}):
            return jsonify({"message": "Vehicle already parked", "status": "duplicate"}), 409

        vehicle_data = {
            "user_id": user_id,
            "customer_type": customer_type,
            "time_in": datetime.now(timezone.utc),
            "license_plate": license_plate,
            "slot_name": slot_name,
            "num_slot": num_slot
        }

        # Ghi vào collection
        parked_vehicle_collection.update_one(
            {"parking_id": parking_id},
            {"$push": {"list": vehicle_data}},
            upsert=True
        )

        # Cập nhật trạng thái slot
        parking_slots_collection.update_one(
            {"parking_id": parking_id},
            {"$pull": {"available_list": slot_name}, "$push": {"occupied_list": slot_name}}
        )

        return jsonify({"message": "Vehicle added successfully", "status": "success"}), 201

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500
    
# update parked vehicles
@parked_vehicle_bp.route('/update_parked_vehicle', methods=['POST'])
def update_parked_vehicle():
    try:
        data = request.get_json()
        parking_id = data.get("parking_id")
        license_plate = data.get("license_plate")
        time_out = datetime.now(timezone.utc)

        if not parking_id or not license_plate:
            return jsonify({"message": "Missing required fields", "status": "fail"}), 400

        doc = parked_vehicle_collection.find_one({"parking_id": parking_id})
        if not doc:
            return jsonify({"message": "Parking lot not found", "status": "not_found"}), 404

        found = False
        for vehicle in doc["list"]:
            if vehicle["license_plate"] == license_plate and "time_out" not in vehicle:
                vehicle["time_out"] = time_out  # Ghi nhận thời điểm rời bãi
                slot_to_release = vehicle["slot_name"]
                found = True
                break

        if not found:
            return jsonify({"message": "Vehicle not found or already checked out", "status": "not_found"}), 404

        # Ghi lại danh sách đã cập nhật
        parked_vehicle_collection.update_one(
            {"parking_id": parking_id},
            {"$set": {"list": doc["list"]}}
        )

        # Cập nhật lại slot
        parked_vehicle_collection.update_one(
            {"parking_id": parking_id},
            {"$pull": {"occupied_list": slot_to_release}, "$addToSet": {"available_list": slot_to_release}}
        )

        return jsonify({"message": "Vehicle checked out successfully", "status": "success"}), 200

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

