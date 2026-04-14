"""Tests for the task CRUD endpoints."""

from fastapi.testclient import TestClient


def test_create_task_returns_201_and_echoes_fields(client: TestClient) -> None:
    response = client.post(
        "/tasks", json={"title": "Buy milk", "description": "2% please"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["description"] == "2% please"
    assert body["completed"] is False
    assert isinstance(body["id"], int)


def test_create_task_returns_422_when_title_missing(client: TestClient) -> None:
    response = client.post("/tasks", json={"description": "no title here"})

    assert response.status_code == 422


def test_list_tasks_is_empty_initially(client: TestClient) -> None:
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_returns_created_tasks(client: TestClient) -> None:
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})

    response = client.get("/tasks")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    titles = {task["title"] for task in body}
    assert titles == {"First", "Second"}


def test_get_task_returns_correct_task(client: TestClient) -> None:
    created = client.post(
        "/tasks", json={"title": "Read book", "description": "chapter 3"}
    ).json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["title"] == "Read book"
    assert body["description"] == "chapter 3"


def test_get_task_returns_404_for_unknown_id(client: TestClient) -> None:
    response = client.get("/tasks/99999")

    assert response.status_code == 404


def test_update_task_updates_only_provided_fields(client: TestClient) -> None:
    created = client.post(
        "/tasks", json={"title": "A", "description": "desc"}
    ).json()

    response = client.put(f"/tasks/{created['id']}", json={"title": "B"})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "B"
    assert body["description"] == "desc"


def test_update_task_returns_404_for_unknown_id(client: TestClient) -> None:
    response = client.put("/tasks/99999", json={"title": "nope"})

    assert response.status_code == 404


def test_delete_task_returns_204_and_task_is_gone(client: TestClient) -> None:
    created = client.post("/tasks", json={"title": "Temp"}).json()

    delete_response = client.delete(f"/tasks/{created['id']}")
    get_response = client.get(f"/tasks/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_delete_task_returns_404_for_unknown_id(client: TestClient) -> None:
    response = client.delete("/tasks/99999")

    assert response.status_code == 404
