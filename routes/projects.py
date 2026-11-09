import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Blueprint,jsonify,request,session
from exception import RecordNotFoundError,ValidationError
from services import ProjectService

project_bp=Blueprint("projects",__name__,url_prefix="/project")


@project_bp.route("",methods=["POST"])
def add_project():
    user_id=session.get("user_id",None)
    if  user_id is None:
         return jsonify({"error": "Unauthorized. Please log in first."}),401
    
    data=request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload" }),400


    name=data.get("name",None)
    description=data.get("description",None)
    start_date=data.get("start_date",None)
    finish_date=data.get("finish_date",None)
    user_id=int(user_id)

      
    try:   
        project_id=ProjectService.add_project(name,description,user_id,start_date,finish_date)
        return jsonify({"message": "Project created", "project_id": project_id}),201

    except ValidationError as e:
         return jsonify({"error": "missing information..required fields: name,description,start_date,finish_date "}),404
            
    except Exception as e:
            return jsonify({"error": f"Failed to create project. Verify that name, desription, and dates are valid .  {str(e)}"}),400
    

@project_bp.route("",methods=["GET"])
def search_project():
    user_id=session.get("user_id",None)
    if  user_id is None:
            return jsonify({"error": "Unauthorized. Please log in first."}),401
    keywords=request.args.get("keywords",None)

    try: 
        projects=ProjectService.search_project(int(user_id),keywords=keywords)
        return jsonify({"projects": projects}),200
    
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve projects: {str(e)}"}), 400


@project_bp.route("/<int:project_id>",methods=["DELETE"])
def delete_project(project_id):
    user_id=session.get("user_id",None)
    if  user_id is None:
            return jsonify({"error": "Unauthorized. Please log in first."}),401
    try:
        if ProjectService.delete_project(project_id,int(user_id)):
            return jsonify({"message": f"{project_id} project deleted successfully ." }),201
        else:
             return jsonify({"error": f"project not deleted"}),400

    except RecordNotFoundError as e :
         return jsonify({"error": str(e)}),404

    except ValidationError as e:
         return jsonify({"error": str(e)}),400
         

    except Exception as e :
         return jsonify({"error": str(e)}),400
         

@project_bp.route("<int:project_id>",methods=["PUT"])
def update_projects(project_id):
    user_id=session.get("user_id",None)
    if  user_id is None:
            return jsonify({"error": "Unauthorized. Please log in first."}),401
    data=request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload" }),400

    name=data.get("name",None)
    description=data.get("description",None)
    start_date=data.get("start_date",None)
    finish_date=data.get("finish_date",None)

    try:
        if ProjectService.update_project(project_id=project_id,name=name,description=description,user_id=user_id,start_date=start_date,finish_date=finish_date):
            return jsonify({"message": f"{project_id} project updated successfully ." }),201
        else:
            return jsonify({"message": f"{project_id} project not updated ." }),200


    except RecordNotFoundError as e :
            return jsonify({"error": str(e)}),404

    except Exception as e :
              return jsonify({"error": str(e)}),500
             
    

