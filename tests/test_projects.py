def test_add_project_success(client):
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
        "name": "UFO Resort Project",
        "description": "Building a tiny house resort in a flower field",
        "start_date": "2026-11-01",
        "finish_date": "2027-05-01"
    }

    response=client.post("/project",json=payloads)
    assert response.status_code==201

    data=response.get_json()
    assert data["message"] == "Project created"
    assert "project_id" in data


def test_add_project_missing_name(client):
    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})
    
    
    payload = {
        "description": "Missing name field",
        "start_date": "2026-11-01",
        "finish_date": "2027-05-01"
    }
    response = client.post("/project", json=payload)
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_search_project(client):
    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})

    response=client.get("/project")
    assert response.status_code==200

    data = response.get_json()
    assert "projects" in data



def test_delete_project_by_id_nonexsistence(client):
    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})

    
    response=client.delete("/project/99")
    assert response.status_code==404


def test_delete_project_success(client):
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
            "name": "UFO Resort Project",
            "description": "Building a tiny house resort in a flower field",
            "start_date": "2026-11-01",
            "finish_date": "2027-05-01"
        }
    
    response=client.post("/project",json=payloads)
    data=response.get_json()
    project_id=int(data["project_id"])
    
    response_2=client.delete(f"/project/{project_id}")
    assert response_2.status_code==201


def test_update_project_no_info(client):
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
                "name": "UFO Resort Project",
                "description": "Building a tiny house resort in a flower field",
                "start_date": "2026-11-01",
                "finish_date": "2027-05-01"
            }
        
    response=client.post("/project",json=payloads)
    data=response.get_json()
    project_id=int(data["project_id"])

    response_2=client.put(f"/project/{project_id}")
    assert response_2.status_code==400

def test_update_project_with_info(client):

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
                "name": "UFO Resort Project",
                "description": "Building a tiny house resort in a flower field",
                "start_date": "2026-11-01",
                "finish_date": "2027-05-01"
            }     
    response=client.post("/project",json=payloads)
    data=response.get_json()
    project_id=int(data["project_id"])

    
    payloads_2={
                    "name": "Leggo project",
                    "description": "Building a leggo house resort in a flower field",
                    "start_date": "2026-12-05",
                    "finish_date": "2029-07-09"
                }
            
    response_2=client.put(f"/project/{project_id}",json=payloads_2)
    assert response_2.status_code==201

    
    