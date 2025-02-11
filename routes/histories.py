import pymongo
from flask import Blueprint, request, jsonify
from db import get_db
from bson.objectid import ObjectId

# Khởi tạo Blueprint
history_bp = Blueprint("history", __name__)
db = get_db()
histories_collection = db["histories"]  # Collection MongoDB
parking_collection = db["parkings"]

@history_bp.route("/", methods=["POST"])
def add_history():
    try:
        # Lấy dữ liệu từ request body
        data = request.get_json()

        # Kiểm tra các trường bắt buộc
        if not all(key in data for key in ("user_id", "parking_id", "license", "time_in", "time_out", "parking_time")):
            return jsonify({"error": "Missing required fields"}), 400

        # Kiểm tra user_id tồn tại
        if not db["users"].find_one({"user_id": data["user_id"]}):
            return jsonify({"error": f"user_id {data['user_id']} does not exist"}), 400

        # Kiểm tra parking_id tồn tại
        parking = db["parkings"].find_one({"_id": data["parking_id"]})
        if not parking:
            return jsonify({"error": f"parking_id {data['parking_id']} does not exist"}), 400


        # Kiểm tra định dạng thời gian
        from datetime import datetime
        try:
            time_in = datetime.fromisoformat(data["time_in"])
            time_out = datetime.fromisoformat(data["time_out"])
            if time_out < time_in:
                return jsonify({"error": "time_out must be greater than time_in"}), 400
        except ValueError:
            return jsonify({"error": "Invalid date format for time_in or time_out"}), 400


        # Tạo đối tượng History
        history = {
            "user_id": data["user_id"],
            "parking_id": data["parking_id"],
            "license": data["license"],
            "time_in": data["time_in"],
            "time_out": data["time_out"],
            "parking_time": data["parking_time"]
        }

        # Thêm vào MongoDB
        result = histories_collection.insert_one(history)

        return jsonify({"message": "History added successfully", "id": str(result.inserted_id)}), 201

    except pymongo.errors.PyMongoError as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500
@history_bp.route('/get_parking_histories', methods=['POST'])
def get_parking_histories():
    try:
        # Lấy dữ liệu từ request
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"status": "error", "message": "user_id is required"}), 400

        # Tìm tất cả lịch sử của user_id
        histories = list(histories_collection.find({"user_id": user_id}))
        if not histories:
            return jsonify({"status": "error", "message": "No histories found for this user"}), 404

        # Lấy thông tin bãi đỗ xe và chuẩn bị dữ liệu trả về
        response_data = []
        for history in histories:
            parking = parking_collection.find_one({"_id": history["parking_id"]})
            if parking:
                response_data.append({
                    "parking_name": parking["parking_name"],
                    "license": history["license"],
                    "parking_time": history["parking_time"],
                    "time_in" : history["time_in"],
                    "time_out": history["time_out"]
                })

        return jsonify({
            "status": "success",
            "message": "Parking histories retrieved successfully",
            "data": response_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500