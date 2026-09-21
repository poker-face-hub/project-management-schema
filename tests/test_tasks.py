def test_health_check(client):
    response=client.get("/")
    assert response.status_code==200

    data=response.get_json()
    assert data["status"]=="ok"
    assert data["message"]=="server is running"


def test_get_all_tasks(client):
    response=client.get("/task")
    assert response.status_code==200
    data=response.get_json()
    assert data is not None


def test_delete_task_by_id_nonexsistence(client):
    response=client.delete("/task/99")
    assert response.status_code==404

    data=response.get_json()
    assert "error" in data
    assert data["error"]=="Task 99 does not exists"


def test_create_task_success(client):
    payloads={"name": "Build Pytest Suite",
        "user_id": 1,
        "milestone_id": 1,
        "project_id":1}
    
    response=client.post("/task",json=payloads)
    assert response.status_code== 201

    data=response.get_json()
    assert data["message"]=="Task created"


def test_create_task_missing_fields(client):
    payloads={"name": "Build Pytest Suite",
            "milestone_id": 1,
            "project_id":1}
        
    response=client.post("/task",json=payloads)
    assert response.status_code== 404

    data=response.get_json()
    assert "error" in data
