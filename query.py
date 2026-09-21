import logging
import sqlite3
from database import get_connection, init_db
from exception import DatabaseError, RecordNotFoundError, ValidationError
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
    return cursor.lastrowid - len(milestones) + 1


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

    # Dynamically query existing user IDs to guarantee valid Foreign Keys
    cursor.execute("SELECT id FROM User ORDER BY id ASC LIMIT 2")
    user_rows = cursor.fetchall()
    return [r[0] for r in user_rows]


def seed_task(cursor, milestone_id=1, project_id=1, user_ids=None):
    if not user_ids or len(user_ids) < 2:
        u1, u2 = 1, 2
    else:
        u1, u2 = user_ids[0], user_ids[1]

    tasks = [
        ("Design Wireframes", u1, milestone_id, project_id, "completed"),
        ("Setup Database Schema", u2, milestone_id, project_id, "in-progress"),
        ("Create Auth Endpoints", u2, milestone_id, project_id, "pending"),
        ("User Testing", u1, milestone_id, project_id, "pending"),
    ]
    cursor.executemany(
        """INSERT INTO Task (name, user_id, milestone_id, project_id, status)
           VALUES (?, ?, ?, ?, ?)""",
        tasks,
    )
    logger.info("Tasks seeded successfully!")


def run_system_integration_test(project_id):
    with Datamanager() as db:
        print("== STAGE 1 : Infrastructure and Indexes ==")
        print("___Applying performance indexes___")
        try:
            if db.apply_schema_indexes():
                print("Indexes applied successfully.")
        except DatabaseError as e:
            print(f"500 Database Error: {e}")

        print("\n== STAGE 2: Dynamic Keyword Search ==")
        print("____Keyword search (Alice)____")
        print(db.search_tasks(keywords="Alice"))

        print("____Keyword search (schema) and status=pending____")
        print(db.search_tasks(keywords="Alice", status="pending"))

        print("\n== STAGE 3: Atomic Task Transfer ==")
        print("___Testing task transfer transaction___")
        print(f"Transfer status : {db.transfer_user_task(1, 2)}")
        print(
            f"Transfer status (invalid user, should fail) : {db.transfer_user_task(2, 999)}"
        )

        print("\n== STAGE 4: Safe Exception Handling ==")
        print("____Testing safe Project deletion____")
        try:
            db.delete_project_safely(999, cascade=False)
        except RecordNotFoundError as e:
            print(f"404 Not Found : {e}")

        try:
            db.delete_project_safely(project_id, cascade=False)
        except ValidationError as e:
            print(f"400 Bad Request : {e}")

        print("\n== STAGE 5: Cascading Relational Delete ==")
        try:
            if db.delete_project_safely(project_id, cascade=True):
                print("Project and all child entities deleted successfully.")
        except DatabaseError as e:
            print(f"500 Database Error : {e}")

        print("\n== STAGE 6: General CRUD & Re-seeding Operations ==")
        print(db.get_pending_task())
        print(db.get_tasks_count_per_user())

        # Re-seed fresh records after cascade deletion
        new_project_id = seed_project(db.cursor)
        new_milestone_id = seed_Milestone(db.cursor, project_id=new_project_id)
        user_ids = seed_user(db.cursor)
        seed_task(
            db.cursor,
            milestone_id=new_milestone_id,
            project_id=new_project_id,
            user_ids=user_ids,
        )
        db.conn.commit()

        if (
            db.add_task(
                "new-task",
                user_ids[0],
                milestone_id=new_milestone_id,
                project_id=new_project_id,
            )
            == 1
        ):
            print("Task added successfully!")

        print("\n== After Re-seeding ==")
        print("All tasks: ", db.get_task())
        print("Pending tasks: ", db.get_task(status="pending"))
        print(
            "Pending tasks of user 1: ",
            db.get_task(status="pending", user_id=user_ids[0]),
        )

        if db.update_task(1):
            print("Task updated!")
        else:
            print("Task couldn't update!")

        print("Summary of project: ", db.get_project_summary(new_project_id))

        print("\n____USER WORKLOAD SUMMARY____")
        workloads = db.get_user_workload_summary()
        for w in workloads:
            print(w)


if __name__ == "__main__":
    conn = get_connection()
    init_db(conn)
    cursor = conn.cursor()
    try:
        project_id = seed_project(cursor)
        milestone_id = seed_Milestone(cursor, project_id=project_id)
        user_ids = seed_user(cursor)
        seed_task(
            cursor,
            milestone_id=milestone_id,
            project_id=project_id,
            user_ids=user_ids,
        )
        conn.commit()
        logger.info("Database created and successfully seeded!")

        run_system_integration_test(project_id)

    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Database error during seeding: {e}")




















