from database import get_connection, init_db
from manager import Datamanager


def test_manager_security():
    conn=get_connection()
    init_db(conn)
    conn.close()

    with get_connection() as c:
        c.execute(
            "INSERT or ignore INTO User (name, age, email) VALUES ('Alice', 25, 'alice@example.com')"
        )
        c.execute(
            "INSERT or ignore INTO User (name, age, email) VALUES ('Bob', 30, 'bob@example.com')"
        )
        c.execute(
            "INSERT or ignore INTO Project (name, description, start_date, finish_date) VALUES ('P1', 'Desc', '2026-01-01', '2026-02-01')"
        )
        c.commit()


    with Datamanager() as db:
        payload="' OR '1'='1"
        results=db.search_tasks(keywords=payload)

        assert len(results)==0,f"SECURITY FAIL: search_tasks leaked {len(results)} rows!"
        print("✓ Datamanager.search_tasks Security: PASSED")

        destructive_status="completed' ; DROP TABLE Task;--"

        updated=db.update_task(task_id=1,new_status=destructive_status)

        assert updated is False ,"SECURITY FAIL: Invalid status payload was executed!"
        print("✓ Datamanager.update_task Security: PASSED")

    print("\nSUCCESS: All Datamanager methods verified secure!")



if __name__=="__main__":
    test_manager_security()