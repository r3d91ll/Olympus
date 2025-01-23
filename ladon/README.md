# LadonStack

LadonStack is a comprehensive monitoring solution that integrates Phoenix, Prometheus, Grafana, Node Exporter, and DCGM Exporter to provide robust observability for your systems and applications.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone this repository:

   ``` shell
   git clone <your-repository-url>
   cd LadonStack
   ```

2. Create a `.env` file based on the `example.env` and fill in your desired configuration:

   ``` shell
   cp example.env .env
   ```

3. Start the stack:

   ``` shell
   docker-compose up -d
   ```

4. Access Grafana at `http://localhost:9300` (or the port you specified in `.env`)

## Connecting Grafana to Prometheus

1. Log in to Grafana (default credentials are in your `.env` file)
2. Go to Configuration > Data Sources
3. Click "Add data source"
4. Select "Prometheus"
5. Set the URL to `http://prometheus:9090`
6. Click "Save & Test"

## Setting up Dashboards

### Node Exporter Dashboard

1. In Grafana, click the "+" icon on the left sidebar
2. Select "Import"
3. Enter dashboard ID `1860` (or choose another from [Grafana's dashboard repository](https://grafana.com/grafana/dashboards/))
4. Select your Prometheus data source
5. Click "Import"

### DCGM Exporter Dashboard

1. Follow the same steps as above
2. Use dashboard ID `12239` for DCGM Exporter

You can find more dashboards at [Grafana's dashboard repository](https://grafana.com/grafana/dashboards/).

## Phoenix Setup

Phoenix is an AI Observability & Evaluation tool. While it's included in this stack, it's still in development.

- Docker container: [arizephoenix/phoenix](https://hub.docker.com/r/arizephoenix/phoenix)
- GitHub repository: [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix)

To interact with Phoenix, you can access it at:

- HTTP: `http://localhost:6006`
- gRPC: `localhost:4317`
- Prometheus metrics: `http://localhost:9091`

Refer to the [Phoenix documentation](https://github.com/Arize-ai/phoenix/blob/main/README.md) for more details on how to use and configure Phoenix.

## Troubleshooting

If you encounter any issues:

1. Check the logs: `docker-compose logs`
2. Ensure all containers are running: `docker-compose ps`
3. Verify your `.env` file configuration
4. Restart the stack: `docker-compose down && docker-compose up -d`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).