'''import logging
import sqlite3
from database import get_connection, init_db
from exception import DatabaseError, RecordNotFoundError, ValidationError
from manager import Datamanager

logger = logging.getLogger(__name__)


def seed_project(cursor):
    projects = ("avy company", "website design", "2026-09-01", "2026-12-01")

    cursor.execute(
        """insert into Project(name,description,start_date,finish_date)
    values(?,?,?,?)""",
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
        """insert into Milestone(name,project_id,due_date)
    values(?,?,?)""",
        milestones,
    )
    logger.info("Milestones seeded successfully!")

    # Calculate the first milestone ID inserted in this batch
    first_milestone_id = cursor.lastrowid - len(milestones) + 1
    return first_milestone_id


def seed_user(cursor):
    users = [
        ("Alice Smith", 28, "alice@example.com"),
        ("Bob Jones", 34, "bob@example.com"),
    ]

    cursor.executemany(
        """insert or ignore into User(name,age,email)
    values(?,?,?)""",
        users,
    )

    logger.info("Users seeded successfully!")

    # Fetch valid user IDs directly from DB to avoid FK failure
    cursor.execute("SELECT id FROM User ORDER BY id ASC LIMIT 2")
    user_rows = cursor.fetchall()
    return [r[0] for r in user_rows]


def seed_task(cursor, milestone_id=1, project_id=1, user_ids=None):
    if not user_ids or len(user_ids) < 2:
        u1, u2 = 1, 2
    else:
        u1, u2 = user_ids[0], user_ids[1]

    tasks = [
        ("Design Wireframes", u1, milestone_id, project_id, "completed"),
        ("Setup Database Schema", u2, milestone_id, project_id, "in-progress"),
        ("Create Auth Endpoints", u2, milestone_id, project_id, "pending"),
        ("User Testing", u1, milestone_id, project_id, "pending"),
    ]

    cursor.executemany(
        """insert into Task(name,user_id,milestone_id,project_id,status)
    values(?,?,?,?,?)""",
        tasks,
    )

    logger.info("Task seeded successfully!")


def run_system_integration_test(project_id):
    with Datamanager() as db:
        print("==STAGE 1 : infrastructure and indexes==")
        print("___Applying performance indexes___")
        try:
            if db.apply_schema_indexes():
                print("indexes applied successfully.")
        except DatabaseError as e:
            print(f"500 database Error: {e}")

        print("==STAGE 2: dynamic keyword search==")
        print("____keyword search (Alice)____")
        print(db.search_tasks(keywords="Alice"))

        print("____keyword search (schema) and status= pending____")
        print(db.search_tasks(keywords="Alice", status="pending"))

        print("STAGE 3: atomic Task transfer==")
        print("___Testing task transfer transaction___")
        print(f"Transfer status : {db.transfer_user_task(1, 2)}")
        print(
            f"Transfer status(invalid user, should be failed) : {db.transfer_user_task(2, 999)}"
        )

        print("==STAGE 4: exception handling safely==")
        print("____Testing safe Project deletion___")
        try:
            db.delete_project_safely(999, cascade=False)
        except RecordNotFoundError as e:
            print(f"404 not found : {e}")

        try:
            db.delete_project_safely(project_id, cascade=False)
        except ValidationError as e:
            print(f"400 Bad request : {e}")

        print("==STAGE 5: cascading relational delete==")
        try:
            if db.delete_project_safely(project_id, cascade=True):
                print("project and all child entities deleted successfully")
        except DatabaseError as e:
            print(f"500 database Error : {e}")

        print("==STAGE 6: General CRUD operations==")
        print(db.get_pending_task())
        print(db.get_tasks_count_per_user())

        # Re-seed fresh records after cascade delete
        new_project_id = seed_project(db.cursor)
        new_milestone_id = seed_Milestone(db.cursor, project_id=new_project_id)
        user_ids = seed_user(db.cursor)
        seed_task(
            db.cursor,
            milestone_id=new_milestone_id,
            project_id=new_project_id,
            user_ids=user_ids,
        )
        db.conn.commit()

        if (
            db.add_task(
                "new-task",
                user_ids[0],
                milestone_id=new_milestone_id,
                project_id=new_project_id,
            )
            == 1
        ):
            print("task added successfully!")

        print("== after re-seeding ==")
        print("all task: ", db.get_task())
        print("pending task: ", db.get_task(status="pending"))
        print(
            "pending task of user: ",
            db.get_task(status="pending", user_id=user_ids[0]),
        )

        if db.update_task(1):
            print("Task updated!")
        else:
            print("Task couldn't update!")

        print("summary of project: ", db.get_project_summary(new_project_id))

        print("____USER WORKLOAD SUMMARY____")
        workloads = db.get_user_workload_summary()
        for w in workloads:
            print(w)


if __name__ == "__main__":
    conn = get_connection()
    init_db(conn)
    cursor = conn.cursor()
    try:
        project_id = seed_project(cursor)
        milestone_id = seed_Milestone(cursor, project_id=project_id)
        user_ids = seed_user(cursor)
        seed_task(
            cursor,
            milestone_id=milestone_id,
            project_id=project_id,
            user_ids=user_ids,
        )
        conn.commit()
        logger.info("Database created and successfully seeded!")

        run_system_integration_test(project_id)

    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Database error during seeding: {e}")

'''





























