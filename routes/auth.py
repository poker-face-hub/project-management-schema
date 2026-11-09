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
        raise ValidationError

    name=data.get("name",None)
    username=data.get("username",None)
    age=data.get("age",None)
    email=data.get("email",None)
    password=data.get("password",None)

    
      
    user_id=AuthService.register_user(name=name,username=username,age=age,email=email,password=password)
    return jsonify({"message": "user registered successfully ", "user_id": user_id}),201

    

@auth_bp.route("/login",methods=["POST"])
def login():
    data=request.get_json(silent=True) 
    if not data:
        raise ValidationError
    
    username=data.get("username",None)
    password=data.get("password",None)
          
    if AuthService.login(username=username,password=password):
        return jsonify({"message": "user log in successful "}),200
    else:
            return jsonify({"error": "Invalid username or password"}),401


@auth_bp.route("/logout",methods=["POST"])
def logout():
     AuthService.logout()
     return jsonify({"messege": "Logged out successfully ."}),200
    

