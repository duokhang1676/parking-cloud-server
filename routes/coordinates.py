from flask import Blueprint, request, jsonify
from db import get_db

coordinates_bp = Blueprint("coordinates", __name__)
db = get_db()
coordinates_collection = db["coordinates"]
parking_collection = db["parkings"]

# get all coordinates
@coordinates_bp.route("/", methods=["GET"])
def get_coordinates():
    """
    Lấy danh sách tất cả các tọa độ.
    """
    coordinates = list(coordinates_collection.find({}, {"_id": 0}))
    return jsonify(coordinates), 200

# get coordinates by parking_id
@coordinates_bp.route("/get_coordinates", methods=["POST"])
def get_coordinates_by_parking_id():
    data = request.get_json()
    parking_id = data.get("parking_id")

    if not parking_id:
        return jsonify({"error": "parking_id is required"}), 400

    records = list(coordinates_collection.find({"parking_id": parking_id}, {"_id": 0}))
    
    if not records:
        return jsonify({"message": "No coordinates found for this parking_id"}), 404

    return jsonify({"status": "success", "data": records}), 200

# insert coordinates
@coordinates_bp.route("/insert_coordinates", methods=["POST"])
def insert_coordinates():
    data = request.get_json()

    required_fields = ["parking_id", "camera_id", "image_url", "coordinates_list"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Kiểm tra parking_id có tồn tại trong collection 'parkings'
    if not parking_collection.find_one({"parking_id": data["parking_id"]}):
        return jsonify({"error": f"Parking ID '{data['parking_id']}' does not exist"}), 400

    # Kiểm tra trùng lặp với parking_id + camera_id
    exists = coordinates_collection.find_one({
        "parking_id": data["parking_id"],
        "camera_id": data["camera_id"]
    })
    if exists:
        return jsonify({"error": "Coordinates for this parking_id and camera_id already exist"}), 400

    coordinates_collection.insert_one(data)
    return jsonify({"message": "Coordinates inserted successfully"}), 201

# udpate coordinates
@coordinates_bp.route("/update_coordinates", methods=["POST"])
def update_coordinates():
    data = request.get_json()
    parking_id = data.get("parking_id")
    camera_id = data.get("camera_id")

    if not parking_id or not camera_id:
        return jsonify({"error": "Missing 'parking_id' or 'camera_id'"}), 400

    # Loại bỏ parking_id và camera_id khỏi phần dữ liệu cần cập nhật
    update_data = {k: v for k, v in data.items() if k not in ("parking_id", "camera_id")}

    if not update_data:
        return jsonify({"error": "No fields to update"}), 400

    result = coordinates_collection.update_one(
        {"parking_id": parking_id, "camera_id": camera_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Coordinates not found"}), 404

    return jsonify({"message": "Coordinates updated successfully"}), 200

# # update coordinates
# @coordinates_bp.route("/update_coordinates", methods=["POST"])
# def update_coordinates():
#     data = request.get_json()
#     parking_id = data.get("parking_id")
#     camera_id = data.get("camera_id")

#     if not parking_id or not camera_id:
#         return jsonify({"error": "parking_id and camera_id are required"}), 400

#     update_fields = ["image_url", "coordinates_list"]
#     update_data = {k: v for k, v in data.items() if k in update_fields}

#     if not update_data:
#         return jsonify({"error": "No valid fields to update"}), 400

#     result = coordinates_collection.update_one(
#         {"parking_id": parking_id, "camera_id": camera_id},
#         {"$set": update_data}
#     )

#     if result.matched_count == 0:
#         return jsonify({"error": "Coordinates not found"}), 404

#     return jsonify({"message": "Coordinates updated successfully"}), 200
