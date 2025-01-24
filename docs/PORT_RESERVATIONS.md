# Olympus Port Reservations

This document defines the port reservations for all Olympus services to prevent conflicts during development and deployment.

## Infrastructure Ports (9900-9999)

These ports are reserved for LadonStack and other infrastructure services:

| Service        | Port | Purpose                    | Internal Port |
|---------------|------|----------------------------|---------------|
| Prometheus    | 9901 | Metrics collection         | 9901         |
| Grafana       | 9902 | Monitoring UI             | 9902         |
| Node Exporter | 9903 | System metrics            | 9903         |
| DCGM          | 9904 | GPU metrics               | 9904         |
| cAdvisor      | 9905 | Container metrics         | 9905         |
| Loki          | 9906 | Log aggregation           | 9906         |
| Promtail      | 9907 | Log collection            | 9907         |
| Reserved      | 9908-9949 | Future monitoring services | -       |
| Reserved      | 9950-9989 | Future logging services   | -       |
| Reserved      | 9990-9999 | Emergency/Debug ports    | -       |

## Application Ports (8001-8999)

These ports are available for HADES and other application services:

| Service          | Port | Purpose                    | Internal Port |
|-----------------|------|----------------------------|---------------|
| HADES RAG       | 8001 | RAG API endpoint          | 8001         |
| HADES ArangoDB  | 8529 | Vector database           | 8529         |
| Reserved        | 8002-8528 | Future HADES services | -            |
| Reserved        | 8530-8999 | Future applications   | -            |

## Common Ports (Reserved)

These ports are intentionally left available for standard services:

| Port Range | Purpose |
|-----------|---------|
| 80, 443   | Web traffic (HTTP/HTTPS) |
| 8080, 8443| Alternative web ports |
| 22, 2222  | SSH access |
| 5000-5999 | Common development ports |
| 3000-3999 | Common database/cache ports |

## Guidelines

1. Infrastructure services MUST use ports in the 99xx range
2. Application services SHOULD use ports in the 8xxx range
3. Never use common ports for custom services
4. Document any new port assignments in this file
5. Internal container ports should match external ports where possible
6. Use environment variables for all port configurations
7. Reserve 9990-9999 for emergency/debug ports

This port scheme ensures:
- No conflicts between infrastructure and applications
- Easy transition to bare metal
- Clear separation of concerns
- Standard ports remain available
- Consistent internal/external port mapping
- Easy to remember monitoring ports (all 99xx)
- Room for infrastructure growth (50+ available ports)
- Emergency ports always available
