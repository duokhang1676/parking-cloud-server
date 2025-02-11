from flask import Blueprint, request, jsonify
from db import get_db
from bson.objectid import ObjectId

# Khởi tạo Blueprint
parking_area_bp = Blueprint("parking_area", __name__)
db = get_db()
parking_areas_collection = db["parking_areas"]  
parking_collection = db["parkings"]

@parking_area_bp.route("/", methods=["POST"])
def add_or_update_parking_area():
    try:
        # Lấy dữ liệu từ request body
        data = request.get_json()

        # Kiểm tra các trường bắt buộc
        if not all(key in data for key in ("parking_id", "area_name", "available", "occupied", "total")):
            return jsonify({"error": "Missing required fields"}), 400

        # Kiểm tra xem parking_id và area_name đã tồn tại chưa
        existing_parking_area = parking_areas_collection.find_one({
            "parking_id": data["parking_id"],
            "area_name": data["area_name"]
        })

        if existing_parking_area:
            # Cập nhật thông tin của parking_area
            update_result = parking_areas_collection.update_one(
                {"_id": existing_parking_area["_id"]},
                {"$set": {
                    "available": data["available"],
                    "occupied": data["occupied"],
                    "total": data["total"]
                }}
            )

            if update_result.modified_count > 0:
                return jsonify({"message": "Parking area updated successfully"}), 200
            else:
                return jsonify({"message": "Parking area already up-to-date"}), 200
        else:
            # Tạo đối tượng Parking_Area mới
            parking_area = {
                "parking_id": data["parking_id"],
                "area_name": data["area_name"],
                "available": data["available"],
                "occupied": data["occupied"],
                "total": data["total"]
            }

            # Thêm vào MongoDB
            result = parking_areas_collection.insert_one(parking_area)

            return jsonify({"message": "Parking area added successfully", "id": str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@parking_area_bp.route('/get_parking_areas', methods=['POST'])
def get_parking_areas():
    try:
        # Nhận dữ liệu từ request
        data = request.get_json()
        parking_name = data.get("parking_name")
        address = data.get("address")

        if not parking_name or not address:
            return jsonify({"status": "error", "message": "Both parking_name and address are required"}), 400

        # Tìm _id của bãi đỗ xe từ collection parking
        parking_doc = parking_collection.find_one({"parking_name": parking_name, "address": address})
        
        if not parking_doc:
            return jsonify({"status": "error", "message": "Parking not found"}), 404

        parking_id = parking_doc['_id']  # Lấy _id của bãi đỗ xe

        # Tìm tất cả các khu vực liên quan trong collection parking_areas
        parking_areas = list(parking_areas_collection.find({"parking_id": str(parking_id)}, {"_id": 0}))

        if not parking_areas:
            return jsonify({"status": "error", "message": "No parking areas found for the given parking"}), 404

        # Chuẩn bị phản hồi
        response = {
            "status": "success",
            "message": "Parking areas retrieved successfully",
            "areas": parking_areas
            
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500