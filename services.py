import logging
from exception import DatabaseError,RecordNotFoundError,ValidationError
from manager import Datamanager
from flask import session
logger=logging.getLogger(__name__)


class ProjectService:
    @staticmethod
    def add_project(name:str ,description:str,user_id: int , start_date:str, finish_date:str) -> int :

        if  name is None or description is None or start_date is None or finish_date is None:
                raise ValidationError("missing requirements")
        
        with Datamanager() as db:
            project_id=db.add_project(name,description,user_id,start_date,finish_date)
            logger.info(f"Service: Successfully created project ID {project_id} for user {user_id}")
            return project_id

    @staticmethod
    def search_project(user_id: int,keywords: str|None=None)->list:
        
        with Datamanager() as db:
                projects=db.search_projects(user_id,keywords)
                return projects

    
    @staticmethod
    def delete_project(project_id: int,user_id: int)-> bool:
        
        with Datamanager() as db:
            return db.delete_project_safely(project_id,user_id)
               
        
    @staticmethod
    def update_project(user_id: int,project_id: int,name: str|None=None,description: str|None=None,start_date:str|None=None,finish_date:str|None=None):
        
        with Datamanager() as db:
            return  db.update_project(project_id=project_id,name=name,description=description,user_id=user_id,start_date=start_date,finish_date=finish_date)
                
        



class MilestoneService:
    @staticmethod
    def add_milestone(user_id: int,name: str,project_id: int,due_date: str)-> int:
    

        if  name is None or project_id is None or due_date is None :
                raise RecordNotFoundError
        try:
            project_id = int(project_id)
        except (TypeError, ValueError):
            raise ValidationError("Project ID must be a valid integer.")
            
        with Datamanager() as db:
            milestone_id=db.add_milestone(user_id=user_id,name=name,project_id=project_id,due_date=due_date)
            return milestone_id
        

    @staticmethod
    def search_milestone(user_id: int,project_id: int,keywords: str|None=None)-> list:
        if project_id is not None:
            try:
                project_id = int(project_id)
            except (TypeError, ValueError):
                raise ValidationError("Milestone ID must be a valid integer.")
                    
        with Datamanager() as db:
            milestone=db.search_milestone(user_id=user_id,project_id=project_id,keywords=keywords)
            return milestone
        
    @staticmethod
    def delete_milestone(milestone_id: int,user_id: int)->bool:
        try:
            milestone_id = int(milestone_id)
        except (TypeError, ValueError):
            raise ValidationError("Project ID must be a valid integer.")
                                
        with Datamanager() as db:
            return db.delete_milestone(milestone_id=milestone_id,user_id=user_id)


    @staticmethod
    def update_milestone(milestone_id: int,user_id: int,name: str,due_date: str)->bool:
         with Datamanager() as db:
            return db.update_milestone(milestone_id=milestone_id,user_id=user_id,name=name,due_date=due_date)
                    



class TaskService:
    @staticmethod
    def search_tasks(keywords: str|None=None,user_id: int|None=None,milestone_id: int|None=None,project_id: int|None=None,status: str|None=None)-> list[dict]:

        with Datamanager() as db:
            tasks=db.search_tasks(keywords=keywords,user_id=user_id,milestone_id=milestone_id,project_id=project_id)
            return tasks
        
    @staticmethod
    def add_task(name: str,user_id: int,milestone_id: int,project_id: int)->int:

        if  name is None or user_id is None or milestone_id is None or project_id is None:
            raise ValidationError
        try:
            user_id=int(user_id)
            milestone_id=int(milestone_id)
            project_id=int(project_id)

        except (TypeError, ValueError):
                    raise ValidationError("ID must be a valid integer.")
        with Datamanager() as db:
            task_id=db.add_task(name=name,user_id=user_id,milestone_id=milestone_id,project_id=project_id)
            return task_id
    

    @staticmethod
    def delete_task(task_id: int,user_id: int)->bool:
            try:
                task_id=int(task_id)
            
            except (TypeError, ValueError):
                        raise ValidationError("ID must be a valid integer.")
            with Datamanager() as db:
                result=db.task_exists(task_id=task_id)
                if not result :
                    raise RecordNotFoundError

                return db.delete_task(task_id=task_id,user_id=user_id)
                


    @staticmethod
    def update_task(task_id: int,new_status: str|None=None,name: str|None=None,user_id: int|None=None,milestone_id: int|None=None,project_id: int|None=None,)->bool:
        
        try:
            if user_id is not None:
                user_id=int(user_id)
            if milestone_id is not None:
                milestone_id=int(milestone_id)
            if project_id is not None:
                project_id=int(project_id)
            
            
        except (TypeError, ValueError):
                raise ValidationError("ID must be a valid integer.")
        with Datamanager() as db:
            if not db.task_exists(task_id):
                raise RecordNotFoundError
            
            return db.update_task(task_id=task_id,new_status=new_status,name=name,user_id=user_id,milestone_id=milestone_id,project_id=project_id)



class AuthService:
    @staticmethod
    def register_user(name: str, username: str, age: int, email: str, password: str):
    
        if not all([name, username, age, email, password]):
                raise RecordNotFoundError
        try:
            age=int(age)
        except( ValueError, TypeError):     
            raise ValidationError
        with Datamanager() as db:
            return db.register_user(name=name,username=username,age=age,email=email,password=password)
    

    @staticmethod
    def login(username: str,password: str)->bool:
        if not all([ username,  password]):
                raise RecordNotFoundError
       
        with Datamanager() as db:
            user=db.get_user_by_username(username)
            if  user and db.authenticate_user(username,password):
                session["user_id"]=user["id"]
                session["username"]=user["username"]
                return True
            return False
                
    @staticmethod
    def logout():
        session.clear()
        return True
        

class ReportService:
    @staticmethod
    def get_user_summary(user_id: int,project_id: int|None=None)->list:

        try:
            if project_id is not None:
                project_id=int(project_id)
        except ValueError :
                raise ValidationError
        
        
        with Datamanager() as db:
            return db.get_user_workload_summary(user_id=user_id,project_id=project_id)