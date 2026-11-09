from database import get_connection
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash
import logging
from exception import DatabaseError,RecordNotFoundError,ValidationError
logger=logging.getLogger(__name__)


class Datamanager:
    def __init__(self):
        self.conn=get_connection()
        self.cursor=self.conn.cursor()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()

        self.conn.close()

    def get_pending_task(self)-> list[tuple]:
        self.cursor.execute("""select Task.id,Task.name,User.name,Project.name from Task 
        join  User on  Task.user_id=User.id
        join  Project on Task.project_id=Project.id
        where 
        Task.status='pending'""")
        row=self.cursor.fetchall()
        return row
#old..all old methods revolve around task
    def get_tasks_count_per_user(self)-> list[tuple]:
        self.cursor.execute("""select user_id,count(*) from Task 
             where status='completed'  group by user_id 
            """)
        row=self.cursor.fetchall()
        return row


    def add_task(self,name: str,user_id: int,milestone_id: int,project_id: int,status: str='pending')-> int:
        self.cursor.execute("""SELECT 1 FROM Milestone m LEFT JOIN Project p on m.project_id= p.id 
        WHERE m.id = ? and p.id = ? and p.user_id = ?""",(milestone_id,project_id,user_id))

        if not self.cursor.fetchone():
            raise ValidationError(f"Milestone ID {milestone_id} does not belong to Project ID {project_id} or unauthorized.")

        
        self.cursor.execute("""insert into Task(name,user_id,milestone_id,project_id,status)
    values(?,?,?,?,?)""",(name,user_id,milestone_id,project_id,status))
        
        self.conn.commit()
        return self.cursor.lastrowid

    


    def close_connection(self):
        self.conn.close()



