# Mount Olympus Memory Management System

## Overview

The Mount Olympus memory management system is designed to provide an efficient and effective way to manage context within large-scale language models. It integrates naturally into the HADES subsystem, which manages different tiers of memory and context.

## Key Components

### Memory Realms in HADES

- **Elysium (Critical Context - n_keep)**: Stores the most important context that must be preserved.
- **Asphodel (Working Memory)**: Handles active conversation state and temporary computational results.
- **Tartarus (Archival Storage)**: Long-term conversation history with indexed retrieval.

### Rivers of Context Flow

- **Styx (Primary Flow Control)**: Manages context flow between memory realms.
- **Lethe (Forgetting Mechanism)**: Implements controlled forgetting of irrelevant context.

## Getting Started

1. Clone the repository:

 ```shell
 git clone https://github.com/your-repo/mount-olympus.git
 ```

2. Install dependencies:

```shell
cd Olympus
pip install -r requirements.txt
```

3. Run the application:

 ```shell
 python run.py
 ```

## Contributing

We welcome contributions to Mount Olympus! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for more information on how to get involved.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
