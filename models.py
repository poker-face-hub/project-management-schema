from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

class UserModel(db.Model):
    __tablename__="User"

    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String,nullable=False)
    username=db.Column(db.String,unique=True,nullable=False)
    age=db.Column(db.Integer,nullable=False)
    email=db.Column(db.String,unique=True)
    password_hash=db.Column(db.String,nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class ProjectModel(db.Model):
    __tablename__="Project"

    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    name =db.Column(db.String,nullable=False)
    description=db.Column(db.String)
    user_id =db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    start_date =db.Column(db.String, nullable=False)
    finish_date =db.Column(db.String, nullable=False)
    priority =db.Column(db.String, default="normal")


# This creates a clean object-oriented link back to the User instance
    user = db.relationship('UserModel', backref=db.backref('projects', lazy=True))


    def __repr__(self):
        return f"<Project {self.name}>"



class MilestoneModel(db.Model):
    __tablename__="Milestone"

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.String, nullable=False)
    project_id=db.Column(db.Integer, db.ForeignKey("Project.id"), nullable=False)
    due_date=db.Column(db.String, nullable=False)

    project=db.relationship("ProjectModel", backref=db.backref("milestones", lazy=True))

    def __repr__(self):
         return f"<Milestone {self.name}>"




class TaskModel(db.Model):
    __tablename__="Task"

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.String, nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey("User.id"), nullable=True)
    milestone_id=db.Column(db.Integer, db.ForeignKey("Milestone.id"), nullable=True)
    project_id=db.Column(db.Integer, db.ForeignKey("Project.id"), nullable=True)
    status=db.Column(db.String, nullable=False, default="pending")

    user=db.relationship("UserModel", backref=db.backref("tasks", lazy=True))
    project=db.relationship("ProjectModel", backref=db.backref("tasks", lazy=True))
    milestone=db.relationship("MilestoneModel", backref=db.backref("tasks", lazy=True))

    def __repr__(self):
            return f"<Task {self.name}>"
            