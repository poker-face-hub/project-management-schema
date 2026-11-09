import logging
import sqlite3
from flask import current_app

logging.basicConfig(handlers=[logging.FileHandler("project-management.log"),logging.StreamHandler()],
                    level=logging.DEBUG,
                    format="%(name)s:%(levelname)s:%(message)s:%(asctime)s")

logger=logging.getLogger(__name__)


def get_connection(database_uri=None):
    if database_uri:
        return sqlite3.connect(database_uri, uri=True)
    try:
        if current_app and "DATABASE_URI" in current_app.config:
            return sqlite3.connect(current_app.config["DATABASE_URI"], uri=True)
    except RuntimeError:
        pass

    
    conn=sqlite3.connect("project-management.db")
    conn.execute("pragma foreign_keys = on")
    conn.commit()
    return conn

def init_db(conn):
    cursor=conn.cursor()


    cursor.execute("""CREATE TABLE IF NOT EXISTS schema_migrations(
    version INTEGER PRIMARY KEY,
    applied at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    cursor.execute("SELECT MAX(version) FROM schema_migrations")
    row=cursor.fetchone()
    current_version=row[0] if row[0] is not None else 0
    logger.info(f"Database migration check: Current schema version is {current_version}")


    if current_version<1:
        cursor.execute("""create table if not exists User(
            id integer primary key autoincrement,
            name text not null,
            username text unique not null,
            age integer not null ,
            email text unique,
            password_hash text not null)
            """)
        logger.info("User table was created!")
        

        cursor.execute("""create table if not exists Project(
        id integer primary key autoincrement,
        name text not null,
        description text ,
        user_id integer not null,
        start_date text not null,
        finish_date text not null,
        foreign key(user_id) references User(id))""")
        logger.info("Project table was created!")
        #cursor.execute("drop table User")

        cursor.execute("""create table if not exists Milestone(
        id integer primary key autoincrement,
        name text not null,
        project_id integer,
        due_date text not null,
        foreign key(project_id) references Project(id))""")
        logger.info("Milestones table was created!")

        
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

        cursor.execute("INSERT INTO schema_migrations(version) VALUES(1)")
        conn.commit()
        logger.info("Database schema intialized successfully!")
        
    if current_version<2:
        try:
            cursor.execute("ALTER TABLE Project ADD COLUMN priority TEXT DEFAULT 'normal'")
        except sqlite3.OperationalError:
            pass

        cursor.execute("INSERT INTO schema_migrations(version) VALUES(2)")
        conn.commit()
        logger.info("Successfully applied migration version 2: Project priority column.")

if __name__=="__main__":
    conn=get_connection()
    init_db(conn)
    conn.close()

