import unittest
import os
from unittest.mock import patch, MagicMock

# Attempt to import the target function and LLM classes
# This structure assumes 'backend' is discoverable in PYTHONPATH,
# which might require adjustment if running tests from a different context.
try:
    from backend.agents.research_workflow import build_knowledge_nexus_workflow
    # LLM Classes are imported here for context, but patching happens where they are looked up.
    from langchain_openai import AzureChatOpenAI, ChatOpenAI
except ImportError as e:
    # Fallback for simpler local test execution (e.g., if backend/ is current dir)
    # This assumes that if the test is run from `python -m unittest discover backend/tests`
    # and the project root is in sys.path, the above should work.
    # This fallback might be needed if running the test file directly.
    print(f"Initial import attempt failed: {e}. Adjusting path for potential local execution.")
    import sys
    from pathlib import Path
    # Assuming this test file is in backend/tests/
    # project_root should be two levels up from this file's directory
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"Added {project_root} to sys.path for test execution.")

    # Retry imports
    try:
        from backend.agents.research_workflow import build_knowledge_nexus_workflow
        from langchain_openai import AzureChatOpenAI, ChatOpenAI
    except ImportError as final_e:
        print(f"CRITICAL: Could not import 'build_knowledge_nexus_workflow' or LLM classes after path adjustment: {final_e}")
        # Define dummies if imports fail, so tests can at least be discovered
        def build_knowledge_nexus_workflow(chroma_service=None): return (None, False)
        class AzureChatOpenAI: pass
        class ChatOpenAI: pass


# Define placeholder values (should match those in research_workflow.py)
AZURE_PLACEHOLDERS = ["YOUR_AZURE_OPENAI_API_KEY", "YOUR_AZURE_OPENAI_ENDPOINT", "YOUR_AZURE_OPENAI_DEPLOYMENT_NAME"]
OPENAI_PLACEHOLDER = "YOUR_OPENAI_API_KEY"

# Patching target for LLM classes is where they are imported and used in research_workflow.py
PATCH_TARGET_AZURE = 'backend.agents.research_workflow.AzureChatOpenAI'
PATCH_TARGET_OPENAI = 'backend.agents.research_workflow.ChatOpenAI'

