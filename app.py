from flask import Flask,jsonify
from config import DevelopmentConfig
from routes.tasks import task_bp

def create_app(config_class=DevelopmentConfig):
    app=Flask(__name__)
    app.config.from_object(config_class)
    app.register_blueprint(task_bp)


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