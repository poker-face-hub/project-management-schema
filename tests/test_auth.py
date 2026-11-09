def test_register_user_success(client):
    payloads={
        "name": "Alex Developer",
        "username": "alexdev",
        "age": 21,
        "email": "alex@example.com",
        "password": "securepassword123"
    }

    respose=client.post("auth/register",json=payloads)
    assert respose.status_code == 201
    assert "user_id" in respose.get_json()



def test_register_duplicate_username(client):
    payloads={
                "name": "Alex Developer",
                "username": "alexdev",
                "age": 21,
                "email": "alex@example.com",
                "password": "securepassword123"
            }
         
    client.post("auth/register",json=payloads)

    payloads={
            "name": "Alex Developer",
            "username": "alexdev",
            "age": 21,
            "email": "alex@example.com",
            "password": "securepassword123"
        }
     
    respose=client.post("auth/register",json=payloads)
    assert respose.status_code== 401
    assert "error" in respose.get_json()


def test_login_success(client):
    payloads={
                "name": "Alex Developer",
                "username": "alexdev",
                "age": 21,
                "email": "alex@example.com",
                "password": "securepassword123"
            }
         
    client.post("auth/register",json=payloads)

    payloads={"username": "alexdev",
        "password": "securepassword123"}
    response=client.post("auth/login",json=payloads)
    assert response.status_code == 200


def test_login_failure(client):
    payloads={
                "name": "Alex Developer",
                "username": "alexdev",
                "age": 21,
                "email": "alex@example.com",
                "password": "securepassword123"
            }
         
    client.post("auth/register",json=payloads)
    
    payloads={"username": "alexdev",
        "password": "wrongpassword123"}
    response=client.post("auth/login",json=payloads)
    assert response.status_code == 401

    