import os
from typing import Optional, Tuple

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import AzureChatOpenAI, ChatOpenAI

# Load environment variables from .env file
# Assuming .env is in the backend directory, adjust path if necessary
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Placeholder strings to check against
AZURE_PLACEHOLDERS = ["YOUR_AZURE_OPENAI_API_KEY", "YOUR_AZURE_OPENAI_ENDPOINT", "YOUR_AZURE_OPENAI_DEPLOYMENT_NAME"]
OPENAI_PLACEHOLDER = "YOUR_OPENAI_API_KEY"
COMMON_OPENAI_PLACEHOLDER = "YOUR_ACTUAL_OPENAI_API_KEY_REPLACE_ME"

class LLMService:
    """
    Service for initializing and interacting with Language Models (LLMs).
    Supports Azure OpenAI and standard OpenAI models.
    """
    def __init__(self, temperature: float = 0.2, model_name: str = "gpt-3.5-turbo"):
        """
        Initializes the LLMService, which identifies and prepares an LLM instance.

        Args:
            temperature (float): The temperature setting for the LLM.
            model_name (str): The model name to use for standard OpenAI.
        """
        self.llm: Optional[BaseChatModel] = None
        self.llm_type: Optional[str] = None  # 'azure', 'openai', or None
        self.initialization_error: Optional[str] = None
        self._initialize_llm(temperature, model_name)

    def _initialize_llm(self, temperature: float, model_name: str) -> None:
        """
        Determines the LLM provider (Azure or OpenAI) based on environment variables
        and initializes the LLM instance.
        """
        azure_vars_present = AZURE_OPENAI_API_KEY is not None and AZURE_OPENAI_ENDPOINT is not None

        if azure_vars_present:
            print("LLMService: Azure environment variables detected. Attempting Azure OpenAI.")
            azure_config_complete = (
                AZURE_OPENAI_API_KEY and AZURE_OPENAI_API_KEY not in AZURE_PLACEHOLDERS and
                AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_ENDPOINT not in AZURE_PLACEHOLDERS and
                OPENAI_API_VERSION and
                AZURE_OPENAI_DEPLOYMENT_NAME and AZURE_OPENAI_DEPLOYMENT_NAME not in AZURE_PLACEHOLDERS
            )
            if azure_config_complete:
                try:
                    self.llm = AzureChatOpenAI(
                        azure_endpoint=AZURE_OPENAI_ENDPOINT,
                        api_key=AZURE_OPENAI_API_KEY,
                        api_version=OPENAI_API_VERSION,
                        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
                        temperature=temperature,
                    )
                    self.llm_type = "azure"
                    print("LLMService: AzureChatOpenAI LLM initialized successfully.")
                except Exception as e:
                    self.initialization_error = f"Error initializing AzureChatOpenAI: {e}"
                    print(f"LLMService: {self.initialization_error}")
            else:
                self.initialization_error = "Azure OpenAI environment variables are present but incomplete or contain placeholders."
                print(f"LLMService: {self.initialization_error}")

        if self.llm is None and not azure_vars_present: # Only try OpenAI if Azure was not attempted or failed AND Azure vars were not present
            print("LLMService: Azure environment variables not detected or Azure init failed and no Azure vars present. Attempting standard OpenAI.")
            if OPENAI_API_KEY and OPENAI_API_KEY != OPENAI_PLACEHOLDER and OPENAI_API_KEY != COMMON_OPENAI_PLACEHOLDER:
                try:
                    self.llm = ChatOpenAI(
                        api_key=OPENAI_API_KEY,
                        model_name=model_name,
                        temperature=temperature
                    )
                    self.llm_type = "openai"
                    print("LLMService: ChatOpenAI LLM initialized successfully.")
                except Exception as e_std:
                    self.initialization_error = f"Error initializing standard ChatOpenAI: {e_std}"
                    print(f"LLMService: {self.initialization_error}")
            else:
                self.initialization_error = "Standard OPENAI_API_KEY not found or is a placeholder."
                print(f"LLMService: {self.initialization_error}")

        if self.llm:
            print(f"LLMService: LLM initialization successful ({self.llm_type}).")
        else:
            final_error_message = "CRITICAL WARNING: No LLM was initialized. "
            if self.initialization_error:
                final_error_message += self.initialization_error
            else:
                final_error_message += "Unknown configuration error."
            print(f"LLMService: {final_error_message} The system may need to use simulated data or skip LLM-dependent tasks.")


    def invoke(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Invokes the initialized LLM with the given prompt.

        Args:
            prompt (str): The prompt to send to the LLM.

        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing the LLM's response content (or None if an error occurred) and an error message (or None if successful).
        """
        if not self.llm:
            error_msg = "LLM not initialized. Cannot invoke."
            print(f"LLMService: {error_msg}")
            return None, error_msg

        try:
            print(f"LLMService: Invoking {self.llm_type} LLM...")
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            return content, None
        except Exception as e:
            error_msg = f"Error during LLM invocation: {e}"
            print(f"LLMService: {error_msg}")
            return None, error_msg

    def is_initialized(self) -> bool:
        """Checks if the LLM was successfully initialized."""
        return self.llm is not None

# Example usage (for testing this module directly)
if __name__ == '__main__':
    print("Testing LLMService...")
    llm_service = LLMService()

    if llm_service.is_initialized():
        print(f"LLM Type: {llm_service.llm_type}")
        test_prompt = "Hello, LLM! Tell me a fun fact about Python programming."
        content, error = llm_service.invoke(test_prompt)
        if error:
            print(f"Test Invocation Error: {error}")
        else:
            print(f"Test Invocation Response: {content}")
    else:
        print(f"LLM could not be initialized. Error: {llm_service.initialization_error}")

    # Test with missing Azure keys but present OpenAI key (requires setting up .env accordingly)
    # print("
To test specific fallback scenarios, modify your .env file and re-run.")
