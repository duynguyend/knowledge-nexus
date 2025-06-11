import pytest
from fastapi.testclient import TestClient
from backend.main import app  # Assuming your FastAPI app instance is named 'app' in main.py

import os
from unittest import mock # For patch.dict and patch
from unittest.mock import MagicMock, patch # Explicitly import MagicMock and patch
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from backend.agents.research_workflow import build_knowledge_nexus_workflow

client = TestClient(app)

# Import active_tasks for direct manipulation in tests
from backend.main import active_tasks
from datetime import datetime, timezone

# Mock datetime globally for consistent timestamps
MOCK_DATETIME = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

@pytest.fixture(autouse=True)
def mock_datetime_utcnow(monkeypatch):
    class MockDatetime(datetime):
        @classmethod
        def utcnow(cls):
            return MOCK_DATETIME
    monkeypatch.setattr('backend.main.datetime', MockDatetime)
    monkeypatch.setattr('backend.models.schemas.datetime', MockDatetime)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "services": {
            "chroma_service": "initialized", # Assuming these are initialized in test env
            "knowledge_nexus_graph": "initialized"
        }
    }

def test_start_research_task_success():
    topic = "test_topic_successful_task"
    # This test might still fail if the underlying services (Chroma, Workflow graph)
    # are not properly mocked or initialized during testing.
    # For now, we focus on the API level contract.
    with patch('backend.main.knowledge_nexus_graph', MagicMock()), \
         patch('backend.main.chroma_service_instance', MagicMock()):
        response = client.post("/research", json={"topic": topic})

    assert response.status_code == 202 # Changed from 503, assuming services are mocked
    response_data = response.json()
    assert "task_id" in response_data
    task_id = response_data["task_id"]
    assert response_data["status"] == "queued"
    assert response_data["message"] == f"Research task for topic '{topic}' has been queued."
    assert response_data["timestamp"] == MOCK_DATETIME.isoformat().replace("+00:00", "Z")


    assert task_id in active_tasks
    assert active_tasks[task_id]["topic"] == topic
    assert active_tasks[task_id]["status"] == "queued"
    # Clean up the task
    if task_id in active_tasks:
        del active_tasks[task_id]

def test_start_research_task_invalid_request():
    response = client.post("/research", json={"not_topic": "some_value"})
    assert response.status_code == 422


@pytest.mark.parametrize(
    "task_status, topic, error_message, expected_message_format",
    [
        ("completed", "cat videos", None, "Research completed for topic: cat videos"),
        ("failed", "dog pictures", "Something broke", "Something broke"),
        ("failed", "bird songs", None, "Research failed for topic: bird songs. No specific error message."),
        ("error_in_workflow", "fish facts", "Workflow errored", "Workflow errored"),
        ("error_in_workflow", "snake myths", None, "Research failed for topic: snake myths. No specific error message."),
        ("running", "hamster wheels", None, "Current status for topic: hamster wheels"),
        ("queued", "gerbil tunnels", None, "Current status for topic: gerbil tunnels"),
        ("awaiting_human_verification", "parrot speech", None, "Current status for topic: parrot speech"),
        ("completed", None, None, "Research completed for topic: N/A"), # Test missing topic
        ("failed", None, "Failure", "Failure"),
        ("failed", None, None, "Research failed for topic: N/A. No specific error message."),
        ("running", None, None, "Current status for topic: N/A"),
    ]
)
def test_get_task_status_message_logic(task_status, topic, error_message, expected_message_format):
    task_id = f"test_status_task_{task_status}_{topic or 'no_topic'}"
    task_data = {
        "task_id": task_id,
        "status": task_status,
        "graph_state": {}, # Needs to exist
    }
    if topic is not None:
        task_data["topic"] = topic
    if error_message is not None:
        task_data["error_message"] = error_message

    active_tasks[task_id] = task_data

    response = client.get(f"/status/{task_id}")
    assert response.status_code == 200
    response_data = response.json()

    assert response_data["task_id"] == task_id
    assert response_data["status"] == task_status
    assert response_data["message"] == expected_message_format
    assert response_data["timestamp"] == MOCK_DATETIME.isoformat().replace("+00:00", "Z")
    assert "progress" in response_data

    del active_tasks[task_id]


