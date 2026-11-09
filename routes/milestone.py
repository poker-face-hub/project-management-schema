import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Blueprint,jsonify,request,session
from exception import RecordNotFoundError,ValidationError
from services import MilestoneService

milestone_bp=Blueprint("milestone",__name__,url_prefix="/milestone")


@milestone_bp.route("",methods=["POST"])
def add_milestone():
    user_id=session.get("user_id",None)
    if  user_id is None:
         return jsonify({"error": "Unauthorized. Please log in first."}),401
    
    data=request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload" }),400

    name=data.get("name",None)
    project_id=data.get("project_id",None)
    due_date=data.get("due_date",None)
   

    try: 
        milestone_id=MilestoneService.add_milestone(user_id=user_id,name=name,project_id=project_id,due_date=due_date)
        return jsonify({"message": "milestone created", "milestone_id": milestone_id}),201
    
    except RecordNotFoundError as e:
        return jsonify({"error": f"missing information..required fields: name,project_id,due_date : {str(e)}"}),404
    except ValidationError as e :
        return jsonify({"error": str(e)}),400
    except Exception as e:
        return jsonify({"error": f"Failed to create milestone. Verify that name, project_id are valid .  {str(e)}"}),500
    

@milestone_bp.route("",methods=["GET"])
def search_milestone():
    user_id=session.get("user_id",None)
    if  user_id is None:
            return jsonify({"error": "Unauthorized. Please log in first."}),401
    project_id=request.args.get("project_id",None)
    keywords=request.args.get("keywords",None)
    try:
        milestone=MilestoneService.search_milestone(user_id=user_id,project_id=project_id,keywords=keywords)
        return jsonify({"milestone": milestone}),200
    
    except ValidationError as e :
        return jsonify({"error": str(e)}),400
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve milestone: {str(e)}"}), 400


@milestone_bp.route("/<int:milestone_id>",methods=["DELETE"])
def delete_milestone(milestone_id):
    user_id=session.get("user_id",None)
    if  user_id is None:
            return jsonify({"error": "Unauthorized. Please log in first."}),401
    try:
        if MilestoneService.delete_milestone(milestone_id=milestone_id,user_id=user_id):
            return jsonify({"message": f"{milestone_id} milestone deleted successfully ." }),201

    except RecordNotFoundError as e :
         return jsonify({"error": str(e)}),404

    except ValidationError as e:
         return jsonify({"error": str(e)}),400
         
    except Exception as e :
         return jsonify({"error": str(e)}),500
         

@milestone_bp.route("<int:milestone_id>",methods=["PUT"])
def update_milestone(milestone_id):
    user_id=session.get("user_id",None)
    if  user_id is None:
            return jsonify({"error": "Unauthorized. Please log in first."}),401
    data=request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload" }),400

    name=data.get("name",None)
    due_date=data.get("due_date",None)
    
    try:
        if MilestoneService.update_milestone(milestone_id=milestone_id,user_id=user_id,name=name,due_date=due_date):
            return jsonify({"message": f"{milestone_id} milestone updated successfully ." }),201
        else:
            return jsonify({"message": f"{milestone_id} milestone not updated ." }),200

    
    except RecordNotFoundError as e :
            return jsonify({"error": str(e)}),404
    except Exception as e :
          return jsonify({"error": str(e)}),500
         

