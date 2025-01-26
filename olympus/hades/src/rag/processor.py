"""Document processor for RAG pipeline."""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib
import uuid
from loguru import logger

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

from db.arango import ArangoDB

class DocumentProcessor:
    """Process documents for RAG pipeline."""
    
    def __init__(
        self,
        db: ArangoDB,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """Initialize document processor.
        
        Args:
            db: ArangoDB instance
            embedding_model: HuggingFace model name for embeddings
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.db = db
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True,
        )
        
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model,
            cache_folder=".cache/huggingface"
        )
        
    def _generate_chunk_id(self, text: str, parent_id: str) -> str:
        """Generate unique ID for text chunk."""
        hash_input = f"{parent_id}:{text}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:32]
        
    def _extract_metadata(
        self,
        text: str,
        source: Optional[str] = None,
        custom_metadata: Optional[Dict] = None
    ) -> Dict:
        """Extract and combine metadata."""
        metadata = {
            "source": source or "unknown",
            "char_count": len(text),
            "word_count": len(text.split()),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if custom_metadata:
            metadata.update(custom_metadata)
            
        return metadata
        
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ) -> List[Document]:
        """Split text into chunks with metadata."""
        try:
            chunks = self.text_splitter.create_documents(
                texts=[text],
                metadatas=[metadata] if metadata else None
            )
            
            logger.debug(f"Split text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk text: {str(e)}")
            return []
            
    async def generate_embeddings(
        self,
        chunks: List[Document]
    ) -> List[Tuple[Document, List[float]]]:
        """Generate embeddings for text chunks."""
        try:
            # Generate embeddings in batches
            embeddings = self.embedding_model.embed_documents(
                [chunk.page_content for chunk in chunks]
            )
            
            # Pair chunks with their embeddings
            chunk_embeddings = list(zip(chunks, embeddings))
            logger.debug(f"Generated embeddings for {len(chunk_embeddings)} chunks")
            
            return chunk_embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            return []
            
    async def process_document(
        self,
        text: str,
        source: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Process document end-to-end."""
        try:
            # Generate parent ID
            parent_id = str(uuid.uuid4())
            
            # Extract metadata
            doc_metadata = self._extract_metadata(
                text=text,
                source=source,
                custom_metadata=metadata
            )
            
            # Chunk text
            chunks = self.chunk_text(text, doc_metadata)
            if not chunks:
                raise ValueError("No chunks generated from text")
                
            # Generate embeddings
            chunk_embeddings = await self.generate_embeddings(chunks)
            if not chunk_embeddings:
                raise ValueError("Failed to generate embeddings")
                
            # Store chunks with embeddings
            for chunk, embedding in chunk_embeddings:
                chunk_id = self._generate_chunk_id(
                    chunk.page_content,
                    parent_id
                )
                
                # Store in vector collection
                success = await self.db.store_vector(
                    text=chunk.page_content,
                    embedding=embedding,
                    metadata=chunk.metadata,
                    chunk_id=chunk_id,
                    parent_id=parent_id
                )
                
                if not success:
                    logger.warning(f"Failed to store chunk {chunk_id}")
                    
            logger.info(
                f"Processed document: {len(chunks)} chunks, "
                f"parent_id: {parent_id}"
            )
            return parent_id
            
        except Exception as e:
            logger.error(f"Failed to process document: {str(e)}")
            raise
            
    async def delete_document(self, parent_id: str) -> bool:
        """Delete all chunks of a document."""
        try:
            success = await self.db.delete_vectors(parent_id=parent_id)
            if success:
                logger.info(f"Deleted document: {parent_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            return False
