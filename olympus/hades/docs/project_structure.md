# Project Olympus Structure

olympus/
├── hades/                      # Knowledge and data management
│   ├── core/                   # Core RAG and data processing
│   ├── db/                     # Database interactions
│   ├── memory/                 # Memory management tiers
│   ├── model_engine/          # Model management
│   └── api/                    # MCP and REST interfaces
│
├── agents/                     # Olympus agent pool
│   ├── core/                   # Agent framework
│   ├── executors/             # Task execution agents
│   ├── optimizers/            # Performance optimization agents
│   ├── analyzers/             # Data analysis agents
│   └── schedulers/            # Task scheduling
│
├── delphi/                     # Frontend interface
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Main application pages
│   │   ├── hooks/             # Custom React hooks
│   │   └── styles/            # Global styles and themes
│   └── public/                # Static assets
│
├── ladon/                      # LadonStack integration
│   ├── exporters/             # Metric exporters
│   ├── collectors/            # Data collectors
│   ├── dashboards/            # Grafana dashboards
│   └── alerts/                # Alert configurations
│
├── shared/                     # Shared utilities and types
│   ├── types/                 # TypeScript/Python type definitions
│   ├── constants/             # Shared constants
│   ├── utils/                 # Common utilities
│   └── protocols/             # Communication protocols
│
├── config/                     # Configuration files
│   ├── development/           # Development settings
│   ├── production/            # Production settings
│   └── testing/               # Test configurations
│
├── scripts/                    # Build and maintenance scripts
│   ├── setup/                 # Setup scripts
│   ├── deploy/                # Deployment scripts
│   └── maintenance/           # Maintenance scripts
│
├── tests/                      # Integration tests
│   ├── e2e/                   # End-to-end tests
│   ├── integration/           # Cross-component tests
│   └── performance/           # Performance tests
│
└── docs/                       # Documentation
    ├── architecture/          # System architecture
    ├── api/                   # API documentation
    ├── deployment/            # Deployment guides
    └── development/           # Development guides

## Key Benefits

1. **Unified Development**
   - Single source of truth
   - Consistent versioning
   - Simplified dependency management
   - Coordinated releases

2. **Shared Resources**
   - Common utilities and types
   - Shared configuration
   - Unified testing framework
   - Centralized documentation

3. **Streamlined Workflow**
   - Single repository to clone
   - Unified build process
   - Integrated CI/CD
   - Centralized issue tracking

4. **Clear Component Separation**
   - HADES: Knowledge management
   - Olympus: Agent operations
   - Delphi: User interface
   - LadonStack: System monitoring

## Development Guidelines

1. **Component Boundaries**
   - Components communicate through well-defined interfaces
   - Shared code goes in `shared/` directory
   - Each component has its own configuration
   - Monitoring handled by LadonStack

2. **Code Organization**
   - Follow consistent naming conventions
   - Use relative imports within components
   - Share types and utilities through `shared/`
   - Keep component-specific code isolated

3. **Testing Strategy**
   - Unit tests within each component
   - Integration tests in root `tests/` directory
   - E2E tests covering full system flows
   - Performance metrics via LadonStack

4. **Documentation**
   - Main documentation in root `docs/`
   - Component-specific docs in their directories
   - API documentation generated from code
   - Architecture diagrams in `docs/architecture/`
