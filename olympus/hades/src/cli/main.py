"""HADES CLI - Heuristic Adaptive Data Extraction System."""
from typing import Optional, List, Any, Callable
import asyncio
from functools import wraps
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from ..model.manager import (
    init_model_engine,
    list_available_models,
    download_model,
    load_model,
    generate_embeddings
)
from ..processing.text import process_file
from ..memory_management.arangodb_store import ArangoMemoryStore
from ..monitoring.phoenix_monitor import PhoenixMonitor

app = typer.Typer(
    help="HADES CLI - Heuristic Adaptive Data Extraction System",
    no_args_is_help=True
)
console = Console()

# Global state
store = None
monitor = None
engine = None
current_model = None

def sync_to_async(func: Callable) -> Callable:
    """Convert a sync function to async."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def async_to_sync(func: Callable) -> Callable:
    """Convert an async function to sync."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            console.print(f"[red]Error:[/red] {str(e)}")
            raise typer.Exit(1)
    return wrapper

def validate_setup() -> bool:
    """Validate that HADES components are initialized."""
    if not all([store, monitor, engine]):
        console.print("[red]Error:[/red] HADES components not initialized. Run 'hades setup' first.")
        return False
    return True

@app.command()
def setup(
    db_host: str = typer.Option("http://localhost:8529", help="ArangoDB host URL"),
    db_name: str = typer.Option("hades_memory", help="Database name"),
    node_exporter_path: str = typer.Option(
        "/var/lib/node_exporter/textfile",
        help="Node exporter path for metrics"
    ),
    config_path: str = typer.Option(
        "config/model_engine.yaml",
        help="Model engine config path"
    )
):
    """Initialize HADES components."""
    @async_to_sync
    async def _setup():
        global store, monitor, engine

        try:
            # Initialize monitor
            monitor = PhoenixMonitor(node_exporter_path)
            console.print("✓ Initialized monitoring")

            # Initialize store
            store = ArangoMemoryStore(db_host, db_name, monitor)
            console.print("✓ Initialized memory store")

            # Initialize model engine
            engine = await init_model_engine(config_path)
            console.print("✓ Initialized model engine")

            console.print("\n[green]HADES setup complete![/green]")
        except Exception as e:
            console.print("[red]Error initializing HADES:[/red]", str(e))
            raise

    _setup()

@app.command()
def model(
    action: str = typer.Argument(
        ...,
        help="Action to perform: download, load, list",
        show_choices=True,
        case_sensitive=False
    ),
    model_name: Optional[str] = typer.Argument(None, help="Name of the model"),
    version: Optional[str] = typer.Option(None, help="Model version")
):
    """Manage models using model_engine."""
    if not validate_setup():
        raise typer.Exit(1)

    @async_to_sync
    async def _list_models():
        models = await list_available_models(engine)
        table = Table(title="Available Models")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Embedding Dim", style="yellow")
        table.add_column("Device", style="blue")

        for model in models:
            table.add_row(
                model["name"],
                model["version"],
                model["type"],
                str(model["embedding_dim"]),
                model.get("device", "cpu")
            )
        console.print(table)

    @async_to_sync
    async def _download_model():
        if not model_name:
            console.print("[red]Error:[/red] Model name required for download")
            raise typer.Exit(1)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description=f"Downloading {model_name}...", total=None)
            await download_model(engine, model_name, version)
        console.print(f"[green]Successfully downloaded {model_name}[/green]")

    @async_to_sync
    async def _load_model():
        if not model_name:
            console.print("[red]Error:[/red] Model name required for loading")
            raise typer.Exit(1)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description=f"Loading {model_name}...", total=None)
            global current_model
            current_model = await load_model(engine, model_name, version)
        console.print(f"[green]Successfully loaded {model_name}[/green]")

    actions = {
        "list": _list_models,
        "download": _download_model,
        "load": _load_model
    }

    if action.lower() not in actions:
        console.print(f"[red]Error:[/red] Invalid action: {action}")
        raise typer.Exit(1)

    actions[action.lower()]()

@app.command()
def embed(
    file_path: str = typer.Argument(..., help="Path to file to embed"),
    chunk_size: int = typer.Option(
        1000,
        help="Size of text chunks",
        min=100,
        max=10000
    ),
    overlap: int = typer.Option(
        100,
        help="Overlap between chunks",
        min=0,
        max=1000
    )
):
    """Generate embeddings for a file and store in ArangoDB."""
    if not validate_setup() or not current_model:
        console.print("[red]Error:[/red] No model loaded. Run 'hades model load <model_name>' first")
        raise typer.Exit(1)

    @async_to_sync
    async def _embed():
        try:
            # Process file into chunks
            chunks = await process_file(file_path, chunk_size, overlap)
            console.print(f"✓ Processed file into {len(chunks)} chunks")

            # Generate embeddings
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Generating embeddings...", total=None)
                embeddings = await generate_embeddings(engine, [c["content"] for c in chunks])
            console.print("✓ Generated embeddings")

            # Store embeddings
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Storing embeddings...", total=None)
                for chunk, embedding in zip(chunks, embeddings):
                    await store.store_memory(chunk["content"], embedding, chunk["metadata"])
            console.print("[green]Successfully stored embeddings![/green]")

        except Exception as e:
            console.print(f"[red]Error processing file:[/red] {str(e)}")
            raise

    _embed()

@app.command()
def query(
    query_text: str = typer.Argument(..., help="Query to search for"),
    limit: int = typer.Option(
        5,
        help="Maximum number of results",
        min=1,
        max=100
    ),
    min_similarity: float = typer.Option(
        0.7,
        help="Minimum similarity score",
        min=0.0,
        max=1.0
    )
):
    """Search stored embeddings."""
    if not validate_setup() or not current_model:
        console.print("[red]Error:[/red] No model loaded. Run 'hades model load <model_name>' first")
        raise typer.Exit(1)

    @async_to_sync
    async def _query():
        try:
            # Generate query embedding
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Generating query embedding...", total=None)
                query_embedding = await generate_embeddings(engine, [query_text])
            console.print("✓ Generated query embedding")

            # Find similar memories
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Searching memories...", total=None)
                results = await store.find_similar_memories(
                    query_embedding[0],
                    limit=limit,
                    min_similarity=min_similarity
                )

            # Display results
            if not results:
                console.print("[yellow]No results found[/yellow]")
                return

            for i, result in enumerate(results, 1):
                panel = Panel(
                    f"{result['content']}\n\n[dim]Similarity: {result['similarity']:.2f}[/dim]",
                    title=f"Result {i}",
                    border_style="blue"
                )
                console.print(panel)
                console.print()

        except Exception as e:
            console.print(f"[red]Error performing query:[/red] {str(e)}")
            raise

    _query()

if __name__ == "__main__":
    app()
