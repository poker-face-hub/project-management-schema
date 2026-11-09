import os
from flask import Flask,jsonify
from config import DevelopmentConfig
#from exception import RecordNotFoundError,ValidationError,UnauthorizedError
from routes.tasks import task_bp
from routes.projects import project_bp
from routes.auth import auth_bp
from routes.milestone import milestone_bp
from routes.report import report_bp





def create_app(config_class=DevelopmentConfig):
    app=Flask(__name__)
    app.secret_key=os.environ.get("FLASK-SECRET-KEY","dev-secret-key-fallback-for-testing")
    app.config.from_object(config_class)
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
    

    
    return app


    
if __name__=="__main__":
    app=create_app(DevelopmentConfig)
    app.run(debug=app.config["DEBUG"],port=5000)