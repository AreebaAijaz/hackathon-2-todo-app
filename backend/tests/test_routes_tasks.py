"""Integration tests for task routes using TestClient."""

import pytest
from fastapi import status

from tests.conftest import TEST_USER_ID


class TestTaskRoutes:
    """Integration tests for task CRUD operations."""

    def test_create_task_with_valid_data(self, client):
        """Test POST /api/tasks with valid data returns 201."""
        response = client.post(
            "/api/tasks",
            json={"title": "Buy groceries", "description": "Milk and eggs"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk and eggs"
        assert data["user_id"] == TEST_USER_ID
        assert data["completed"] is False
        assert "id" in data

    def test_create_task_with_empty_title_fails(self, client):
        """Test POST /api/tasks with empty title returns 422."""
        response = client.post(
            "/api/tasks",
            json={"title": "", "description": "Test"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_tasks_returns_list(self, client):
        """Test GET /api/tasks returns list."""
        response = client.get("/api/tasks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_list_tasks_after_creating_tasks(self, client):
        """Test GET /api/tasks returns created tasks."""
        # Create two tasks
        client.post("/api/tasks", json={"title": "Task 1"})
        client.post("/api/tasks", json={"title": "Task 2"})

        # List tasks
        response = client.get("/api/tasks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        # Tasks should be ordered by created_at desc, so Task 2 first
        assert data[0]["title"] == "Task 2"
        assert data[1]["title"] == "Task 1"

    def test_get_task_by_id_existing(self, client):
        """Test GET /api/tasks/{id} for existing task returns 200."""
        # Create a task
        create_response = client.post(
            "/api/tasks",
            json={"title": "Test Task"}
        )
        task_id = create_response.json()["id"]

        # Get the task
        response = client.get(f"/api/tasks/{task_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"

    def test_get_task_by_id_nonexistent(self, client):
        """Test GET /api/tasks/{id} for nonexistent task returns 404."""
        response = client.get("/api/tasks/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Task not found"

    def test_update_task_with_new_title(self, client):
        """Test PUT /api/tasks/{id} with new title returns 200."""
        # Create a task
        create_response = client.post(
            "/api/tasks",
            json={"title": "Original Title"}
        )
        task_id = create_response.json()["id"]

        # Update the task
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"title": "Updated Title"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["id"] == task_id

    def test_update_task_with_new_description(self, client):
        """Test PUT /api/tasks/{id} with new description."""
        # Create a task
        create_response = client.post(
            "/api/tasks",
            json={"title": "Test Task", "description": "Original"}
        )
        task_id = create_response.json()["id"]

        # Update description
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"description": "Updated description"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["title"] == "Test Task"  # Title unchanged

    def test_update_task_with_empty_update(self, client):
        """Test PUT /api/tasks/{id} with no fields updates nothing."""
        # Create a task
        create_response = client.post(
            "/api/tasks",
            json={"title": "Test Task"}
        )
        task_id = create_response.json()["id"]

        # Update with empty body
        response = client.put(f"/api/tasks/{task_id}", json={})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Test Task"

    def test_delete_task_existing(self, client):
        """Test DELETE /api/tasks/{id} returns 200."""
        # Create a task
        create_response = client.post(
            "/api/tasks",
            json={"title": "Task to Delete"}
        )
        task_id = create_response.json()["id"]

        # Delete the task
        response = client.delete(f"/api/tasks/{task_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Task deleted successfully"

        # Verify task is deleted
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_nonexistent(self, client):
        """Test DELETE /api/tasks/{id} for nonexistent task returns 404."""
        response = client.delete("/api/tasks/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Task not found"

    def test_toggle_task_complete(self, client):
        """Test PATCH /api/tasks/{id}/complete toggles completed status."""
        # Create a task (starts as not completed)
        create_response = client.post(
            "/api/tasks",
            json={"title": "Task to Complete"}
        )
        task_id = create_response.json()["id"]

        # Toggle to completed
        response = client.patch(f"/api/tasks/{task_id}/complete")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["completed"] is True

        # Toggle back to not completed
        response = client.patch(f"/api/tasks/{task_id}/complete")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["completed"] is False

    def test_toggle_task_complete_nonexistent(self, client):
        """Test PATCH /api/tasks/{id}/complete for nonexistent task."""
        response = client.patch("/api/tasks/99999/complete")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Task not found"

    def test_user_isolation(self, client, session):
        """Test tasks are isolated by user_id."""
        # Create a task as test-user
        create_response = client.post(
            "/api/tasks",
            json={"title": "Test User Task"}
        )
        task_id = create_response.json()["id"]

        # Override get_current_user to return different user
        from main import app
        from auth.dependencies import get_current_user

        def get_different_user():
            return "different-user-id"

        app.dependency_overrides[get_current_user] = get_different_user

        # Try to get the task as different user
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # List tasks should return empty for different user
        response = client.get("/api/tasks")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

        # Reset override
        from tests.conftest import TEST_USER_ID

        def get_current_user_override():
            return TEST_USER_ID

        app.dependency_overrides[get_current_user] = get_current_user_override

    def test_health_endpoint(self, client):
        """Test GET /health returns 200."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test GET / returns 200."""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data

    def test_create_task_without_description(self, client):
        """Test creating task without description uses default empty string."""
        response = client.post(
            "/api/tasks",
            json={"title": "Task without description"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["description"] == ""

    def test_update_task_nonexistent(self, client):
        """Test updating nonexistent task returns 404."""
        response = client.put(
            "/api/tasks/99999",
            json={"title": "Updated"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Task not found"

    def test_task_timestamps(self, client):
        """Test task has created_at and updated_at timestamps."""
        response = client.post(
            "/api/tasks",
            json={"title": "Test Timestamps"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data

    def test_multiple_tasks_ordering(self, client):
        """Test tasks are ordered by created_at descending."""
        # Create tasks in order
        client.post("/api/tasks", json={"title": "First"})
        client.post("/api/tasks", json={"title": "Second"})
        client.post("/api/tasks", json={"title": "Third"})

        response = client.get("/api/tasks")
        data = response.json()

        # Should be in reverse order (newest first)
        assert data[0]["title"] == "Third"
        assert data[1]["title"] == "Second"
        assert data[2]["title"] == "First"
