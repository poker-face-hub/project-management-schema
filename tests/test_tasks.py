def create_test_dependencies(client):
    """Helper to register user, log in, create a project and milestone, and return their IDs."""
    client.post("/auth/register", json={
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    })
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})

    project_res = client.post("/project", json={
        "name": "Test Project",
        "description": "Testing tasks",
        "start_date": "2026-11-01",
        "finish_date": "2027-05-01"
    })
    project_id = project_res.get_json()["project_id"]

    milestone_res = client.post("/milestone", json={
        "name": "Test Milestone",
        "project_id": project_id,
        "due_date": "2026-12-01"
    })
    milestone_id = milestone_res.get_json()["milestone_id"]

    return project_id, milestone_id


def test_health_check(client):
    response=client.get("/")
    assert response.status_code==200

    data=response.get_json()
    assert data["status"]=="ok"
    assert data["message"]=="server is running"


def test_get_all_tasks(client):
    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})

    response=client.get("/task")
    assert response.status_code==200
    data=response.get_json()
    assert data is not None


def test_delete_task_by_id_nonexsistence(client):
    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})

    response=client.delete("/task/99")
    assert response.status_code==404

    data=response.get_json()
    assert "error" in data
    assert data["error"]=="Task 99 does not exists"


def test_create_task_success(client):
    project_id,milestone_id=create_test_dependencies(client)
    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})


    payloads={"name": "Build Pytest Suite",
        "milestone_id": milestone_id,
        "project_id":project_id}
    
    response=client.post("/task",json=payloads)
    assert response.status_code== 201

    data=response.get_json()
    assert data["message"]=="Task created"


def test_create_task_missing_fields(client):
    project_id,milestone_id=create_test_dependencies(client)

    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})


    payloads={"name": "Build Pytest Suite",
            "project_id":project_id}
        
    response=client.post("/task",json=payloads)
    assert response.status_code== 404

    data=response.get_json()
    assert "error" in data


def test_update_task_success(client):
    project_id,milestone_id=create_test_dependencies(client)

    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})


    payload_create={"name": "Build Pytest Suite",
            "milestone_id": milestone_id,
            "project_id":project_id}
    client.post("/task",json=payload_create)

    payloads={
        "name": "Updated Task Name",
        "status": "completed",
        
    }
    response=client.put("/task/1",json=payloads)
    data=response.get_json()

    assert response.status_code==200
    assert  "message" in data



def test_update_task_failed(client):
    project_id,milestone_id=create_test_dependencies(client)

    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})


    payload_create={"name": "Build Pytest Suite",
            "milestone_id": milestone_id,
            "project_id":project_id}
    client.post("/task",json=payload_create)

    payloads={
        "name": "Updated Task Name",
        "status": "completed",
        "milestone_id": "mew",
        "project_id": 1
    }
    response=client.put("/task/1",json=payloads)
    data=response.get_json()

    assert response.status_code==400
    assert  "error" in data


def test_update_task_nonexistence_task(client):
    project_id,milestone_id=create_test_dependencies(client)

    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})


    payloads={
            "name": "Updated Task Name",
            "status": "completed",
            "milestone_id": milestone_id,
            "project_id": project_id
        }
    response=client.put("/task/99",json=payloads)

    assert response.status_code==404
    data=response.get_json()
    assert "error" in data



    
def test_update_task_nonexistence_json(client):
    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})



    response=client.put("/task/1",json={})
    assert response.status_code==400
    data=response.get_json()
    assert "error" in data
    

