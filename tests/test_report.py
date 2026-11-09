
def test_get_user_summary_success(client):
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

    payloads={"name": "Build Pytest Suite",
            "milestone_id": milestone_id,
            "project_id":project_id}
        
    client.post("/task",json=payloads)

    response=client.get("/report")
    assert response.status_code==200


def test_get_user_summary_unauthorise(client):
    response=client.get("/report")
    assert response.status_code==401


def test_get_user_summary_with_project_id(client):
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

    payloads={"name": "Build Pytest Suite",
            "milestone_id": milestone_id,
            "project_id":project_id}
        
    client.post("/task",json=payloads)

    response=client.get(f"/report?project_id={project_id}")
    assert response.status_code==200



def test_get_user_summary_nonexistent_project_id(client):
    client.post("/auth/register", json={
            "name": "Project Owner",
            "username": "owner1",
            "age": 25,
            "email": "owner@example.com",
            "password": "password123"
        })
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})


    response=client.get("/report?project_id=99")
    assert response.status_code==200


def test_get_user_summary_invalid_project_id(client):
    client.post("/auth/register", json={
            "name": "Project Owner",
            "username": "owner1",
            "age": 25,
            "email": "owner@example.com",
            "password": "password123"
        })
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})


    response=client.get("/report?project_id=abc")
    assert response.status_code==401
    
    
    