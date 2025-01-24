"""RAG API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Dict, List, Optional
from pydantic import BaseModel
from loguru import logger

from db.arango import ArangoDB
from rag.processor import DocumentProcessor
from rag.retriever import Retriever
from rag.chain import RAGChain

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    metadata_filter: Optional[Dict] = None
    return_sources: bool = True

class QueryResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
    relevance_scores: Optional[List[float]] = None

async def get_rag_chain():
    """Get RAG chain instance."""
    try:
        db = ArangoDB()
        await db.connect()
        
        retriever = Retriever(db)
        chain = RAGChain(retriever)
        return chain
    except Exception as e:
        logger.error(f"Failed to initialize RAG chain: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize RAG system"
        )

async def get_document_processor():
    """Get document processor instance."""
    try:
        db = ArangoDB()
        await db.connect()
        return DocumentProcessor(db)
    except Exception as e:
        logger.error(f"Failed to initialize document processor: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize document processor"
        )

@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    chain: RAGChain = Depends(get_rag_chain)
):
    """Query the RAG system."""
    try:
        response = await chain.generate_response(
            query=request.query,
            metadata_filter=request.metadata_filter,
            return_sources=request.return_sources
        )
        
        if isinstance(response, dict):
            return QueryResponse(**response)
        return QueryResponse(response=response)
        
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process query"
        )

@router.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    metadata: Optional[Dict] = None,
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """Ingest a document into the RAG system."""
    try:
        content = await file.read()
        text = content.decode("utf-8")
        
        # Process document
        doc_id = await processor.process(
            text=text,
            metadata={
                "source": file.filename,
                **(metadata or {})
            }
        )
        
        return {
            "success": True,
            "document_id": doc_id
        }
        
    except Exception as e:
        logger.error(f"Document ingestion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to ingest document"
        )

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """Delete a document from the RAG system."""
    try:
        success = await processor.delete(doc_id)
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Document deletion failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document"
        )
