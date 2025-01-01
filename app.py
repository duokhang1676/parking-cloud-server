from flask import Flask
from routes.users import user_bp
from routes.parking import parking_bp
from routes.registers import register_bp
from routes.customers import customer_bp
from routes.parking_areas import parking_area_bp
from routes.histories import history_bp

# Tạo ứng dụng Flask
app = Flask(__name__)

# Đăng ký các Blueprint
app.register_blueprint(user_bp, url_prefix="/api/users")
app.register_blueprint(parking_bp, url_prefix="/api/parking")
app.register_blueprint(register_bp, url_prefix="/api/registers")
app.register_blueprint(customer_bp, url_prefix="/api/customers")
app.register_blueprint(parking_area_bp, url_prefix="/api/parking_areas")
app.register_blueprint(history_bp, url_prefix="/api/histories")

@app.route("/")
def index():
    """
    Route kiểm tra server.
    """
    return "Parking Management API is running!", 200

# Điểm khởi chạy server
if __name__ == "__main__":
    app.run(debug=True)
