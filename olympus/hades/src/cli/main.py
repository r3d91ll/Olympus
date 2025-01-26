#!/usr/bin/env python3
from typing import Optional, List
import asyncio
import typer
from pathlib import Path
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..memory_management.arangodb_store import ArangoMemoryStore
from ..monitoring.phoenix_monitor import PhoenixMonitor

app = typer.Typer(help="HADES CLI - Memory Management System")
console = Console()

# Initialize components
store = None
monitor = None

@app.command()
def setup(
    db_host: str = "http://localhost:8529",
    db_name: str = "hades_memory",
    node_exporter_path: str = "/var/lib/node_exporter/textfile"
):
    """Initialize HADES components."""
    global store, monitor
    
    try:
        # Initialize monitoring
        monitor = PhoenixMonitor(
            node_exporter_path=node_exporter_path,
            metrics_prefix="olympus_hades"
        )
        
        # Initialize ArangoDB store
        store = ArangoMemoryStore(
            host=db_host,
            db_name=db_name,
            phoenix_monitor=monitor
        )
        
        console.print("[green]✓[/green] HADES components initialized successfully")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error initializing HADES: {str(e)}")
        raise typer.Exit(1)

@app.command()
def model(
    action: str = typer.Argument(..., help="Action to perform: download, load, list"),
    model_name: Optional[str] = typer.Argument(None, help="Name of the model")
):
    """Manage models using model_engine."""
    if not any([action == a for a in ["download", "load", "list"]]):
        console.print("[red]✗[/red] Invalid action. Use: download, load, or list")
        raise typer.Exit(1)
        
    try:
        if action == "list":
            # TODO: Implement model listing
            console.print("Available models:")
            # Call model_engine.list_models()
            
        elif action == "download":
            if not model_name:
                console.print("[red]✗[/red] Model name required for download")
                raise typer.Exit(1)
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                progress.add_task(f"Downloading {model_name}...", total=None)
                # TODO: Implement model download
                # await model_engine.download_model(model_name)
                
        elif action == "load":
            if not model_name:
                console.print("[red]✗[/red] Model name required for loading")
                raise typer.Exit(1)
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                progress.add_task(f"Loading {model_name}...", total=None)
                # TODO: Implement model loading
                # await model_engine.load_model(model_name)
                
    except Exception as e:
        console.print(f"[red]✗[/red] Error in model command: {str(e)}")
        raise typer.Exit(1)

@app.command()
def embed(
    file_path: str = typer.Argument(..., help="Path to file to embed"),
    chunk_size: int = typer.Option(1000, help="Size of text chunks"),
    overlap: int = typer.Option(100, help="Overlap between chunks")
):
    """Generate embeddings for a file and store in ArangoDB."""
    if not store:
        console.print("[red]✗[/red] HADES not initialized. Run 'setup' first.")
        raise typer.Exit(1)
        
    file_path = Path(file_path)
    if not file_path.exists():
        console.print(f"[red]✗[/red] File not found: {file_path}")
        raise typer.Exit(1)
        
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processing file...", total=None)
            # TODO: Implement file processing
            # chunks = chunk_file(file_path, chunk_size, overlap)
            # embeddings = await model.embed_chunks(chunks)
            # await store.store_embeddings(embeddings)
            
        console.print("[green]✓[/green] File processed successfully")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error processing file: {str(e)}")
        raise typer.Exit(1)

@app.command()
def query(
    query_text: str = typer.Argument(..., help="Query to search for"),
    limit: int = typer.Option(5, help="Maximum number of results"),
    min_similarity: float = typer.Option(0.7, help="Minimum similarity score")
):
    """Search stored embeddings."""
    if not store:
        console.print("[red]✗[/red] HADES not initialized. Run 'setup' first.")
        raise typer.Exit(1)
        
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Searching...", total=None)
            # TODO: Implement search
            # embedding = await model.embed_text(query_text)
            # results = await store.find_similar_memories(
            #     query_vector=embedding,
            #     limit=limit,
            #     min_similarity=min_similarity
            # )
            
        # TODO: Format and display results
        console.print("\nResults:")
        # for result in results:
        #     console.print(f"- {result['content']} (score: {result['similarity']:.2f})")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error searching: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
