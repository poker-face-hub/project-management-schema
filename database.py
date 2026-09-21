import logging
import sqlite3

logging.basicConfig(handlers=[logging.FileHandler("project-management.log"),logging.StreamHandler()],
                    level=logging.DEBUG,
                    format="%(name)s:%(levelname)s:%(message)s:%(asctime)s")

logger=logging.getLogger(__name__)


def get_connection():
    conn=sqlite3.connect("project-management.db")
    conn.execute("pragma foreign_keys = on")
    conn.commit()
    return conn

def init_db(conn):
    cursor=conn.cursor()

    cursor.execute("""create table if not exists Project(
    id integer primary key autoincrement,
    name text not null,
    description text ,
    start_date text not null,
    finish_date text not null)""")
    logger.info("Project table was created!")
    #cursor.execute("drop table Milestone")

    cursor.execute("""create table if not exists Milestone(
    id integer primary key autoincrement,
    name text not null,
    project_id integer,
    due_date text not null,
    foreign key(project_id) references Project(id))""")
    logger.info("Milestones table was created!")

    cursor.execute("""create table if not exists User(
    id integer primary key autoincrement,
    name text not null,
    age integer not null ,
    email text unique)
    """)
    logger.info("User table was created!")

    #cursor.execute("drop table Task")
    cursor.execute("""create table if not exists Task(
    id integer primary key autoincrement,
    name text not null,
    user_id integer not null,
    milestone_id integer ,
    project_id integer,
    status text not null default 'pending',
    foreign key(user_id) references User(id),
    foreign key(milestone_id) references Milestone(id),
    foreign key(project_id) references Project(id))""")
    logger.info("Task table was created!")

    conn.commit()
    logger.info("Database schema intialized successfully!")
    


if __name__=="__main__":
    conn=get_connection()
    init_db(conn)
    conn.close()

