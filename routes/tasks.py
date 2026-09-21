import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Blueprint,jsonify,request
from manager import Datamanager


task_bp=Blueprint("tasks",__name__,url_prefix="/task")

@task_bp.route("",methods=["GET"])
def get_all_tasks():
    keyword=request.args.get("keyword",None)
    user_id=request.args.get("user_id",None)
    milestone_id=request.args.get("milestone_id",None)
    project_id=request.args.get("project_id",None)
    try:
        if user_id is not None:
            user_id=int(user_id)
        if milestone_id is not None:
            milestone_id=int(milestone_id)
        if project_id is not None:
            project_id=int(project_id)
    except ValueError as e:
        return jsonify({"Error": f"Invalid query parameter. user_id, milestone_id, and project_id must be integers. str({e})"}),400
    with Datamanager() as db:
        tasks=db.search_tasks(keywords=keyword,user_id=user_id,milestone_id=milestone_id,project_id=project_id)
        return jsonify({"Tasks":tasks}),200
    
@task_bp.route("",methods=["POST"])
def add_task():

    data=request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload" }),400

    name=data.get("name",None)
    user_id=data.get("user_id",None)
    milestone_id=data.get("milestone_id",None)
    project_id=data.get("project_id",None)

    if  name is None or user_id is None or milestone_id is None or project_id is None:
        return jsonify({"error": "missing information..required fields: name,user_id,milestone_id,project_id "}),400
    try:
        with Datamanager() as db:
            task_id=db.add_task(name,user_id,milestone_id,project_id)
            return jsonify({"message": "Task created", "task_id": task_id}),201
        
    except Exception as e:
        return jsonify({"error": f"Failed to create task. Verify that user_id, project_id, and milestone_id exist.  {str(e)}"}),400


@task_bp.route("/<int:task_id>",methods=["DELETE"])
def delete_task_by_id(task_id):
    try:
        with Datamanager() as db:
            result=db.task_exists(task_id)
            if not result :
                return jsonify({"error": f"Task {task_id} does not exists"}),404

            success=db.delete_task(task_id)
            if success:
                return jsonify({"message": f"Task {task_id} deleted successfully"}),200
    except Exception as e:
            return jsonify({"error": f"could Not delete task {str(e)}"}),400
