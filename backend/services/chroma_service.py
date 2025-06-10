import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional, Any
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChromaService:
    def __init__(self, persist_directory: str = "./chroma_db_store", embedding_model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the ChromaDB client and embedding function.

        Args:
            persist_directory (str): Directory to store ChromaDB data.
            embedding_model_name (str): Name of the SentenceTransformer model to use.
                                        Defaults to 'all-MiniLM-L6-v2'.
                                        Set to None to use ChromaDB's default embedding function.
        """
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            if embedding_model_name:
                self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=embedding_model_name
                )
                logger.info(f"Using SentenceTransformer embedding function with model: {embedding_model_name}")
            else:
                self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
                logger.info("Using DefaultEmbeddingFunction from ChromaDB.")
            logger.info(f"ChromaDB client initialized. Data will be persisted in: {persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client or embedding function: {e}", exc_info=True)
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
    chroma_service = ChromaService(persist_directory="./test_chroma_db")

    collection_name = "my_test_collection"

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
        #     chroma_service.client.delete_collection(collection_name)
        #     logger.info(f"Successfully deleted collection: {collection_name}")
        # except Exception as e:
        #     logger.error(f"Failed to delete collection {collection_name}: {e}")

    else:
        logger.error(f"Could not get or create collection: {collection_name}")

    logger.info("ChromaService example usage finished.")
