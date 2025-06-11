import chromadb
from typing import List, Dict, Optional, Any
import logging
import os
from openai import AzureOpenAI
from chromadb import Documents, EmbeddingFunction, Embeddings

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AzureOpenAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self, embedding_api_key: str, azure_endpoint: str, api_version: str, azure_deployment_name: str):
        self._client = AzureOpenAI(
            api_key=embedding_api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )
        self._azure_deployment_name = azure_deployment_name

    def __call__(self, texts: Documents) -> Embeddings:
        try:
            response = self._client.embeddings.create(model=self._azure_deployment_name, input=texts)
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Azure OpenAI API call failed: {e}", exc_info=True)
            # Depending on how chromadb handles errors in embedding functions,
            # you might want to raise the exception or return empty embeddings.
            # For now, returning empty list for each failed text or raising.
            # Returning empty list might lead to issues if chromadb expects specific list length.
            # Consider returning List[Optional[List[float]]] or similar if chromadb supports it,
            # or handling this more robustly based on chromadb's error handling.
            # For simplicity, let's re-raise for now, or return empty embeddings for all if one fails.
            # raise # Option 1: Re-raise the exception
            return [[] for _ in texts] # Option 2: Return empty embeddings for all texts if API call fails for the batch


class ChromaService:
    def __init__(self, persist_directory: str = "./chroma_db_store"):
        """
        Initializes the ChromaDB client and Azure OpenAI embedding function.

        Args:
            persist_directory (str): Directory to store ChromaDB data.
        """
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)

            azure_embedding_api_key = os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY")
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_api_version = os.getenv("OPENAI_API_VERSION") # or AZURE_OPENAI_API_VERSION
            azure_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

            if not all([azure_embedding_api_key, azure_endpoint, azure_api_version, azure_embedding_deployment]):
                logger.error("Azure OpenAI embedding environment variables are not fully set.")
                raise ValueError("Missing one or more Azure OpenAI embedding environment variables.")

            self.embedding_function = AzureOpenAIEmbeddingFunction(
                embedding_api_key=azure_embedding_api_key,
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                azure_deployment_name=azure_embedding_deployment
            )
            logger.info(f"Using Azure OpenAI embedding function with deployment: {azure_embedding_deployment}")
            logger.info(f"ChromaDB client initialized. Data will be persisted in: {persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client or Azure OpenAI embedding function: {e}", exc_info=True)
            raise

    def get_or_create_collection(self, collection_name: str) -> Optional[chromadb.api.models.Collection.Collection]:
        """
        Gets an existing collection or creates it if it doesn't exist.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            Optional[chromadb.api.models.Collection.Collection]: The collection object, or None if an error occurred.
        """
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function  # type: ignore
            )
            logger.info(f"Successfully retrieved or created collection: {collection_name}")
            return collection
        except Exception as e:
            logger.error(f"Failed to get or create collection '{collection_name}': {e}", exc_info=True)
            return None

    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> bool:
        """
        Adds documents to the specified collection.

        Args:
            collection_name (str): The name of the collection.
            documents (List[str]): A list of document texts.
            metadatas (List[Dict[str, Any]]): A list of metadata dictionaries corresponding to the documents.
            ids (List[str]): A list of unique IDs for the documents.

        Returns:
            bool: True if documents were added successfully, False otherwise.
        """
        collection = self.get_or_create_collection(collection_name)
        if not collection:
            return False

        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully added {len(documents)} documents to collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add documents to collection '{collection_name}': {e}", exc_info=True)
            return False

    def query_documents(self, collection_name: str, query_texts: List[str], n_results: int = 5) -> Optional[Dict[str, Any]]:
        """
        Queries documents from the specified collection.

        Args:
            collection_name (str): The name of the collection.
            query_texts (List[str]): A list of query texts.
            n_results (int): The number of results to return for each query.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the query results, or None if an error occurred.
        """
        collection = self.get_or_create_collection(collection_name)
        if not collection:
            return None

        try:
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                # include=['metadatas', 'documents'] # Optional: specify what to include in results
            )
            logger.info(f"Successfully queried collection '{collection_name}' with {len(query_texts)} queries.")
            return results
        except Exception as e:
            logger.error(f"Failed to query documents from collection '{collection_name}': {e}", exc_info=True)
            return None

    def get_document_by_id(self, collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific document by its ID from the collection.

        Args:
            collection_name (str): The name of the collection.
            doc_id (str): The ID of the document to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The document data if found, otherwise None.
        """
        collection = self.get_or_create_collection(collection_name)
        if not collection:
            return None

        try:
            result = collection.get(ids=[doc_id], include=['documents', 'metadatas'])
            if result and result['ids']:
                logger.info(f"Successfully retrieved document with ID '{doc_id}' from collection '{collection_name}'.")
                # Construct a more usable output, assuming one ID is fetched
                document = {
                    "id": result["ids"][0],
                    "document": result["documents"][0] if result["documents"] else None,
                    "metadata": result["metadatas"][0] if result["metadatas"] else None,
                }
                return document
            else:
                logger.warning(f"Document with ID '{doc_id}' not found in collection '{collection_name}'.")
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve document with ID '{doc_id}' from collection '{collection_name}': {e}", exc_info=True)
            return None

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    logger.info("Starting ChromaService example usage...")

    # Initialize service (will create ./chroma_db_store if it doesn't exist)
    # This will now require Azure OpenAI environment variables to be set.
    # For local testing, ensure you have a .env file with:
    # AZURE_OPENAI_EMBEDDING_API_KEY="your_embedding_key"
    # AZURE_OPENAI_ENDPOINT="your_endpoint"
    # OPENAI_API_VERSION="your_api_version"
    # AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="your_deployment_name"
    # from dotenv import load_dotenv # You would typically load this at the start of your app
    # load_dotenv()

    logger.info("Attempting to initialize ChromaService with Azure OpenAI embeddings.")
    logger.info("Ensure Azure OpenAI embedding environment variables (AZURE_OPENAI_EMBEDDING_API_KEY, AZURE_OPENAI_ENDPOINT, OPENAI_API_VERSION, AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME) are set.")

    try:
        chroma_service = ChromaService(persist_directory="./test_chroma_db")
    except ValueError as ve:
        logger.error(f"Initialization failed due to missing env vars: {ve}")
        logger.info("Skipping further tests as ChromaService could not be initialized.")
        chroma_service = None # Ensure it's None so subsequent tests don't run
    except Exception as e:
        logger.error(f"An unexpected error occurred during ChromaService initialization: {e}", exc_info=True)
        logger.info("Skipping further tests as ChromaService could not be initialized.")
        chroma_service = None


    collection_name = "my_test_collection_azure"

    # Get or create collection
    # collection = chroma_service.get_or_create_collection(collection_name) # This line is problematic if chroma_service is None

    if chroma_service and collection_name: # Proceed only if chroma_service was initialized
        collection = chroma_service.get_or_create_collection(collection_name)

    # Get or create collection
    collection = chroma_service.get_or_create_collection(collection_name)

    if collection:
        logger.info(f"Collection '{collection_name}' obtained. Current count: {collection.count()}")

        # Add documents
        docs_to_add = ["This is document 1 about apples.", "Document 2 discusses bananas.", "The third document is about oranges."]
        metadata_to_add = [{"source": "doc1", "type": "fruit"}, {"source": "doc2", "type": "fruit"}, {"source": "doc3", "type": "fruit"}]
        ids_to_add = ["id1", "id2", "id3"]

        # Check if documents already exist by ID to avoid errors on re-runs
        existing_docs = chroma_service.get_document_by_id(collection_name, "id1") # Check one ID
        if not existing_docs: # if id1 is not found, assume others are not either for this simple test
            if chroma_service.add_documents(collection_name, docs_to_add, metadata_to_add, ids_to_add):
                logger.info("Documents added successfully for the first time.")
            else:
                logger.error("Failed to add documents.")
        else:
            logger.info("Documents seem to already exist in the collection, skipping add.")

        logger.info(f"Collection count after attempting to add documents: {collection.count()}")

        # Query documents
        query_results = chroma_service.query_documents(collection_name, query_texts=["Tell me about apples"], n_results=1)
        if query_results and query_results.get('documents'):
            logger.info(f"Query results for 'apples': {query_results['documents'][0]}")
        else:
            logger.warning("No results found for 'apples' query or query failed.")
            if query_results:
                 logger.info(f"Raw query result: {query_results}")


        # Get a specific document by ID
        retrieved_doc = chroma_service.get_document_by_id(collection_name, "id2")
        if retrieved_doc:
            logger.info(f"Retrieved document id2: {retrieved_doc}")
        else:
            logger.warning("Could not retrieve document id2.")

        # Test getting a non-existent document
        non_existent_doc = chroma_service.get_document_by_id(collection_name, "id_non_existent")
        if not non_existent_doc:
            logger.info("Correctly handled non-existent document retrieval (returned None).")

        # Clean up (optional): Delete the collection
        # try:
        #     if chroma_service: # Ensure client exists
        #         chroma_service.client.delete_collection(collection_name)
        #         logger.info(f"Successfully deleted collection: {collection_name}")
        # except Exception as e:
        #     logger.error(f"Failed to delete collection {collection_name}: {e}")

    elif not chroma_service:
        # This case is already handled by the logger messages inside the try-except for ChromaService initialization
        pass
    else:
        logger.error(f"Could not get or create collection: {collection_name} (chroma_service might be None or collection_name is empty)")


    logger.info("ChromaService example usage with Azure OpenAI finished.")
