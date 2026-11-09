import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Blueprint,jsonify,request,session
from exception import RecordNotFoundError,ValidationError,UnauthorizedError
from services import TaskService


task_bp=Blueprint("tasks",__name__,url_prefix="/task")

@task_bp.route("",methods=["GET"])
def get_all_tasks():
    user_id = session.get("user_id")
    if not user_id:
        raise UnauthorizedError
    keyword=request.args.get("keyword",None)
    user_id=int(user_id)
    milestone_id=request.args.get("milestone_id",None)
    project_id=request.args.get("project_id",None)
    
    tasks=TaskService.search_tasks(keywords=keyword,user_id=user_id,milestone_id=milestone_id,project_id=project_id)
    return jsonify({"Tasks":tasks}),200
        
        
@task_bp.route("",methods=["POST"])
def add_task():
    user_id = session.get("user_id")
    if  user_id is None:
             raise UnauthorizedError
        
    data=request.get_json(silent=True)
    if not data:
        raise ValidationError
    
    name=data.get("name",None)
    milestone_id=data.get("milestone_id",None)
    project_id=data.get("project_id",None)

    
    task_id=TaskService.add_task(name,user_id,milestone_id,project_id)
    return jsonify({"message": "Task created", "task_id": task_id}),201

    

@task_bp.route("/<int:task_id>",methods=["DELETE"])
def delete_task_by_id(task_id):
    user_id = session.get("user_id")
    if not user_id:
        raise UnauthorizedError
    
    if TaskService.delete_task(task_id=task_id,user_id=user_id):
        return jsonify({"message": f"Task {task_id} deleted successfully"}),200




@task_bp.route("/<int:task_id>",methods=["PUT"])
def update_task_by_id(task_id):
    user_id = session.get("user_id")
    if  user_id is None:
             raise UnauthorizedError
        
    data=request.get_json(silent=True)
    if not data:
        raise ValidationError
    
    new_status=data.get("status",None)
    name=data.get("name",None)
    milestone_id=data.get("milestone_id",None)
    project_id=data.get("project_id",None)

    
             
    if TaskService.update_task(task_id=task_id,new_status=new_status,name=name,user_id=user_id,milestone_id=milestone_id,project_id=project_id):
        return jsonify({"message": f"Task {task_id} updated successfully"}),200
    else:
        return jsonify({"error": f"Failed to update task. Verify that status,name, user_id, project_id, and milestone_id provided."}),400
