import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Blueprint,jsonify,request,session
from services import ReportService
from exception import RecordNotFoundError,ValidationError,UnauthorizedError

report_bp=Blueprint("report",__name__,url_prefix="/report")


@report_bp.route("",methods=["GET"])
def get_user_summary():

    user_id=session.get("user_id",None)
    if  user_id is None:
            raise UnauthorizedError

    project_id=request.args.get("project_id",None)
    
   
    
    projects=ReportService.get_user_summary(user_id=user_id,project_id=project_id)
    if projects:
        return jsonify({"summary": projects}),200
    else:
        return jsonify({"message":"no project to show"}),200