#it was created befor search  task..i didn't delete it cause maybe it has some connection to other files..maybe it's unprofessional to keep similar kind of things,i'll clean those previous unuse methods after the project and all assignment is done

    def get_task(self,status: str|None =None,user_id: int|None =None,project_id: int|None =None)-> list[tuple]|list:
        query="select * from Task "
        conditions=[]
        params: list=[]

        if status:
            conditions.append("status=?")
            params.append(status)

        if user_id is not None:
                    conditions.append("user_id=?")
                    params.append(user_id)

        if project_id is not None:
                    conditions.append("project_id=?")
                    params.append(project_id)

        if conditions:
             query+=" where " + " and ".join(conditions)
        
        self.cursor.execute(query,params)
       
        return self.cursor.fetchall()
    

    def task_exists(self,task_id: int)-> bool:
         self.cursor.execute("select 1  from Task where id = ? ",(task_id,))
         row=self.cursor.fetchone()
         return row is not None

    

    def delete_task(self,task_id: int,user_id: int)-> bool:
         self.cursor.execute("DELETE FROM Task WHERE id = ? and user_id = ?",(task_id,user_id))
         self.conn.commit()
         return self.cursor.rowcount > 0


    def update_task(self,task_id: int,new_status: str|None=None,name: str|None=None,user_id: int|None=None,milestone_id: int|None=None,project_id: int|None=None)-> bool:
        self.cursor.execute("""SELECT project_id,milestone_id FROM Task
        WHERE id = ? and user_id = ?""",(task_id,user_id))

        task_row=self.cursor.fetchone()
        if not task_row:
              raise RecordNotFoundError(f"Task ID {task_id} does not exist or unauthorized.")

        target_milestone_id = milestone_id if milestone_id is not None else task_row[1]
        target_project_id = project_id if project_id is not None else task_row[0]

        if milestone_id is not None or project_id is not None:
            verify_relation = """
                SELECT 1 FROM Milestone m
                JOIN Project p ON m.project_id = p.id
                WHERE m.id = ? AND p.id = ? AND p.user_id = ?
            """
            self.cursor.execute(verify_relation, (target_milestone_id, target_project_id, user_id))
            if not self.cursor.fetchone():
                raise ValidationError(f"Milestone ID {target_milestone_id} does not belong to Project ID {target_project_id} or unauthorized.")
        
        valid_status=["pending","in-progress","completed"]
        if new_status is not None and new_status not in valid_status:
            logger.info(f"Error: '{new_status}' is not a valid status.")
            raise ValidationError("invalid status")
            
        conditions=[]
        params: list[int|str]=[]


        if name is not None:
            conditions.append("name = ?")
            params.append(name)

        if new_status is not None:
            conditions.append("status = ?")
            params.append(new_status)

        if milestone_id is not None:
            conditions.append("milestone_id = ?")
            params.append(milestone_id)

        if project_id is not None:
            conditions.append("project_id = ?")
            params.append(project_id)



        if not conditions:
            return False
        query="update Task set "
        query+=" , ".join(conditions) + " where id = ? and user_id = ? "
        params.extend([task_id,user_id])
        self.cursor.execute(query,params)
        self.conn.commit()
         
        return self.cursor.rowcount > 0


    def get_project_summary(self,project_id: int)-> dict|None:
         query="""
         select 
            count(*) as total_task,
            sum(case when status = 'pending' then 1 else 0 end) AS pending_task,
            sum(case when status = 'in-progress'  then 1 else 0 end) AS in_progress_task,
            sum(case when status = 'completed' then 1 else 0 end) AS completed_task
         from Task
         where project_id = ? """

         self.cursor.execute(query,(project_id,))
         row=self.cursor.fetchone()
         if row and row[0] > 0:
              return {
                   "Total":       row[0],
                   "Pending":     row[1] or 0,
                   "In-progress": row[2] or 0,
                   "completed":   row[3] or 0
              }
         return None


    def get_user_workload_summary_old(self)-> list[dict]:
        query="""
                select
                    u.id,u.name,
                    count(t.id) as total_assigned,
                    sum(case when t.status = 'pending' then 1 else 0 end) AS pending_task,
                    sum(case when t.status = 'in-progress'  then 1 else 0 end) AS in_progress_task,
                    sum(case when t.status = 'completed' then 1 else 0 end) AS completed_task
                FROM User u
                left join Task t ON u.id = t.user_id
                GROUP BY u.id,u.name
                    """


        self.cursor.execute(query)
        row=self.cursor.fetchall()

        summary=[] 
        if row:
            for r in row:
                summary.append({
                    "user_id":     r[0],
                    "user_name":   r[1],
                    "total_task":  r[2],
                    "pending_task":r[3] or 0,
                    "in_progress": r[4] or 0,
                    "completed":   r[5] or 0
                })
        return summary
    def search_tasks(self,keywords: str|None=None,user_id: int|None=None,milestone_id: int|None=None,project_id: int|None=None,status: str|None=None)-> list[dict]:
        query="""
            select   
                t.id,t.name as task_name,t.status as task_status,
                u.name as user_name,m.name as milestone_name,
                p.name as project_name
            from Task t
            LEFT JOIN User u ON t.user_id = u.id
            LEFT JOIN Milestone m ON t.milestone_id = m.id
            LEFT JOIN Project p ON t.project_id = p.id
            where 1=1
                """
        
        params: list=[]

        if keywords is not None:
              query+= " AND " + """(t.name LIKE ? OR u.name LIKE ? OR m.name LIKE ? OR p.name LIKE ?)"""
              wildcard_keyword=f"%{keywords}%"
              params.extend([wildcard_keyword,wildcard_keyword,wildcard_keyword,wildcard_keyword])

        if user_id is not None:
             query+=" AND " + """ t.user_id = ? """
             params.append(user_id)


        if milestone_id is not None:
                     query+=" AND " + """ t.milestone_id = ? """
                     params.append(milestone_id)


        if project_id is not None:
                     query+=" AND " + """ t.project_id = ? """
                     params.append(project_id)


        if status is not None:
                     query+=" AND " + """ t.status = ? """
                     params.append(status)

        self.cursor.execute(query,params)
        row=self.cursor.fetchall()
        task=[]
        if row:
             for r in row:
                  task.append({
                       "task_id":r[0],
                       "task_name":r[1],
                       "task_status":r[2],
                       "user_name":r[3],
                       "milestone_name":r[4],
                       "project_name":r[5]
                  })

        return task
                  
        

