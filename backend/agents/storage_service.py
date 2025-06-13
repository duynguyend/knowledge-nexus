from typing import List, Dict, Any, Optional, Tuple

# Attempt to import ChromaService from the expected location
try:
    from ..services.chroma_service import ChromaService
except ImportError:
    print("StorageService: Could not perform relative import for ChromaService. Using dummy class for StorageService.")
    # Define a dummy ChromaService if the real one cannot be imported
    # This allows StorageService to be defined and tested independently to some extent
    class ChromaService: # type: ignore
        def __init__(self, persist_directory: Optional[str] = None):
            self.persist_directory = persist_directory
            print(f"Dummy ChromaService initialized (persist_directory: {persist_directory}).")

        def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> bool:
            print(f"Dummy ChromaService: Add {len(documents)} documents to collection '{collection_name}'.")
            # Simulate success
            return True

        def get_collection(self, collection_name: str):
            print(f"Dummy ChromaService: Get collection '{collection_name}'.")
            # Simulate a collection object with a count method for basic compatibility
            class DummyCollection:
                def count(self):
                    return 0 # Simulate empty collection
            return DummyCollection()

        def delete_collection(self, collection_name: str):
            print(f"Dummy ChromaService: Delete collection '{collection_name}'.")
            # Simulate success
            return True


