from models import db,UserModel,ProjectModel,MilestoneModel,TaskModel
from sqlalchemy import or_,case,func
from werkzeug.security import generate_password_hash,check_password_hash
import logging
from exception import DatabaseError,RecordNotFoundError,ValidationError
logger=logging.getLogger(__name__)


class Datamanager:
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            db.session.rollback()
        return False
    
    


    def add_task(self,name: str,user_id: int,milestone_id: int,project_id: int,status: str='pending')-> int:
        query=db.session.query(MilestoneModel).join(ProjectModel,MilestoneModel.project_id==ProjectModel.id).filter(MilestoneModel.id==milestone_id,ProjectModel.id==project_id,ProjectModel.user_id==user_id).first()
        
        if not query:
            raise ValidationError(f"Milestone ID {milestone_id} does not belong to Project ID {project_id} or unauthorized.")

        task=TaskModel(name=name,user_id=user_id,milestone_id=milestone_id,project_id=project_id,status=status)

        db.session.add(task)
        db.session.commit()
        return task.id

    

    def task_exists(self,task_id: int)-> bool:
         return TaskModel.query.filter_by(id=task_id).first() is not None
    

    def delete_task(self,task_id: int,user_id: int)-> bool:
        task=TaskModel.query.filter_by(id=task_id,user_id=user_id).first()
        if not task:
            raise RecordNotFoundError(
            f"Task ID {task_id} does not exist or is not owned by user {user_id}."
        )
        db.session.delete(task)
        db.session.commit()
        return True


    def update_task(self,task_id: int,new_status: str|None=None,name: str|None=None,user_id: int|None=None,milestone_id: int|None=None,project_id: int|None=None)-> bool:
        task=TaskModel.query.filter_by(id=task_id,user_id=user_id).first()
    
        if not task:
              raise RecordNotFoundError(f"Task ID {task_id} does not exist or unauthorized.")

        target_milestone_id = milestone_id if milestone_id is not None else task.milestone_id
        target_project_id = project_id if project_id is not None else task.project_id

        if milestone_id is not None or project_id is not None:
            verify_relation=db.session.query(MilestoneModel).join(ProjectModel,MilestoneModel.project_id==ProjectModel.id).filter(MilestoneModel.id==target_milestone_id,
                                                                                                                                  ProjectModel.id==target_project_id,
                                                                                                                                  ProjectModel.user_id==user_id,).first()

            if not verify_relation:
                raise ValidationError(f"Milestone ID {target_milestone_id} does not belong to Project ID {target_project_id} or unauthorized.")
        
        valid_status=["pending","in-progress","completed"]
        if new_status is not None and new_status not in valid_status:
            logger.info(f"Error: '{new_status}' is not a valid status.")
            raise ValidationError("invalid status")

        update=False
        if name is not None:
            task.name=name
            update=True

        if new_status is not None:
            task.status=new_status
            update=True

        if milestone_id is not None:
            task.milestone_id=milestone_id
            update=True

        if project_id is not None:
            task.project_id=project_id
            update=True

        db.session.commit()
        return update


    
    def search_tasks(self,keywords: str|None=None,user_id: int|None=None,milestone_id: int|None=None,project_id: int|None=None,status: str|None=None)-> list[dict]:
        query=db.session.query(
             TaskModel.id.label("task_id"),
             TaskModel.name.label("task_name"),
             TaskModel.status.label("task_status"),
             UserModel.name.label("user_name"),
             MilestoneModel.name.label("milestone_name"),
             ProjectModel.name.label("project_name"),
             ).outerjoin(UserModel,TaskModel.user_id==UserModel.id).outerjoin(MilestoneModel,TaskModel.milestone_id==MilestoneModel.id).outerjoin(ProjectModel,TaskModel.project_id==ProjectModel.id)
        
        
        if keywords is not None:
              pattern=f"%{keywords}%"
              query=query.filter(or_(TaskModel.name.ilike(pattern),
                                     UserModel.name.ilike(pattern),
                                     MilestoneModel.name.ilike(pattern),
                                     ProjectModel.name.ilike(pattern),))
            
        if user_id is not None:
            query=query.filter(TaskModel.user_id==user_id)
             

        if milestone_id is not None:
            query=query.filter(TaskModel.milestone_id==milestone_id)


        if project_id is not None:
            query=query.filter(TaskModel.project_id==project_id)


        if status is not None:
            query=query.filter(TaskModel.status==status)

        row=query.all()
        
        return [
             {
            "task_id":r.task_id,
            "task_name":r.task_name,
            "task_status":r.task_status,
            "user_name":r.user_name,
            "milestone_name":r.milestone_name,
            "project_name":r.project_name,
             } for r in row
        ]





    def delete_project_safely(self,project_id: int,user_id: int,cascade: bool=False)-> bool:
        try:
            project=ProjectModel.query.filter_by(id=project_id,user_id=user_id).first()
            if not project:
                raise RecordNotFoundError(f"Project ID {project_id} does not exists")

            if cascade:
                TaskModel.query.filter_by(project_id=project_id).delete(synchronize_session=False)
                MilestoneModel.query.filter_by(project_id=project_id).delete(synchronize_session=False)

            else:
                has_milestone=MilestoneModel.query.filter_by(project_id=project_id).first() is not None
                has_task=TaskModel.query.filter_by(project_id=project_id).first() is not None
                if has_milestone or has_task:
                     raise ValidationError(f"Can not delete Project {project_id}: active milestone or task exists."
                                      "Set cascade=True to force delete all related data.")


            db.session.delete(project)
            db.session.commit()
            return True


            
        except (RecordNotFoundError,ValidationError) as e :
             db.session.rollback()
             raise
                   
        except Exception as e:
                db.session.rollback()
                raise DatabaseError(f"Unexpected database Error during project deletion: {e}")




    def add_project(self, name:str ,description:str,user_id: int , start_date:str, finish_date:str) ->int:
         project=ProjectModel(name=name,description=description,user_id=user_id,start_date=start_date,finish_date=finish_date)
         db.session.add(project)
         db.session.commit()
         
         return project.id
        



    def search_projects(self,user_id,keywords:str|None =None )-> list:
        query=ProjectModel.query.filter_by(user_id=user_id)
         
        if keywords is not None:
              pattern=f"%{keywords}%"
              query=query.filter(or_(
                    ProjectModel.name.ilike(pattern),ProjectModel.description.ilike(pattern),
              ))

        projects=query.all()

        return [{
                "project_id":  p.id,
                "project_name":p.name,
                "description": p.description,
                "user_id":     p.user_id,
                "start_date":  p.start_date,
                "finish_date": p.finish_date} for p in projects]


    def update_project(self,project_id:int, name:str|None=None, description:str|None=None, user_id: int|None =None, start_date:str|None=None, finish_date:str|None=None):
    
        project=ProjectModel.query.filter_by(id=project_id,user_id=user_id).first()
        
        if not project:
            raise RecordNotFoundError(f"Project ID {project_id} does not exists")


        update=False
        if name is not None:
            project.name=name
            update=True
        
        if description is not None:
            project.description=description
            update=True

        if start_date is not None:
            project.start_date=start_date
            update=True

        if finish_date is not None:
            project.finish_date=finish_date
            update=True

        
        if not update:
            return False
    
        
        db.session.commit()
        
        return True



    def register_user(self,name: str, username: str, age:int , email: str, password: str)-> int:
          exist_user=UserModel.query.filter_by(username=username).first()
          if exist_user :
                raise ValidationError(f"username: {username} already exists ")

          hassed_password=generate_password_hash(password)

          new_user=UserModel(name=name,username=username,age=age,email=email,password_hash=hassed_password)
          db.session.add(new_user)
          db.session.commit()
          
          return new_user.id


    def authenticate_user(self,username: str, password: str)-> bool:
        user=UserModel.query.filter_by(username=username).first()
        if  not user :
                return False #user not found

        return check_password_hash(user.password_hash,password)


    def get_user_by_username(self,username:str)->dict|bool:
        user=UserModel.query.filter_by(username=username).first()

        if not user:
            return False

        return {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "age": user.age,
                "email": user.email,
                "password_hash": user.password_hash
        }




    # Milestone part


    def add_milestone(self,user_id: int,name:str,project_id: int,due_date: str)-> int:
        project=ProjectModel.query.filter_by(id=project_id,user_id=user_id).first()
        if not  project:
              raise RecordNotFoundError(f"Project ID {project_id} does not exist or is not owned by user {user_id}.")
        milestone=MilestoneModel(name=name,project_id=project_id,due_date=due_date)
        db.session.add(milestone)
        db.session.commit()
        return milestone.id


    def search_milestone(self,user_id: int, project_id: int|None=None, keywords: str|None=None)-> list:
        query=db.session.query(MilestoneModel,ProjectModel.name.label("project_name")).join(ProjectModel,MilestoneModel.project_id==ProjectModel.id).filter(ProjectModel.user_id==user_id)
        
        if project_id is not None:
            query=query.filter(MilestoneModel.project_id==project_id)

        if keywords is not None:
              pattern=f"%{keywords}%"
              query=query.filter(or_(MilestoneModel.name.ilike(pattern),ProjectModel.name.ilike(pattern),))
              
        rows = query.all()
        
        return [{
            "milestone_id": m.id,
            "milestone_name": m.name,
            "due_date": m.due_date,
            "project_id": m.project_id,
            "project_name": project_name,
        } for m,project_name in rows]




    def update_milestone(self, milestone_id: int, user_id: int, name: str | None = None, due_date: str | None = None) -> bool:
        milestone=MilestoneModel.query.join(ProjectModel,MilestoneModel.project_id==ProjectModel.id).filter(MilestoneModel.id==milestone_id,
                                                                                                            ProjectModel.user_id==user_id,).first()
        if not milestone :
            raise RecordNotFoundError(f"Milestone ID {milestone_id} does not exist or unauthorized.")
            
        update=False
        if name is not None:
            milestone.name=name
            update=True

        if due_date is not None:
            milestone.due_date=due_date
            update=True

        if not update:
            return False

        db.session.commit()
        return True




    def delete_milestone(self,milestone_id: int,user_id: int,cascade: bool= False)->  bool: 
        milestone=MilestoneModel.query.join(ProjectModel,MilestoneModel.project_id==ProjectModel.id).filter(MilestoneModel.id==milestone_id,ProjectModel.user_id==user_id,).first()
        if not milestone :
              raise RecordNotFoundError(f"Milestone ID {milestone_id} does not exist or unauthorized.")


        
        has_task = TaskModel.query.filter_by(milestone_id=milestone_id).first()
        if has_task and not cascade:
              raise ValidationError(
                f"Cannot delete Milestone {milestone_id}: active tasks are attached. "
                "Set cascade=True to delete associated tasks."
            )
            
        if cascade:
            TaskModel.query.filter_by(milestone_id=milestone_id).delete(synchronize_session=False)
        # 3. Safe deletion
        db.session.delete(milestone)
        db.session.commit()
        return True



    def get_user_workload_summary(self,user_id: int,project_id: int|None=None)-> list:
        project_query=ProjectModel.query.filter_by(user_id=user_id)
        
        if project_id is not None:
              project_query=project_query.filter_by(id=project_id)

       
        projects=project_query.all()
        project_summary=[]

        for p in projects:
            task_counts=db.session.query(
                func.count(TaskModel.id).label("total_task"),
                func.sum(
                    case((TaskModel.status=='completed',1), else_=0)
                 ).label("completed"),
                func.sum(
                    case((TaskModel.status=='pending',1), else_=0)
                    ).label('pending'),
                func.sum(
                    case((TaskModel.status=='in-progress',1), else_=0)
                    ).label('in_progress')).filter(TaskModel.project_id==p.id,TaskModel.user_id==user_id).first()
            if task_counts:
                 total_tasks=int(task_counts.total_task or 0)
                 completed_tasks=int(task_counts.completed or 0)
                 pending_tasks=int(task_counts.pending or 0)
                 in_progress_tasks=int(task_counts.in_progress or 0)
            else:
                 total_tasks=completed_tasks=pending_tasks=in_progress_tasks=0


            milestone_rows=db.session.query(MilestoneModel.id.label("milestone_id"),
                                            MilestoneModel.name.label("milestone_name"),
                                            MilestoneModel.due_date.label("milestone_due_date"),
                                            func.count(TaskModel.id).label("milestone_total_task"),
                                            func.sum(
                                                case((TaskModel.status=='completed',1), else_=0)
                                                ).label("completed"),
                                            func.sum(
                                                case((TaskModel.status=='pending',1), else_=0)
                                                ).label('pending'),
                                            func.sum(
                                                case((TaskModel.status=='in-progress',1), else_=0)
                                                ).label('in_progress')
                                            ).outerjoin(TaskModel,MilestoneModel.id==TaskModel.milestone_id).filter(MilestoneModel.project_id==p.id).group_by(
                                                 MilestoneModel.id,
                                                 MilestoneModel.name,
                                                 MilestoneModel.due_date
                                            ).all()
            
            milestone_breakdown=[{
                                    "milestone_id": m.milestone_id,
                                    "name": m.milestone_name,
                                    "due_date": m.milestone_due_date,
                                    "total_tasks_count": int(m.milestone_total_task or 0),
                                    "completed_task": int(m.completed or 0),
                                    "pending_task": int(m.pending or 0),
                                    "in-progress_task":int(m.in_progress or 0)} for m in milestone_rows]
            
            project_summary.append({
                "project_id": p.id,
                "project_name": p.name,
                "description": p.description,
                "start_date": p.start_date,
                "finish_date": p.finish_date,
                "task_summary": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "pending_tasks": pending_tasks,
                    "in_progress_tasks": in_progress_tasks
                },
                "milestone_breakdown": milestone_breakdown
            })

        return project_summary 