from flask import Blueprint, request, jsonify
from db import get_db

# Khởi tạo Blueprint cho parking
parking_bp = Blueprint("parking", __name__)
db = get_db()
parking_collection = db["parkings"]  # Collection cho Parking

# Lấy danh sách bãi đỗ xe
@parking_bp.route("/", methods=["GET"])
def get_parking():
    parking = list(parking_collection.find({}, {"_id": 0}))
    return jsonify(parking), 200
# Lấy bãi xe theo tên và địa chỉ
@parking_bp.route('/get_parking_id', methods=['POST'])
def get_parking_id():
    data = request.get_json()
    address = data.get("address")
    parking_name = data.get("parking_name")

    parking = parking_collection.find_one({"address": address, "parking_name": parking_name}, {"_id": 1})
    if parking:
        return jsonify({"parking_id": parking["_id"], "status": "success"}), 200
    return jsonify({"message": "Parking not found", "status": "fail"}), 404
# Tạo bãi đỗ xe mới
@parking_bp.route("/", methods=["POST"])
def create_parking():
    data = request.json
    if not all(key in data for key in ("parking_id", "parking_name", "address", "status")):
        return jsonify({"error": "Missing fields"}), 400

    # Kiểm tra nếu parking_id đã tồn tại
    if parking_collection.find_one({"parking_id": data["parking_id"]}):
        return jsonify({"error": "Parking already exists"}), 400

    parking_collection.insert_one(data)
    return jsonify({"message": "Parking created successfully"}), 201

@parking_bp.route('/get_parking_slot', methods=['POST'])
def get_parking_info():
    try:
        # Lấy dữ liệu từ request
        data = request.get_json()
        parking_name = data.get("parking_name")
        address = data.get("address")

        if not parking_name or not address:
            return jsonify({"status": "error", "message": "parking_name and address are required"}), 400

        # Tìm kiếm trong collection
        parking_doc = parking_collection.find_one(
            {"parking_name": parking_name, "address": address},
            {"_id": 0, "parking_areas": 1}
        )

        if not parking_doc:
            return jsonify({"status": "error", "message": "Parking not found"}), 404

        # Trả về thông tin
        return jsonify({
            "status": "success",
            "message": "Parking data retrieved successfully",
            "data": parking_doc["parking_areas"]
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
