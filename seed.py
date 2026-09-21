import logging
from database import get_connection, init_db
from manager import Datamanager
logger = logging.getLogger(__name__)

def seed_project(cursor):
    projects = ("avy company", "website design", "2026-09-01", "2026-12-01")
    cursor.execute(
        """INSERT INTO Project (name, description, start_date, finish_date)
           VALUES (?, ?, ?, ?)""",
        projects,
    )
    logger.info("Project seeded successfully!")
    return cursor.lastrowid


def seed_Milestone(cursor, project_id=1):
    milestones = [
        ("UI Mockups Approved", project_id, "2026-09-15"),
        ("Backend API Deployed", project_id, "2026-10-30"),
    ]
    cursor.executemany(
        """INSERT INTO Milestone (name, project_id, due_date)
           VALUES (?, ?, ?)""",
        milestones,
    )
    logger.info("Milestones seeded successfully!")

    # Calculate the first milestone_id created in this specific batch
    return cursor.lastrowid 


def seed_user(cursor):
    users = [
        ("Alice Smith", 28, "alice@example.com"),
        ("Bob Jones", 34, "bob@example.com"),
    ]
    cursor.executemany(
        """INSERT OR IGNORE INTO User (name, age, email)
           VALUES (?, ?, ?)""",
        users,
    )
    logger.info("Users seeded successfully!")

   

def seed_task(cursor, milestone_id=1, project_id=1):
    
    tasks = [
        ("Design Wireframes", 1, milestone_id, project_id, "completed"),
        ("Setup Database Schema",2, milestone_id, project_id, "in-progress"),
        ("Create Auth Endpoints", 2, 2, project_id, "pending"),
        ("User Testing", 1, 2, project_id, "pending"),
    ]
    cursor.executemany(
        """INSERT INTO Task (name, user_id, milestone_id, project_id, status)
           VALUES (?, ?, ?, ?, ?)""",
        tasks)
    cursor.execute("select * from Task")
    print(cursor.fetchall())
    logger.info("Tasks seeded successfully!")








if __name__ == "__main__":
    conn = get_connection()
    init_db(conn)
    cursor = conn.cursor()
    
    project_id = seed_project(cursor)
    seed_Milestone(cursor, project_id=project_id)
    seed_user(cursor)
    seed_task(cursor)
    conn.commit()