class TestLLMInitialization(unittest.TestCase):

    # Helper to set up environment variables for a test
    def set_env_vars(self, env_vars_dict):
        # `patch.dict` is context-managed, so changes are reverted after the 'with' block.
        # However, for individual tests, we often apply it as a decorator or directly.
        # Here, we'll store the original state and restore it in tearDown if needed,
        # but `patch.dict` within each test is cleaner.
        self.original_environ = os.environ.copy()
        os.environ.update(env_vars_dict)

    def tearDown(self):
        # Restore original environment variables if `set_env_vars` was used in a way that needs manual cleanup.
        # Using `patch.dict` as a context manager or decorator handles this automatically.
        if hasattr(self, 'original_environ'):
            os.environ.clear()
            os.environ.update(self.original_environ)

    @patch(PATCH_TARGET_OPENAI)
    @patch(PATCH_TARGET_AZURE)
    def test_azure_openai_success(self, MockAzureChatOpenAI, MockChatOpenAI):
        """Azure succeeds, OpenAI fallback should not be called."""
        mock_azure_instance = MagicMock(spec=AzureChatOpenAI)
        MockAzureChatOpenAI.return_value = mock_azure_instance

        env_vars = {
            "AZURE_OPENAI_API_KEY": "valid_azure_key",
            "AZURE_OPENAI_ENDPOINT": "valid_azure_endpoint",
            "OPENAI_API_VERSION": "valid_api_version",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "valid_deployment_name",
            "OPENAI_API_KEY": OPENAI_PLACEHOLDER # Ensure OpenAI fallback is not viable
        }
        with patch.dict(os.environ, env_vars, clear=True):
            _, llm_initialized = build_knowledge_nexus_workflow(chroma_service=None)

        MockAzureChatOpenAI.assert_called_once()
        MockChatOpenAI.assert_not_called()
        self.assertTrue(llm_initialized, "LLM should be initialized with Azure.")

    @patch(PATCH_TARGET_OPENAI)
    @patch(PATCH_TARGET_AZURE)
    def test_standard_openai_success_as_fallback_due_to_incomplete_azure(self, MockAzureChatOpenAI, MockChatOpenAI):
        """Azure config is incomplete, standard OpenAI should be used."""
        mock_openai_instance = MagicMock(spec=ChatOpenAI)
        MockChatOpenAI.return_value = mock_openai_instance

        env_vars = {
            "AZURE_OPENAI_API_KEY": "valid_azure_key",
            # AZURE_OPENAI_ENDPOINT is missing
            "OPENAI_API_VERSION": "valid_api_version",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "valid_deployment_name",
            "OPENAI_API_KEY": "valid_openai_key"
        }
        with patch.dict(os.environ, env_vars, clear=True):
            _, llm_initialized = build_knowledge_nexus_workflow(chroma_service=None)

        # AzureChatOpenAI might not be called if pre-checks fail, or it might be called and fail internally
        # The key is that ChatOpenAI is called as a fallback.
        MockChatOpenAI.assert_called_once()
        self.assertTrue(llm_initialized, "LLM should be initialized with standard OpenAI as fallback.")

    @patch(PATCH_TARGET_OPENAI)
    @patch(PATCH_TARGET_AZURE)
    def test_standard_openai_success_azure_not_configured(self, MockAzureChatOpenAI, MockChatOpenAI):
        """Azure is not configured (placeholders/missing), standard OpenAI should be used."""
        mock_openai_instance = MagicMock(spec=ChatOpenAI)
        MockChatOpenAI.return_value = mock_openai_instance

        env_vars = {
            "AZURE_OPENAI_API_KEY": AZURE_PLACEHOLDERS[0],
            "AZURE_OPENAI_ENDPOINT": AZURE_PLACEHOLDERS[1],
            "OPENAI_API_VERSION": "valid_api_version", # Version might be present
            "AZURE_OPENAI_DEPLOYMENT_NAME": AZURE_PLACEHOLDERS[2],
            "OPENAI_API_KEY": "valid_openai_key"
        }
        with patch.dict(os.environ, env_vars, clear=True):
            _, llm_initialized = build_knowledge_nexus_workflow(chroma_service=None)

        MockAzureChatOpenAI.assert_not_called() # Or assert it wasn't successfully initialized if pre-checks are loose
        MockChatOpenAI.assert_called_once()
        self.assertTrue(llm_initialized, "LLM should be initialized with standard OpenAI.")

    @patch(PATCH_TARGET_OPENAI)
    @patch(PATCH_TARGET_AZURE)
    def test_azure_preferred_when_both_configured(self, MockAzureChatOpenAI, MockChatOpenAI):
        """Azure should be preferred if both Azure and standard OpenAI are validly configured."""
        mock_azure_instance = MagicMock(spec=AzureChatOpenAI)
        MockAzureChatOpenAI.return_value = mock_azure_instance

        env_vars = {
            "AZURE_OPENAI_API_KEY": "valid_azure_key",
            "AZURE_OPENAI_ENDPOINT": "valid_azure_endpoint",
            "OPENAI_API_VERSION": "valid_api_version",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "valid_deployment_name",
            "OPENAI_API_KEY": "valid_openai_key" # Standard OpenAI also configured
        }
        with patch.dict(os.environ, env_vars, clear=True):
            _, llm_initialized = build_knowledge_nexus_workflow(chroma_service=None)

        MockAzureChatOpenAI.assert_called_once()
        MockChatOpenAI.assert_not_called()
        self.assertTrue(llm_initialized, "LLM should be initialized with Azure (preferred).")

    @patch(PATCH_TARGET_OPENAI)
    @patch(PATCH_TARGET_AZURE)
    def test_no_llm_initialized_all_missing_or_placeholders(self, MockAzureChatOpenAI, MockChatOpenAI):
        """Neither Azure nor standard OpenAI configured, no LLM should initialize."""
        env_vars = {
            "AZURE_OPENAI_API_KEY": AZURE_PLACEHOLDERS[0],
            "AZURE_OPENAI_ENDPOINT": "", # Empty string
            "OPENAI_API_VERSION": "valid_api_version",
            "AZURE_OPENAI_DEPLOYMENT_NAME": AZURE_PLACEHOLDERS[2],
            "OPENAI_API_KEY": OPENAI_PLACEHOLDER
        }
        with patch.dict(os.environ, env_vars, clear=True):
            _, llm_initialized = build_knowledge_nexus_workflow(chroma_service=None)

        MockAzureChatOpenAI.assert_not_called()
        MockChatOpenAI.assert_not_called()
        self.assertFalse(llm_initialized, "No LLM should be initialized.")

    @patch(PATCH_TARGET_OPENAI)
    @patch(PATCH_TARGET_AZURE)
    def test_no_llm_initialized_azure_fails_openai_missing(self, MockAzureChatOpenAI, MockChatOpenAI):
        """Azure is configured but fails to init, and standard OpenAI is not configured."""
        MockAzureChatOpenAI.side_effect = Exception("Azure Initialization Failed")

        env_vars = {
            "AZURE_OPENAI_API_KEY": "valid_azure_key",
            "AZURE_OPENAI_ENDPOINT": "valid_azure_endpoint",
            "OPENAI_API_VERSION": "valid_api_version",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "valid_deployment_name",
            "OPENAI_API_KEY": OPENAI_PLACEHOLDER # OpenAI not configured
        }
        with patch.dict(os.environ, env_vars, clear=True):
            _, llm_initialized = build_knowledge_nexus_workflow(chroma_service=None)

        MockAzureChatOpenAI.assert_called_once() # Azure was attempted
        MockChatOpenAI.assert_not_called()
        self.assertFalse(llm_initialized, "No LLM should be initialized if Azure fails and OpenAI is missing.")

    @patch(PATCH_TARGET_OPENAI)
    @patch(PATCH_TARGET_AZURE)
    def test_fallback_when_azure_fails_openai_succeeds(self, MockAzureChatOpenAI, MockChatOpenAI):
        """Azure is configured but fails, standard OpenAI is configured and should be used."""
        MockAzureChatOpenAI.side_effect = Exception("Azure Initialization Failed")
        mock_openai_instance = MagicMock(spec=ChatOpenAI)
        MockChatOpenAI.return_value = mock_openai_instance

        env_vars = {
            "AZURE_OPENAI_API_KEY": "valid_azure_key",
            "AZURE_OPENAI_ENDPOINT": "valid_azure_endpoint",
            "OPENAI_API_VERSION": "valid_api_version",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "valid_deployment_name",
            "OPENAI_API_KEY": "valid_openai_key" # OpenAI is configured
        }
        with patch.dict(os.environ, env_vars, clear=True):
            _, llm_initialized = build_knowledge_nexus_workflow(chroma_service=None)

        MockAzureChatOpenAI.assert_called_once() # Azure was attempted
        MockChatOpenAI.assert_called_once()     # OpenAI was called as fallback
        self.assertTrue(llm_initialized, "LLM should be initialized with standard OpenAI after Azure failure.")

if __name__ == '__main__':
    # This allows running the tests directly from this file,
    # though `python -m unittest discover` is generally preferred.
    unittest.main()
