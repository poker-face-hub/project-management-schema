import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Blueprint,jsonify,request,session
from services import ReportService
from exception import RecordNotFoundError,ValidationError

report_bp=Blueprint("report",__name__,url_prefix="/report")


@report_bp.route("",methods=["GET"])
def get_user_summary():

    user_id=session.get("user_id",None)
    if  user_id is None:
            return jsonify({"error": "Unauthorized. Please log in first."}),401


    project_id=request.args.get("project_id",None)
    
    try:
    
        projects=ReportService.get_user_summary(user_id=user_id,project_id=project_id)
        if projects:
            return jsonify({"summary": projects}),200
        else:
            return jsonify({"message":"no project to show"}),200

    except ValidationError as e:
                 return jsonify({"error": f"invalod project id: {str(e)}"}),401
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to report summary: {str(e)}"}), 400
