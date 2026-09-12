from flask import Blueprint, request

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.route("/getReport", methods = ["GET"])
def generateReport():
    user_id = request.args.get("userId") or request.form.get("userId")
    
   