class StorageService:
    """
    Service for interacting with a vector database (ChromaDB).
    Manages storing and retrieving research data.
    """
    def __init__(self, persist_directory: Optional[str] = "./chroma_db_store_service"):
        """
        Initializes the StorageService with a ChromaService instance.

        Args:
            persist_directory (Optional[str]): The directory for ChromaDB to persist data.
                                               Defaults to "./chroma_db_store_service".
        """
        self.chroma_service: Optional[ChromaService] = None
        self.initialization_error: Optional[str] = None
        try:
            # Adjust the import path based on your actual project structure
            # If this script is in backend/agents/ and chroma_service.py is in backend/services/
            # then the relative import `from ..services.chroma_service import ChromaService` is correct
            # when this module is imported as part of the package.
            # If running this script directly, Python might struggle with relative imports.
            # The try-except block for ChromaService definition is a workaround for direct execution/testing.
            global ChromaService
            if 'ChromaService' not in globals() or globals()['ChromaService'].__module__ == __name__:
                 # This checks if ChromaService is the dummy one defined above
                 # Re-attempt import if running in a context where it might be found
                 from ..services.chroma_service import ChromaService as RealChromaService
                 self.chroma_service = RealChromaService(persist_directory=persist_directory)
            else:
                 # ChromaService was already imported (likely the real one by a higher-level module)
                 # or it's the dummy if the import above failed and we are in the except block of the initial try-import
                 self.chroma_service = ChromaService(persist_directory=persist_directory)

            print(f"StorageService: ChromaService initialized successfully (persist_directory: {persist_directory}).")
        except ImportError as e_imp:
             # This will catch if `from ..services.chroma_service import ChromaService as RealChromaService` fails
             # and ChromaService is still the dummy.
            if 'ChromaService' in globals() and globals()['ChromaService'].__module__ == __name__:
                print(f"StorageService: Failed to import real ChromaService ({e_imp}). Using dummy ChromaService as fallback.")
                self.chroma_service = ChromaService(persist_directory=persist_directory) # Ensure it's the dummy
            else:
                # Some other import error or ChromaService wasn't even the dummy (should not happen)
                self.initialization_error = f"Failed to initialize ChromaService due to import error: {e_imp}"
                print(f"StorageService Error: {self.initialization_error}")

        except Exception as e:
            self.initialization_error = f"Failed to initialize ChromaService: {str(e)}"
            print(f"StorageService Error: {self.initialization_error}")
            # self.chroma_service might be None or the dummy depending on where the exception occurred.

    def is_initialized(self) -> bool:
        """Checks if the underlying ChromaService was successfully initialized."""
        return self.chroma_service is not None and self.initialization_error is None

    def add_research_data(self, task_id: str, research_items: List[Dict[str, Any]], topic: str) -> Tuple[bool, Optional[str]]:
        """
        Adds processed research data to storage.

        Args:
            task_id (str): The unique ID for the research task, used as the collection name.
            research_items (List[Dict[str, Any]]): A list of research items (dictionaries).
                                                   Each item should have 'id', 'snippet', 'url', 'title'.
            topic (str): The research topic.

        Returns:
            Tuple[bool, Optional[str]]: A boolean indicating success, and an optional error message.
        """
        if not self.is_initialized() or self.chroma_service is None:
            return False, self.initialization_error or "ChromaService not available."

        if not research_items:
            return True, "No research items to add."

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []

        for item in research_items:
            if item.get('snippet'):
                documents.append(item['snippet'])
                metadatas.append({
                    "source_url": item.get('url', ''),
                    "title": item.get('title', ''),
                    "research_topic": topic,
                    "original_id_from_source": item.get('id')
                })
                ids.append(item['id'])

        if not documents:
            return True, "No valid documents extracted from research items to add to ChromaDB."

        collection_name = task_id
        try:
            print(f"StorageService: Attempting to add {len(documents)} documents to ChromaDB collection: {collection_name}")
            added_successfully = self.chroma_service.add_documents(
                collection_name=collection_name,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            if added_successfully:
                print(f"StorageService: Added {len(documents)} documents to ChromaDB for task '{task_id}'.")
                return True, None
            else:
                error_msg = f"Failed to add documents to ChromaDB for task '{task_id}' (reason unknown from ChromaService)."
                print(f"StorageService: {error_msg}")
                return False, error_msg
        except Exception as e:
            error_msg = f"Error interacting with ChromaDB during add: {e}"
            print(f"StorageService: {error_msg}")
            return False, error_msg

    def get_collection_item_count(self, task_id: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Gets the number of items in a specific collection (task).

        Args:
            task_id (str): The unique ID for the research task (collection name).

        Returns:
            Tuple[Optional[int], Optional[str]]: Number of items or None, and an optional error message.
        """
        if not self.is_initialized() or self.chroma_service is None:
            return None, self.initialization_error or "ChromaService not available."

        try:
            collection = self.chroma_service.get_collection(collection_name=task_id)
            if collection:
                return collection.count(), None
            else:
                return 0, f"Collection '{task_id}' not found or could not be retrieved."
        except Exception as e:
            error_msg = f"Error getting collection count for '{task_id}': {e}"
            print(f"StorageService: {error_msg}")
            return None, error_msg

    def clear_storage_for_task(self, task_id: str) -> Tuple[bool, Optional[str]]:
        """
        Deletes the collection associated with a task_id.

        Args:
            task_id (str): The unique ID for the research task (collection name).

        Returns:
            Tuple[bool, Optional[str]]: True if deletion was successful or collection didn't exist,
                                       False if an error occurred, and an optional error message.
        """
        if not self.is_initialized() or self.chroma_service is None:
            return False, self.initialization_error or "ChromaService not available."

        try:
            print(f"StorageService: Attempting to delete collection '{task_id}' for cleanup.")
            self.chroma_service.delete_collection(collection_name=task_id)
            print(f"StorageService: Collection '{task_id}' deleted or did not exist.")
            return True, None
        except Exception as e:
            error_msg = f"Error deleting collection '{task_id}': {e}"
            print(f"StorageService: {error_msg}")
            return False, error_msg


# Example usage (for testing this module directly)
if __name__ == '__main__':
    print("Testing StorageService...")
    test_persist_dir = "./test_chroma_db_storage_service"
    storage_service = StorageService(persist_directory=test_persist_dir)

    if storage_service.is_initialized():
        test_task_id = "test_task_001"

        print(f"\nAttempting pre-test cleanup for task: {test_task_id}")
        cleaned, error_clean = storage_service.clear_storage_for_task(test_task_id)
        if error_clean:
            print(f"Pre-test cleanup error: {error_clean}")

        print(f"\nInitial item count for task '{test_task_id}':")
        count, error = storage_service.get_collection_item_count(test_task_id)
        if error:
            print(f"Error getting count: {error}")
        else:
            print(f"Count: {count}")

        print(f"\nAdding mock research data for task '{test_task_id}'...")
        mock_data = [
            {"id": "doc1", "snippet": "Content for document 1", "url": "http://example.com/doc1", "title": "Document 1"},
            {"id": "doc2", "snippet": "Content for document 2", "url": "http://example.com/doc2", "title": "Document 2"},
            {"id": "doc3", "snippet": "", "url": "http://example.com/doc3", "title": "Document 3 - Empty Snippet"}
        ]
        success, error = storage_service.add_research_data(test_task_id, mock_data, "Test Topic")
        if error:
            print(f"Error adding data: {error}")
        elif success:
            print("Data added successfully.")

        print(f"\nItem count after adding for task '{test_task_id}':")
        count, error = storage_service.get_collection_item_count(test_task_id)
        if error:
            print(f"Error getting count: {error}")
        else:
            print(f"Count: {count}")

        print(f"\nAdding no research data for task '{test_task_id}':")
        success, error = storage_service.add_research_data(test_task_id, [], "Test Topic Empty")
        if error:
            print(f"Error adding empty data: {error}")
        elif success:
            print("Adding empty data handled correctly (no error, success=True).")


        print(f"\nAttempting post-test cleanup for task: {test_task_id}")
        cleaned, error_clean = storage_service.clear_storage_for_task(test_task_id)
        if error_clean:
            print(f"Post-test cleanup error: {error_clean}")
        else:
            if cleaned:
                 print(f"Collection '{test_task_id}' cleaned up successfully.")
    else:
        print(f"StorageService could not be initialized. Error: {storage_service.initialization_error}")

    print("\nNote: If the real ChromaService from ..services.chroma_service cannot be imported, a dummy version is used.")
    print("For full testing with actual ChromaDB, ensure the main application structure allows the relative import.")
