def test_add_milestone_success(client):
    user_payload = {
        "name": "Project Owner",
        "username": "owner1",
        "age": 25,
        "email": "owner@example.com",
        "password": "password123"
    }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})

    project_payloads={
        "name": "UFO Resort Project",
        "description": "Building a tiny house resort in a flower field",
        "start_date": "2026-11-01",
        "finish_date": "2027-05-01"
    }

    project_response=client.post("/project",json=project_payloads)
    project_data=project_response.get_json()
    project_id=project_data["project_id"] 


    payloads={
        "name": "creating the body",
        "project_id": project_id,
        "due_date": "2026-11-01"
    }

    response=client.post("/milestone",json=payloads)
    assert response.status_code==201

    data=response.get_json()
    assert data["message"] == "milestone created"
    assert "milestone_id" in data




def test_add_milestone_missing_name(client):
    user_payload = {
            "name": "Project Owner",
            "username": "owner1",
            "age": 25,
            "email": "owner@example.com",
            "password": "password123"
        }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})

    project_payloads={
        "name": "UFO Resort Project",
        "description": "Building a tiny house resort in a flower field",
        "start_date": "2026-11-01",
        "finish_date": "2027-05-01"
    }

    project_response=client.post("/project",json=project_payloads)
    project_data=project_response.get_json()
    project_id=project_data["project_id"] 


    payloads={
        "project_id": project_id,
        "due_date": "2026-11-01"
    }

    
    
    response = client.post("/milestone", json=payloads)
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_search_milestone(client):
    user_payload = {
            "name": "Project Owner",
            "username": "owner1",
            "age": 25,
            "email": "owner@example.com",
            "password": "password123"
        }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})

    project_payloads={
        "name": "UFO Resort Project",
        "description": "Building a tiny house resort in a flower field",
        "start_date": "2026-11-01",
        "finish_date": "2027-05-01"
    }

    project_response=client.post("/project",json=project_payloads)
    

    response=client.get("/milestone")
    assert response.status_code==200

    data = response.get_json()
    assert "milestone" in data



def test_delete_milestone_by_id_nonexsistence(client):
    user_payload = {
            "name": "Project Owner",
            "username": "owner1",
            "age": 25,
            "email": "owner@example.com",
            "password": "password123"
        }
    client.post("/auth/register", json=user_payload)
    client.post("/auth/login", json={"username": "owner1", "password": "password123"})

    project_payloads={
        "name": "UFO Resort Project",
        "description": "Building a tiny house resort in a flower field",
        "start_date": "2026-11-01",
        "finish_date": "2027-05-01"
    }

    project_response=client.post("/project",json=project_payloads)


    response=client.delete("/milestone/99")
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

    project_payloads={
        "name": "UFO Resort Project",
        "description": "Building a tiny house resort in a flower field",
        "start_date": "2026-11-01",
        "finish_date": "2027-05-01"
    }

    project_response=client.post("/project",json=project_payloads)
    project_data=project_response.get_json()
    project_id=project_data["project_id"] 


    payloads={
        "name": "creating the body",
        "project_id": project_id,
        "due_date": "2026-11-01"
    }
    
    response=client.post("/milestone",json=payloads)
    data=response.get_json()
    milestone_id=int(data["milestone_id"])
    
    response_2=client.delete(f"/milestone/{milestone_id}")
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

    project_payloads={
        "name": "UFO Resort Project",
        "description": "Building a tiny house resort in a flower field",
        "start_date": "2026-11-01",
        "finish_date": "2027-05-01"
    }

    project_response=client.post("/project",json=project_payloads)
    project_data=project_response.get_json()
    project_id=project_data["project_id"] 


    payloads={
        "name": "creating the body",
        "project_id": project_id,
        "due_date": "2026-11-01"
    }
        
    response=client.post("/milestone",json=payloads)
    data=response.get_json()
    milestone_id=int(data["milestone_id"])

    response_2=client.put(f"/milestone/{milestone_id}")
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

    project_payloads={
        "name": "UFO Resort Project",
        "description": "Building a tiny house resort in a flower field",
        "start_date": "2026-11-01",
        "finish_date": "2027-05-01"
    }

    project_response=client.post("/project",json=project_payloads)
    project_data=project_response.get_json()
    project_id=project_data["project_id"] 


    payloads={
        "name": "creating the body",
        "project_id": project_id,
        "due_date": "2026-11-01"
    }



    response=client.post("/milestone",json=payloads)
    data=response.get_json()
    milestone_id=int(data["milestone_id"])

    
    payloads_2={
                    "name": "changing head",
                    "project_id": project_id,
                    "due_date": "2026-12-05"
                }
            
    response_2=client.put(f"/milestone/{milestone_id}",json=payloads_2)
    assert response_2.status_code==201

    
    