def test_get_task_status_not_found():
    non_existent_task_id = "non_existent_task_123"
    response = client.get(f"/status/{non_existent_task_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Task with ID '{non_existent_task_id}' not found."


# For /submit-verification tests
from backend.models.schemas import HumanApproval

def test_submit_verification_success():
    task_id = "test_verification_task_success"
    topic = "topic_for_verification"
    verification_data_id = "data_to_verify_123"
    mock_verification_request = {
        "task_id": task_id, # Ensure task_id is in the request model as per schema
        "data_id": verification_data_id,
        "data_to_verify": {"id": "source1", "content_preview": "preview"}, # Match DataSource
    }

    active_tasks[task_id] = {
        "task_id": task_id,
        "topic": topic,
        "status": "awaiting_human_verification",
        "graph_state": {
            "topic": topic,
            "task_id": task_id,
            "current_verification_request": mock_verification_request,
            "human_in_loop_needed": True,
        },
    }

    approval_input = {
        "task_id": task_id,
        "data_id": verification_data_id,
        "approved": True,
        "notes": "Looks good to me."
    }
    with patch('backend.main.run_research_workflow_async', MagicMock()) as mock_run_workflow:
        response = client.post(f"/submit-verification/{task_id}", json=approval_input)

    assert response.status_code == 200
    assert response.json() == {"message": f"Verification submitted for task '{task_id}'. Workflow is scheduled to resume."}

    assert task_id in active_tasks
    updated_task = active_tasks[task_id]
    assert updated_task["status"] == "resuming_after_verification"
    assert "human_feedback" in updated_task["graph_state"]
    assert updated_task["graph_state"]["human_feedback"]["data_id"] == verification_data_id
    assert updated_task["graph_state"]["human_feedback"]["approved"] is True
    mock_run_workflow.assert_called_once() # Check if background task was triggered

    del active_tasks[task_id]

def test_submit_verification_task_not_found():
    non_existent_task_id = "non_existent_verification_task"
    approval_input = {
        "task_id": non_existent_task_id,
        "data_id": "any_id",
        "approved": True,
        "notes": "Test"
    }
    response = client.post(f"/submit-verification/{non_existent_task_id}", json=approval_input)
    assert response.status_code == 404

def test_submit_verification_task_not_awaiting_verification():
    task_id = "test_verification_task_wrong_state"
    active_tasks[task_id] = {
        "task_id": task_id,
        "topic": "test_topic_wrong_state",
        "status": "queued",
        "graph_state": {"topic": "test_topic_wrong_state", "task_id": task_id},
    }

    approval_input = {
        "task_id": task_id,
        "data_id": "any_id",
        "approved": True,
        "notes": "Test"
    }
    response = client.post(f"/submit-verification/{task_id}", json=approval_input)

    assert response.status_code == 400
    assert response.json()["detail"] == f"Task '{task_id}' is not currently awaiting human verification. Current status: queued."

    del active_tasks[task_id]

def test_get_task_results_completed():
    task_id = "test_results_task_completed"
    document_content = "This is the final research document."
    active_tasks[task_id] = {
        "task_id": task_id,
        "topic": "topic_for_results_completed",
        "status": "completed",
        "final_graph_state": {
            "final_document": document_content
        },
    }

    response = client.get(f"/results/{task_id}")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["task_id"] == task_id
    assert response_data["document_content"] == document_content
    assert response_data["format"] == "markdown"

    del active_tasks[task_id]

def test_get_task_results_not_found():
    non_existent_task_id = "non_existent_results_task"
    response = client.get(f"/results/{non_existent_task_id}")
    assert response.status_code == 404

def test_get_task_results_not_completed():
    task_id = "test_results_task_not_completed"
    active_tasks[task_id] = {
        "task_id": task_id,
        "topic": "topic_for_results_not_completed",
        "status": "running",
        "graph_state": {},
    }

    response = client.get(f"/results/{task_id}")
    assert response.status_code == 202
    assert response.json()["detail"] == f"Task '{task_id}' is not yet completed. Current status: running."
    del active_tasks[task_id]

def test_get_task_results_failed():
    task_id = "test_results_task_failed"
    error_msg = "Something went terribly wrong."
    active_tasks[task_id] = {
        "task_id": task_id,
        "topic": "topic_for_results_failed",
        "status": "failed",
        "error_message": error_msg,
        "graph_state": {},
    }

    response = client.get(f"/results/{task_id}")
    assert response.status_code == 422
    assert response.json()["detail"] == f"Task ended inconclusively. Status: failed. Error: {error_msg}"
    del active_tasks[task_id]


# Test LLM initialization (from original file, kept for completeness)
# This test might require more specific mocking of Langchain components if it were to run in a CI environment
# without actual API keys.
@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skipping LLM initialization test in CI due to API key requirements")
def test_llm_initialization_priority(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("OPENAI_API_VERSION", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT_NAME", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test_azure_key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.azure.com")
    monkeypatch.setenv("OPENAI_API_VERSION", "test_version")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT_NAME", "test_deployment")

    with mock.patch('langchain_openai.AzureChatOpenAI', autospec=True) as mock_azure_chat_openai, \
         mock.patch('langchain_openai.ChatOpenAI', autospec=True) as mock_chat_openai:

        mock_azure_chat_openai.return_value = MagicMock(spec=AzureChatOpenAI)
        workflow_app_azure = build_knowledge_nexus_workflow(chroma_service=None)

        mock_azure_chat_openai.assert_called_once_with(
            azure_endpoint="https://test.azure.com",
            api_key="test_azure_key",
            api_version="test_version",
            azure_deployment="test_deployment",
            temperature=0.2
        )
        assert workflow_app_azure.nodes['synthesize'].func.keywords.get('llm') == mock_azure_chat_openai.return_value
        mock_chat_openai.assert_not_called()

    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("OPENAI_API_VERSION", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT_NAME", raising=False)

    with mock.patch('langchain_openai.AzureChatOpenAI', autospec=True) as mock_azure_chat_openai_none, \
         mock.patch('langchain_openai.ChatOpenAI', autospec=True) as mock_chat_openai_none:

        workflow_app_none = build_knowledge_nexus_workflow(chroma_service=None)
        mock_azure_chat_openai_none.assert_not_called()
        mock_chat_openai_none.assert_not_called()
        assert workflow_app_none.nodes['synthesize'].func.keywords.get('llm') is None

# Ensure active_tasks is cleaned up after each test function that uses it
@pytest.fixture(autouse=True)
def cleanup_active_tasks():
    yield # Test runs here
    # Teardown: clear active_tasks
    # This is a bit aggressive but ensures no leakage between tests if tasks are not deleted
    # For more targeted cleanup, individual tests should delete the tasks they create.
    # However, given the direct modification of active_tasks, a global cleanup might be safer.
    # Example: active_tasks.clear() # -> This might be too broad if some tests expect tasks to persist across calls.
    # Better to rely on explicit deletion within tests, as done in most tests above.
    # If a test ID is missed, it could affect other tests.
    # The current approach is to delete specific task_ids within each test.
    pass
