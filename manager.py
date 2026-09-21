from database import get_connection
import sqlite3
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

    def get_tasks_count_per_user(self)-> list[tuple]:
        self.cursor.execute("""select user_id,count(*) from Task 
             where status='completed'  group by user_id 
            """)
        row=self.cursor.fetchall()
        return row


    def add_task(self,name: str,user_id: int,milestone_id: int,project_id: int,status: str='pending')-> int:
        self.cursor.execute("""insert into Task(name,user_id,milestone_id,project_id,status)
    values(?,?,?,?,?)""",(name,user_id,milestone_id,project_id,status))
        
        self.conn.commit()
        return self.cursor.lastrowid
    def close_connection(self):
        self.conn.close()

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

    def delete_task(self,task_id: int)-> bool:
         self.cursor.execute("DELETE FROM Task WHERE id = ?",(task_id,))
         self.conn.commit()
         return self.cursor.rowcount > 0


    def update_task(self,task_id: int,new_status: str|None=None,name: str|None=None,user_id: int|None=None,milestone_id: int|None=None,project_id: int|None=None)-> bool:
        valid_status=["pending","in-progress","completed"]
        if new_status is not None and new_status not in valid_status:
            logger.info(f"Error: '{new_status}' is not a valid status.")
            return False

        conditions=[]
        params: list[int|str]=[]


        if name is not None:
            conditions.append("name = ?")
            params.append(name)


        if user_id is not None:
            conditions.append("user_id = ? ")
            params.append(user_id)

        if milestone_id is not None:
            conditions.append("milestone_id = ?")
            params.append(milestone_id)


        if project_id is not None:
            conditions.append("project_id = ?")
            params.append(project_id)

        if new_status is not None:
            conditions.append("status = ?")
            params.append(new_status)



        if not conditions:
            return False
        query="update Task set "
        query+=" , ".join(conditions) + " where id = ? "
        params.append(task_id)
        self.cursor.execute(query,params)
         
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


    def get_user_workload_summary(self)-> list[dict]:
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



    def delete_project_safely(self,project_id: int,cascade: bool=False)-> bool:
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


            self.cursor.execute("DELETE from Project where id = ?",(project_id,))
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

        