'''from database import get_connection,init_db
import logging
logger=logging.getLogger(__name__)
import sqlite3
from manager import Datamanager
from exception import DatabaseError,RecordNotFoundError,ValidationError


def seed_project(cursor):
    projects=("avy company","website design","2026-09-01",
            "2026-12-01")

    cursor.execute("""insert into Project(name,description,start_date,finish_date)
    values(?,?,?,?)""",projects)

    logger.info("Project seeded successfully!")

    return cursor.lastrowid



def seed_Milestone(cursor,project_id=1):
    milestones=[("UI Mockups Approved",project_id, "2026-09-15"),
        ("Backend API Deployed", project_id, "2026-10-30"),]

    cursor.executemany("""insert into Milestone(name,project_id,due_date)
    values(?,?,?)""",milestones)
    logger.info("Milestones seeded successfully!")
    return cursor.lastrowid
   

def seed_user(cursor):
    users=[("Alice Smith", 28, "alice@example.com"),
        ("Bob Jones", 34, "bob@example.com"),]

    cursor.executemany("""insert or ignore into User(name,age,email)
    values(?,?,?)""",users)

    logger.info("Users seeded successfully!")

def seed_task(cursor,milestone_id=None,project_id=1):
    tasks=[("Design Wireframes", 1, milestone_id, project_id, "completed"),
        ("Setup Database Schema", 2, milestone_id, project_id, "in-progress"),
        ("Create Auth Endpoints", 2, milestone_id, project_id, "pending"),
        ("User Testing", 1, milestone_id, project_id, "pending"),]

    cursor.executemany("""insert into Task(name,user_id,milestone_id,project_id,status)
    values(?,?,?,?,?)""",tasks)

    logger.info("Task seeded successfully!")


def run_system_integration_test(project_id):
        with Datamanager() as db:
            print("==STAGE 1 : infrastucture and indexes==")
            print("___Appling performances indexes___")
            try:
                if db.apply_schema_indexes():
                    print("indexes applied successfully.")
            except DatabaseError as e:
                print(f"500 database Error: {e}")

            
            print("==STAGE 2: dynamic keyword search==")
            print("____keyword search (Alice)____")
            print(db.search_tasks(keywords="Alice"))

            print("____keyword search (schema) and status= pending____")
            print(db.search_tasks(keywords="Alice",status="pending"))

            print("STAGE 3: automic Task transfer==")
            print("___Testing task  transfer transaction___")
            print(f"Transfer status : {db.transfer_user_task(1,2)}")
            print(f"Transfer status(invalid user ,should be failed) : {db.transfer_user_task(2,999)}")


            print("==STAGE 4: exception handling safely")
            print("____Testing safe Project deletion___")
            try:
                db.delete_project_safely(999,cascade=False)
            except RecordNotFoundError as e:
                print(f"404 not found : {e}")

            try:
                db.delete_project_safely(project_id,cascade=False)
            except ValidationError as e:
                print(f"400 Bad request : {e}")
            
            print("==STAGE 5: casecading relational delete==")
            try:
                if db.delete_project_safely(project_id,cascade=True):
                    print("project and all child entities deleted successfully")
            except DatabaseError as e:
                        print(f"500 database Error : {e}")
            
            

            print("==STAGE 6: General crud operation==")
            print(db.get_pending_task())
            print(db.get_tasks_count_per_user())


            print("== DEBUG STATE BEFORE RE-SEEDING ==")
            print("Users in DB:", db.cursor.execute("SELECT id FROM User").fetchall())
            print("Projects in DB:", db.cursor.execute("SELECT id FROM Project").fetchall())
            print("Milestones in DB:", db.cursor.execute("SELECT id FROM Milestone").fetchall())
                        
            
            new_project_id=seed_project(db.cursor)
            new_milestone_id=seed_Milestone(db.cursor,project_id=new_project_id)
            seed_task(db.cursor,milestone_id=new_milestone_id,project_id=new_project_id)
            db.conn.commit()
            
            if db.add_task("new-task",1,milestone_id=new_milestone_id,project_id=new_project_id)==1:
                print("task added successfully!")
            print("== after re-seeding ==")
            print("all task: ",db.get_task())
            print("pending task: ",db.get_task(status="pending"))
            print("pending task of user 1: ",db.get_task(status="pending",user_id=1))

            if db.update_task(1) :
                print("Task updated!")
            else :
                print("Task couldn't update!")

            print("summary of project: ",db.get_project_summary(new_project_id))

            print("____USER WORKLOAD SUMMARY____")
            workloads=db.get_user_workload_summary()
            for w in workloads:
                print(w)




if __name__=="__main__":
    conn=get_connection()
    init_db(conn)
    cursor=conn.cursor()
    try:
        project_id=seed_project(cursor)
        milestone_id=seed_Milestone(cursor,project_id=project_id)
        seed_user(cursor)
        seed_task(cursor,milestone_id=milestone_id,project_id=project_id)
        conn.commit()
        logger.info("Database created and successfully seeded!")
        run_system_integration_test(project_id)


    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Database error during seeding: {e}")
         
            '''



        
        