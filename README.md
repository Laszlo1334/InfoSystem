# InfoSystem - Monitoring System with Authorization

This project implements a comprehensive monitoring system with JWT-based authorization for PostgreSQL database operations using Prometheus, Grafana, and Flask.

## Architecture

The system consists of the following services:

1. **PostgreSQL Database** - Stores resources, users, and usage statistics
2. **Data Generator** - Python script that simulates database activity
3. **Prometheus** - Collects and stores metrics
4. **Postgres Exporter** - Exports PostgreSQL metrics to Prometheus
5. **Grafana** - Visualizes metrics through dashboards
6. **Auth Service** - Flask-based JWT authentication service
7. **Nginx Reverse Proxy** - Protects Grafana access with JWT validation

## Features

- JWT token-based authentication
- Protected Grafana access through Nginx reverse proxy
- Custom business metrics dashboards:
  - Resource operations (INSERT/UPDATE/DELETE) tracking
  - Active users monitoring
  - Usage statistics visualization
- Automatic database initialization
- Real-time metrics collection and visualization

## Getting Started

### Prerequisites

- Docker
- Docker Compose v2

### Running the System

1. Start all services:
```bash
docker compose up -d
```

2. Wait for services to initialize (about 30 seconds)

3. Check service status:
```bash
docker compose ps
```

### Accessing Services

- **Auth Service (Direct)**: http://localhost:5000
- **Grafana (Direct, no auth)**: http://localhost:3000 (admin/admin)
- **Grafana (Protected via Nginx)**: http://localhost:8080 (requires JWT token)
- **Prometheus**: http://localhost:9090
- **PostgreSQL**: localhost:55432 (metrics/metrics_pass)

## Authentication Flow

1. **Login** - Get JWT token:
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin"}'
```

Response:
```json
{
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

2. **Verify Token**:
```bash
curl -X GET http://localhost:5000/verify \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

3. **Access Grafana through Nginx** (requires token in Authorization header):
```bash
curl http://localhost:8080/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Test Users

Default test users (defined in `auth/init.db.sql`):
- `admin@example.com` / `admin`
- `user@example.com` / `user`

## Testing

Run the automated test script:
```bash
python test_auth.py
```

This script tests:
- Login with correct credentials
- Login with incorrect credentials
- Token verification
- Nginx proxy authentication

## Custom Dashboards

The system includes a custom "Business Metrics" dashboard that displays:

1. **Resource Operations Rate** - Real-time INSERT/UPDATE/DELETE operations per second
2. **Total Resources** - Current number of resources in the database
3. **Active Users** - Number of registered users
4. **Usage Statistics Records** - Total usage tracking records
5. **Database Operations Over Time** - Historical view of all operations

## Development

### Directory Structure

```
.
├── auth/                   # Authentication service
│   ├── Dockerfile
│   ├── main.py            # Flask app with JWT
│   ├── database.py        # Database initialization
│   ├── entrypoint.sh      # Container startup script
│   ├── init.db.sql        # Initial database schema
│   └── requirements.txt
├── grafana/               # Grafana configuration
│   ├── provisioning/      # Auto-provisioning configs
│   │   ├── dashboards/
│   │   └── datasources/
│   └── dashboards/        # Custom dashboard definitions
├── nginx/                 # Nginx reverse proxy
│   └── nginx.conf         # Nginx configuration
├── prometheus/            # Prometheus configuration
│   └── prometheus.yml
├── python/                # Data generator
│   └── generator.py
├── sql/                   # PostgreSQL initialization
│   └── init.sql
├── docker-compose.yml     # Service orchestration
└── test_auth.py          # Authentication tests

```

### Stopping the System

```bash
docker compose down
```

To remove all data volumes:
```bash
docker compose down -v
```

## Security Notes

- The secret key in `auth/main.py` should be changed in production
- JWT tokens expire after 24 hours
- Passwords are currently stored in plain text (should use hashing in production)
- Consider using environment variables for sensitive configuration

## Troubleshooting

### Auth service fails to start
Check the entrypoint.sh file encoding:
```bash
file auth/entrypoint.sh
```

### Grafana dashboards not appearing
Restart the Grafana service:
```bash
docker compose restart grafana
```

### Connection refused errors
Ensure all services are healthy:
```bash
docker compose ps
docker compose logs [service-name]
```
