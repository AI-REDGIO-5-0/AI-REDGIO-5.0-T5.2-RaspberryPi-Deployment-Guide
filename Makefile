# Makefile for managing the Edge AI system

# Build all Docker services
build:
	docker compose build

# Start all services (build if needed)
up:
	docker compose up --build

# Stop and remove all containers
down:
	docker compose down

# Show logs from the main edge_node container
logs:
	docker compose logs -f edge_node

# Show logs from the REST API
logs-rest:
	docker compose logs -f rest_api

# Show logs from the MQTT broker
logs-mqtt:
	docker compose logs -f mqtt

# Restart only the edge_node container
restart:
	docker compose restart edge_node

# Clean volumes and everything (be careful!)
clean:
	docker compose down -v

# Tail full system logs
logs-all:
	docker compose logs -f

# Rebuild everything from scratch
rebuild:
	docker compose down -v
	docker compose build
	docker compose up