def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activity = response.json()[expected_activity]
    assert activity["description"] == "Learn strategies and compete in chess tournaments"
    assert activity["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert activity["max_participants"] == 12
    assert activity["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    # Arrange
    activity = "Art Club"
    email = "alex@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_handles_encoded_activity_name(client):
    # Arrange
    activity = "Programming Class"
    email = "student+club@mergington.edu"

    # Act
    response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert client.get("/activities").json()[activity]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity = "Robotics Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(client):
    # Arrange
    activity = "Art Club"

    # Act
    response = client.post(f"/activities/{activity}/signup")

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]


def test_same_email_can_join_different_activities(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    chess_response = client.post("/activities/Chess Club/signup", params={"email": email})
    art_response = client.post("/activities/Art Club/signup", params={"email": email})

    # Assert
    assert chess_response.status_code == 200
    assert art_response.status_code == 200
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]
    assert email in activities["Art Club"]["participants"]


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_unregister_rejects_missing_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "not-registered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity = "Robotics Club"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_cannot_remove_participant_twice(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    first_response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )
    second_response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 404
    assert second_response.json() == {"detail": "Participant not found"}
