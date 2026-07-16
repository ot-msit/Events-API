import requests

def test_api_health(base_url):
    response = requests.get(f"{base_url}/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_api_openapi_spec_is_served(base_url):
    response = requests.get(f"{base_url}/api/openapi.yaml")
    assert response.status_code == 200
    assert "openapi" in response.text[:200]

# User

def test_api_register_user(base_url, credentials):
    response = requests.post(f"{base_url}/api/auth/register", json=credentials)
    assert response.status_code == 201
    data_received = response.json()
    assert data_received["message"] == "User created successfully"
    assert data_received["user"].get("username") == credentials["username"]

def test_api_register_user_duplicated_username_fails(base_url, credentials):
    response = requests.post(f"{base_url}/api/auth/register", json=credentials)
    assert response.status_code == 201
    response = requests.post(f"{base_url}/api/auth/register", json=credentials)
    assert response.status_code == 400

def test_api_user_login_returns_token(base_url, credentials):
    # register new user
    response = requests.post(f"{base_url}/api/auth/register", json=credentials)
    assert response.status_code == 201
    # try to log in
    response = requests.post(f"{base_url}/api/auth/login", json=credentials)
    assert response.status_code == 200
    data_received = response.json()
    assert data_received["access_token"] != ""
    assert data_received["user"].get("username") == credentials["username"]

def test_api_user_login_without_username_fails(base_url, credentials):
    credentials.update({"username": ""})
    response = requests.post(f"{base_url}/api/auth/login", json=credentials)
    assert response.status_code == 400

def test_api_user_login_without_password_fails(base_url, credentials):
    credentials.update({"password": ""})
    response = requests.post(f"{base_url}/api/auth/login", json=credentials)
    assert response.status_code == 400

def test_api_user_login_with_wrong_credentials_fails(base_url, credentials):
    # register new user
    response = requests.post(f"{base_url}/api/auth/register", json=credentials)
    assert response.status_code == 201
    # try to log in
    credentials.update({"password": "a-wrong_password"})
    response = requests.post(f"{base_url}/api/auth/login", json=credentials)
    assert response.status_code == 401

# Events

def test_api_get_events(base_url):
    response = requests.get(f"{base_url}/api/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_get_one_event(base_url, auth_headers, event):
    # create event
    response = requests.post(f"{base_url}/api/events", json=event, headers=auth_headers)
    assert response.status_code == 201
    event_id = response.json().get("id")
    # get this event
    response = requests.get(f"{base_url}/api/events/{event_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_api_create_event(base_url, auth_headers, event):
    response = requests.post(f"{base_url}/api/events", json=event, headers=auth_headers)
    assert response.status_code == 201
    data_received = response.json()
    assert data_received["title"] == event.get("title")
    assert data_received["description"] == event.get("description")
    assert data_received["date"] == event.get("date")
    assert data_received["location"] == event.get("location")
    assert data_received["capacity"] == event.get("capacity")
    assert data_received["is_public"] == event.get("is_public")

def test_api_create_event_without_login_fails(base_url, event):
    response = requests.post(f"{base_url}/api/events", json=event)
    assert response.status_code == 401

# rsvp

def test_api_rsvp_to_public_event(base_url, credentials, event):
    # register user
    response = requests.post(f"{base_url}/api/auth/register", json=credentials)
    assert response.status_code == 201
    # login
    response = requests.post(f"{base_url}/api/auth/login", json=credentials)
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    # create event
    response = requests.post(f"{base_url}/api/events", json=event, headers=auth_headers)
    assert response.status_code == 201
    event_id = response.json().get("id")
    # attend event
    response = requests.post(f"{base_url}/api/rsvps/event/{event_id}", json={"attending": True})
    assert response.status_code == 201
    assert response.json()["attending"] is True