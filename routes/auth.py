import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Blueprint,jsonify,request,session
from exception import RecordNotFoundError,ValidationError
from services import AuthService

auth_bp=Blueprint("auth",__name__,url_prefix="/auth")


@auth_bp.route("/register",methods=["POST"])
def register():
    data=request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload" }),400


    name=data.get("name",None)
    username=data.get("username",None)
    age=data.get("age",None)
    email=data.get("email",None)
    password=data.get("password",None)

    
    try:   
        user_id=AuthService.register_user(name=name,username=username,age=age,email=email,password=password)
        return jsonify({"message": "user registered successfully ", "user_id": user_id}),201
    
    except RecordNotFoundError as e:
                return jsonify({"error": f"missing requirements"}),404
    except ValidationError as e:
          return jsonify({"error": f"invalid data . {str(e)}"}),401
    except Exception as e:
            return jsonify({"error": f"Failed to create pregister user .  {str(e)}"}),500



    

@auth_bp.route("/login",methods=["POST"])
def login():
    data=request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload" }),400
    
    username=data.get("username",None)
    password=data.get("password",None)

    
    
    try:      
        if AuthService.login(username=username,password=password):
            return jsonify({"message": "user log in successful "}),200
        else:
                return jsonify({"error": "Invalid username or password"}),401
    except RecordNotFoundError as e:
            return jsonify({"error": f"missing username or password"}),404
    except Exception as e:
            return jsonify({"error": f"Failed to log in  .  {str(e)}"}),500


@auth_bp.route("/logout",methods=["POST"])
def logout():
     AuthService.logout()
     return jsonify({"messege": "Logged out successfully ."}),200
    