#it was befor when you asked me to build it ,when everything was build arounf Task..itis not updated later
    def transfer_user_task(self,from_user_id: int,to_user_id: int)-> bool:
         try:
            self.cursor.execute("select id from User where id = ?",(from_user_id,))
            if not self.cursor.fetchone():
                raise ValueError(f"target user_id {from_user_id} does not exists.")

            self.cursor.execute("select id from User where id = ?",(to_user_id,))
            if not self.cursor.fetchone():
                    raise ValueError(f"target user_id {to_user_id} does not exists.")

            update_query="""update Task set user_id = ? where user_id = ?"""

            self.cursor.execute(update_query,(to_user_id,from_user_id))
            self.conn.commit()
            return True
         except Exception as e:
              self.conn.rollback()
              print(f"Transaction failed : {e}")
              return False



    def delete_project_safely(self,project_id: int,user_id: int,cascade: bool=False)-> bool:
        try:
            self.cursor.execute("select 1 from Project where id = ?",(project_id,))
            if not self.cursor.fetchone():
                raise RecordNotFoundError(f"Project ID {project_id} does not exists")

            if cascade:
                self.cursor.execute("delete from Task where project_id = ?",(project_id,))
                self.cursor.execute("delete from Milestone where project_id = ?",(project_id,))

            else:
                self.cursor.execute("select 1 from Milestone where project_id = ? limit 1 ",(project_id,))
                has_milestone=self.cursor.fetchone()
                self.cursor.execute("select 1 from Task where project_id = ? limit 1 ",(project_id,))
                has_task=self.cursor.fetchone()
                if has_milestone or has_task:
                     raise ValidationError(f"Can not delete Project {project_id}: active milestone or task exists."
                                      "Set cascade=True to force deleter all related data.")


            self.cursor.execute("DELETE from Project where id = ? and user_id = ?",(project_id,user_id))
            self.conn.commit()
            return True


            
        except (RecordNotFoundError,ValidationError) as e :
             self.conn.rollback()
             raise
                   
        except Exception as e:
                self.conn.rollback()
                raise DatabaseError(f"Unexpected database Error during project deletion: {e}")



    def apply_schema_indexes(self)-> bool:
        indexes=[
              "CREATE INDEX IF NOT EXISTS idx_task_user_id ON Task(user_id)",
              "CREATE INDEX IF NOT EXISTS idx_task_milestone_id ON Task(milestone_id)",
              "CREATE INDEX IF NOT EXISTS idx_task_project_id ON Task(project_id)",
              "CREATE INDEX IF NOT EXISTS idx_task_status ON Task(status)",
              "CREATE INDEX IF NOT EXISTS idx_milestone_project_id ON Milestone(project_id)",
         ]

        try:
                for idx in indexes:
                   self.cursor.execute(idx)
                self.conn.commit()
                return True
        except Exception as e:
             self.conn.rollback()
             raise DatabaseError(f"failed to apply database indexes : {e}")


    def add_project(self, name:str ,description:str,user_id: int , start_date:str, finish_date:str) ->int:
         query="insert into Project (name,description,user_id,start_date,finish_date) VALUES (?,?,?,?,?)"
         self.cursor.execute(query,(name,description,user_id,start_date,finish_date))
         self.conn.commit()
         return self.cursor.lastrowid
    
        



    def search_projects(self,user_id,keywords:str|None =None )-> list:
         query="select  * from Project WHERE user_id = ?"
         params=[user_id]
         if keywords is not None:
              query+=" AND  (name LIKE ? OR description LIKE ?)"
              params.extend([f"%{keywords}%",f"%{keywords}%"])

         self.cursor.execute(query,params)
         row=self.cursor.fetchall()
         projects=[]
         if row:
              for r in row:
                   projects.append({
                        "project_id":  r[0],
                        "project_name":r[1],
                        "description": r[2],
                        "user_id":     r[3],
                        "start_date":  r[4],
                        "finish_date": r[5]
                   })

         return projects


    def update_project(self,project_id:int, name:str|None=None, description:str|None=None, user_id: int|None =None, start_date:str|None=None, finish_date:str|None=None):
        try:
            self.cursor.execute("select 1 from Project where id = ? AND user_id = ? ",(project_id,user_id))
            if not self.cursor.fetchone():
                raise RecordNotFoundError(f"Project ID {project_id} does not exists")

            query="UPDATE Project set "
            conditions=[]
            params: list=[]

            if name is not None:
                 conditions.append(" name = ?")
                 params.append(name)

            
            if description is not None:
                             conditions.append(" description = ?")
                             params.append(description)

            if start_date is not None:
                             conditions.append(" start_date = ?")
                             params.append(start_date)

            if finish_date is not None:
                                         conditions.append(" finish_date = ?")
                                         params.append(finish_date)

            
            if not conditions:
                return False
        
            query+=" , ".join(conditions) + " where id = ? and user_id = ? "
            params.extend([project_id,user_id])
            self.cursor.execute(query,params)
            self.conn.commit()
         
            return True

        except RecordNotFoundError :
             raise



    def register_user(self,name: str, username: str, age:int , email: str, password: str)-> int:
          self.cursor.execute("select 1 from User WHERE username=? ",(username,))
          if self.cursor.fetchone() :
                raise ValidationError(f"username: {username} already exists ")

          hassed_password=generate_password_hash(password)

          query="INSERT INTO User (name,username,age,email,password_hash) VALUES (?,?,?,?,?)"

          self.cursor.execute(query,(name,username,age,email,hassed_password))
          self.conn.commit()
          return self.cursor.lastrowid


    def authenticate_user(self,username: str, password: str)-> bool:
        self.cursor.execute("select password_hash from User WHERE username = ? ",(username,))
        row=self.cursor.fetchone()
        if  not row :
                return False #user not found
        stored_hass_password=row[0]

        return check_password_hash(stored_hass_password,password)


    def get_user_by_username(self,username:str)->dict|bool:
        self.cursor.execute("select * from User where username = ?",(username,))
        row=self.cursor.fetchone()
        if not  row:
            return False

        return {
                "id": row[0],
                "name": row[1],
                "username": row[2],
                "age": row[3],
                "email": row[4],
                "password_hash": row[5]
        }




    # Milestone part


    def add_milestone(self,user_id: int,name:str,project_id: int,due_date: str)-> int:
        self.cursor.execute("""SELECT  1  FROM Project 
          where id = ? and user_id = ?""",(project_id,user_id))
        if not  self.cursor.fetchone():
              raise RecordNotFoundError
        self.cursor.execute("insert into Milestone(name,project_id,due_date) VALUES(?,?,?)",(name,project_id,due_date))
        self.conn.commit()
        return self.cursor.lastrowid


    def search_milestone(self,user_id: int, project_id: int|None=None, keywords: str|None=None)-> list:
        query="""SELECT m.id ,m.name,m.due_date,m.project_id,p.name as project_name
        FROM Milestone m 
        LEFT JOIN Project p on m.project_id=p.id WHERE p.user_id = ? """

        params: list=[user_id]
        

        if project_id is not None:
            query+=" AND project_id = ?"
            params.append(project_id)

        if keywords is not None:
              query += " AND  (m.name LIKE ? OR p.name LIKE ?)"
              params.extend([f"%{keywords}%",f"%{keywords}%"])

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        milestones = []
        for r in rows:
            milestones.append({
                "milestone_id": r[0],
                "milestone_name": r[1],
                "due_date": r[2],
                "project_id": r[3],
                "project_name": r[4]
            })
        return milestones


    def update_milestone(self, milestone_id: int, user_id: int, name: str | None = None, due_date: str | None = None) -> bool:
        verify_query="""select 1 from Milestone m 
        LEFT JOIN 
        Project p ON m.project_id=p.id 
        WHERE m.id = ? and p.user_id = ?"""

        self.cursor.execute(verify_query,(milestone_id,user_id))
        row=self.cursor.fetchone()
        if not row :
            raise RecordNotFoundError(f"Milestone ID {milestone_id} does not exist or unauthorized.")
            

        conditions = []
        params: list = []
        if name is not None:
            conditions.append("name = ?")
            params.append(name)
        if due_date is not None:
            conditions.append("due_date = ?")
            params.append(due_date)

        if not conditions:
            return False


        query="UPDATE Milestone SET " + ", ".join(conditions) + " WHERE id = ?"
        params.append(milestone_id)
        self.cursor.execute(query,params)
        self.conn.commit()

        return self.cursor.rowcount> 0


    def delete_milestone(self,milestone_id: int,user_id: int,cascade: bool= False)->  bool: 
        verify_query="""select 1 from Milestone m 
                  LEFT JOIN 
                  Project p ON m.project_id=p.id 
                  WHERE m.id = ? and p.user_id = ?"""
          
        self.cursor.execute(verify_query,(milestone_id,user_id))
        row=self.cursor.fetchone()
        if not row :
              raise RecordNotFoundError(f"Milestone ID {milestone_id} does not exist or unauthorized.")


        self.cursor.execute("SELECT 1 FROM Task WHERE milestone_id = ? and user_id = ? LIMIT 1",(milestone_id, user_id))
        has_task = self.cursor.fetchone()
        if has_task and not cascade:
              raise ValidationError(
                f"Cannot delete Milestone {milestone_id}: active tasks are attached. "
                "Set cascade=True to delete associated tasks."
            )
            

        
        if cascade:
            self.cursor.execute("DELETE FROM Task WHERE milestone_id = ?", (milestone_id,))

        # 3. Safe deletion
        self.cursor.execute("DELETE FROM Milestone WHERE id = ?", (milestone_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0



    def get_user_workload_summary(self,user_id: int,project_id: int|None=None)-> list:
        query="""SELECT id,name,description,start_date,finish_date FROM Project WHERE user_id = ? """
        params=[user_id]
        if project_id is not None:
              query+=" AND id = ?"
              params.append(project_id)

        self.cursor.execute(query,params)
        projects=self.cursor.fetchall()
        project_summary=[]

        for p in projects:
            p_id,p_name,p_description,p_start_date,p_finish_date=p

            self.cursor.execute("""SELECT COUNT(*) AS total_task,
            SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END ) AS completed,
            SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END ) AS pending,
            SUM(CASE WHEN status='in-progress' THEN 1 ELSE 0 END ) AS in_progress 
            FROM Task 
            WHERE project_id = ? AND user_id = ?""",(p_id,user_id))

            task_status=self.cursor.fetchone()
            total_task,completed_task,pending_task,in_progress_task=task_status

            total_tasks: int = total_task or 0
            completed_tasks: int = completed_task or 0
            pending_tasks : int= pending_task or 0
            in_progress_tasks: int = in_progress_task or 0

            self.cursor.execute("""
                SELECT m.id,m.name,m.due_date,
                COUNT(t.id) as milestone_total_task,
                SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END ) AS completed,
                SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END ) AS pending,
                SUM(CASE WHEN status='in-progress' THEN 1 ELSE 0 END ) AS in_progress
                FROM Milestone m
                LEFT JOIN Task t 
                on m.id=t.milestone_id
                WHERE m.project_id = ? GROUP BY m.id """,(p_id,))
            milestones=self.cursor.fetchall()
            milestone_breakdown=[]
            for m in milestones:
                    m_id,m_name,m_due_date,total,m_complete,m_pending,m_in_progress=m
                    milestone_breakdown.append({
                        "milestone_id": m_id,
                        "name": m_name,
                        "due_date": m_due_date,
                        "total_tasks_count": total or 0,
                        "completed_task": m_complete or 0,
                        "pending_task": m_pending or 0,
                        "in-progress_task":m_in_progress or 0
                    })

            project_summary.append({
                "project_id": p_id,
    "project_name": p_name,
    "description": p_description,
    "start_date": p_start_date,
    "finish_date": p_finish_date,
    "task_summary": {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks
    },
    "milestone_breakdown": milestone_breakdown
            })

        return project_summary 