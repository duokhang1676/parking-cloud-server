from flask import Blueprint, request, jsonify
from db import get_db
from datetime import datetime, timedelta
import json
from bson import json_util

# Khởi tạo Blueprint cho register
register_bp = Blueprint("register", __name__)
db = get_db()
register_collection = db["register"]  # Collection cho Register

# Lấy danh sách đăng ký
@register_bp.route("/", methods=["GET"])
def get_registers():
    registers = list(register_collection.find({}, {"_id": 0}))
    return jsonify(registers), 200

@register_bp.route('/get_register_list', methods=['POST'])
def get_register_list():
    try:
        # Lấy dữ liệu từ request
        data = request.get_json()
        parking_id = data.get("parking_id")

        if not parking_id:
            return jsonify({"status": "error", "message": "parking_id is required"}), 400

        # Tìm tài liệu `registers` theo parking_id
        registers_doc = register_collection.find({"parking_id": parking_id}, {"_id":0,"parking_id":0})
        registers_list = list(registers_doc)
        registers_json = json.loads(json_util.dumps(registers_list))
        print(registers_json)
        if not registers_doc:
            return jsonify({"status": "error", "message": "No registers found for this parking_id"}), 404

        # Chuẩn bị phản hồi
        response = {
            "status": "success",
            "message": "Registers retrieved successfully",
            "data": registers_json
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@register_bp.route('/register_parking', methods=['POST'])
def register_parking():
    data = request.get_json()

    user_id = data.get("user_id")
    parking_id = data.get("parking_id")
    license_plate = data.get("license_plate")

    if not user_id or not parking_id or not license_plate:
        return jsonify({"message": "Missing required fields", "status": "fail"}), 400

    # Kiểm tra thông tin đã đăng ký và còn hiệu lực
    existing_register = register_collection.find_one({
        "user_id": user_id,
        "parking_id": parking_id,
        "register_list.license_plate": license_plate
    })

    if existing_register:
        # Kiểm tra thời gian hiệu lực
        for reg in existing_register.get("register_list", []):
            if reg["license_plate"] == license_plate and reg["expired"] > datetime.now():
                return jsonify({"message": "License plate already registered and still valid", "status": "exists"}), 409

    # Thêm mới thông tin nếu không còn hiệu lực hoặc chưa đăng ký
    register_data = {
        "license_plate": license_plate,
        "register_time": datetime.now(),
        "expired": datetime.now() + timedelta(days=30)  # Đăng ký 1 tháng
    }

    # Cập nhật hoặc thêm mới vào cơ sở dữ liệu
    register_collection.update_one(
        {"user_id": user_id, "parking_id": parking_id},
        {"$push": {"register_list": register_data}},
        upsert=True
    )

    return jsonify({"message": "Registration successful", "status": "success"}), 201

