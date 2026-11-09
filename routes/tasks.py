import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Blueprint,jsonify,request,session
from exception import RecordNotFoundError,ValidationError
from services import TaskService


task_bp=Blueprint("tasks",__name__,url_prefix="/task")

@task_bp.route("",methods=["GET"])
def get_all_tasks():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401
    keyword=request.args.get("keyword",None)
    user_id=int(user_id)
    milestone_id=request.args.get("milestone_id",None)
    project_id=request.args.get("project_id",None)
    try:
        
        if milestone_id is not None:
            milestone_id=int(milestone_id)
        if project_id is not None:
            project_id=int(project_id)

        tasks=TaskService.search_tasks(keywords=keyword,user_id=user_id,milestone_id=milestone_id,project_id=project_id)
        return jsonify({"Tasks":tasks}),200
            
    except ValueError as e:
        return jsonify({"Error": f"Invalid query parameter. user_id, milestone_id, and project_id must be integers. str({e})"}),400
    
        
@task_bp.route("",methods=["POST"])
def add_task():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401

    data=request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload" }),400

    name=data.get("name",None)
    milestone_id=data.get("milestone_id",None)
    project_id=data.get("project_id",None)

    try:
        task_id=TaskService.add_task(name,user_id,milestone_id,project_id)
        return jsonify({"message": "Task created", "task_id": task_id}),201
    
    except ValidationError as e:
             return jsonify({"error": "invalid id or missing information."}),404
                
    except Exception as e:
        return jsonify({"error": f"Failed to create task. Verify that user_id, project_id, and milestone_id exist.  {str(e)}"}),400


@task_bp.route("/<int:task_id>",methods=["DELETE"])
def delete_task_by_id(task_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401
    try:
        if TaskService.delete_task(task_id=task_id,user_id=user_id):
            return jsonify({"message": f"Task {task_id} deleted successfully"}),200

    except RecordNotFoundError as e:
             return jsonify({"error": f"Task {task_id} does not exists"}),404 
    except ValidationError as e:
                 return jsonify({"error": "invalid id or missing information."}),404
    except Exception as e:
            return jsonify({"error": f"could Not delete task {str(e)}"}),400



@task_bp.route("/<int:task_id>",methods=["PUT"])
def update_task_by_id(task_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized. Please log in first."}), 401

    data=request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload" }),400

    new_status=data.get("status",None)
    name=data.get("name",None)
    milestone_id=data.get("milestone_id",None)
    project_id=data.get("project_id",None)

    
    try:         
        if TaskService.update_task(task_id=task_id,new_status=new_status,name=name,user_id=user_id,milestone_id=milestone_id,project_id=project_id):
            return jsonify({"message": f"Task {task_id} updated successfully"}),200
        else:
            return jsonify({"error": f"Failed to update task. Verify that status,name, user_id, project_id, and milestone_id provided."}),400
    except RecordNotFoundError as e:
         return jsonify({"error": f"Task {task_id} does not exists"}),404 
    except Exception as e:
        return jsonify({"error": f"Failed to update task. Verify that status,user_id, project_id, and milestone_id valid.  {str(e)}"}),400