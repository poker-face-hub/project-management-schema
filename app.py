import os
from flask import Flask,jsonify
from config import DevelopmentConfig
from models import db, UserModel, ProjectModel, MilestoneModel, TaskModel
from exception import RecordNotFoundError,ValidationError,UnauthorizedError
from routes.tasks import task_bp
from routes.projects import project_bp
from routes.auth import auth_bp
from routes.milestone import milestone_bp
from routes.report import report_bp





def create_app(config_class=DevelopmentConfig):
    app=Flask(__name__)
    app.secret_key=os.environ.get("FLASK-SECRET-KEY","dev-secret-key-fallback-for-testing")
    app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        db.create_all()

        
    app.register_blueprint(task_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(milestone_bp)
    app.register_blueprint(report_bp)


    @app.route("/",methods=["GET"])
    @app.route("/health",methods=["GET"])
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "server is running",
            "DEBUG": app.config["DEBUG"],
        }),200
    

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        error_message=str(e) if str(e) else "Invalid input data or missing required fields . "
        return jsonify({"error": error_message}),400


    @app.errorhandler(RecordNotFoundError)
    def handler_not_found_error(e):
        error_message = str(e) if str(e) else "Requested record does not exist."
        return jsonify({"error": error_message}), 404
    


    @app.errorhandler(UnauthorizedError)
    def handler_Unauthorized_error(e):
        return jsonify({"error": f"Unauthorized Request : {str(e)}"}), 401
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    return app


    
if __name__=="__main__":
    app=create_app(DevelopmentConfig)
    app.run(debug=app.config["DEBUG"],port=5000)