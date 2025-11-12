# IntelliNet Orchestrator

A Python + Angular based network service orchestration system that simulates a telecommunication service orchestration platform.

## Project Structure

```
intellinet-orchestrator/
├── src/                          # Python backend
│   ├── models/                   # Domain models (Device, Link, Service)
│   ├── repositories/             # Data access layer (Neo4j, SQLite)
│   ├── services/                 # Business logic (ServiceOrchestrator)
│   ├── api/                      # FastAPI REST endpoints
│   └── config.py                 # Configuration management
├── frontend/                     # Angular frontend
│   ├── src/
│   │   └── app/
│   │       ├── core/             # Core module (shared services)
│   │       └── features/         # Feature modules
│   │           ├── topology/     # Topology visualization
│   │           ├── services/     # Service management
│   │           └── analytics/    # Analytics dashboard
│   ├── package.json
│   └── angular.json
├── config.yaml                   # Application configuration
├── .env.example                  # Environment variables template
└── requirements.txt              # Python dependencies
```

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start Neo4j database (Docker):
   ```bash
   docker run -d --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/your_password \
     neo4j:5.12
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm start
   ```

The frontend will be available at http://localhost:4200

## Configuration

The application uses a hybrid configuration approach:
- `config.yaml` for default settings
- Environment variables (`.env`) for sensitive data and overrides
- Environment variables take precedence over YAML settings

## Technology Stack

**Backend:**
- Python 3.11+
- FastAPI
- Neo4j (graph database)
- SQLite (metrics storage)
- Pydantic (data validation)

**Frontend:**
- Angular 16+
- TypeScript
- Cytoscape.js (topology visualization)
- Plotly.js (analytics charts)
- Angular Material (UI components)

## Development

### Running Tests

Backend:
```bash
pytest tests/ --cov=src
```

Frontend:
```bash
cd frontend
npm test
```

### Code Structure

- **Domain Models**: OOP hierarchy for network devices (DWDM, MPLS, GPON, etc.)
- **Rule Engine**: Drools-style validation for service provisioning
- **Repository Pattern**: Abstraction for Neo4j and SQLite operations
- **Service Layer**: Business logic orchestration
- **REST API**: FastAPI endpoints with Pydantic validation

## Deployment

### Docker Deployment (Recommended)

The easiest way to deploy IntelliNet Orchestrator is using Docker Compose:

1. **Prerequisites:**
   - Docker 20.10+
   - Docker Compose 2.0+

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and set secure passwords:
   # - NEO4J_PASSWORD
   # - JWT_SECRET
   ```

3. **Deploy using the deployment script:**
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh production
   ```

   Or manually with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. **Initialize databases:**
   ```bash
   python scripts/init_db.py
   ```

5. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs
   - Neo4j Browser: http://localhost:7474

### Manual Deployment

For development or custom deployments:

1. **Start Neo4j:**
   ```bash
   docker run -d --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/your_password \
     neo4j:5.12
   ```

2. **Initialize databases:**
   ```bash
   python scripts/init_db.py
   ```

3. **Start backend:**
   ```bash
   uvicorn src.api.app:app --host 0.0.0.0 --port 8000
   ```

4. **Build and serve frontend:**
   ```bash
   cd frontend
   npm run build -- --configuration production
   # Serve the dist/frontend directory with a web server
   ```

### Health Checks

The application provides health check endpoints:

- Backend: `GET /health`
- Frontend: `GET /health` (via nginx)

### Monitoring

View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f neo4j
```

Check service status:
```bash
docker-compose ps
```

### Stopping Services

```bash
docker-compose down

# To remove volumes as well
docker-compose down -v
```

## CI/CD

The project includes GitHub Actions workflows for continuous integration:

- **Backend Tests**: Runs pytest with Neo4j service container
- **Frontend Tests**: Runs Angular unit tests
- **Code Quality**: Linting and formatting checks
- **Security Scanning**: Dependency and code security scans

See `.github/workflows/ci.yml` for details.

## Features

### Network Topology Management
- Create and manage network devices (DWDM, OTN, SONET, MPLS, GPON, FTTH)
- Define links between devices with bandwidth and latency attributes
- Interactive graph visualization using Cytoscape.js
- Real-time topology updates

### Service Provisioning
- Automated service provisioning with path finding
- Rule-based validation engine for capacity and QoS constraints
- Support for multiple service types (MPLS VPN, OTN Circuit, GPON Access, FTTH)
- Service lifecycle management (provision, activate, decommission)

### Analytics and Monitoring
- Real-time network status dashboard
- Historical metrics and performance data
- Device and link utilization tracking
- Service logs and event tracking

### Path Optimization
- Shortest path calculation using Neo4j algorithms
- Optimal path selection considering utilization and latency
- Multi-constraint path finding

### Security
- JWT-based authentication
- Role-based access control (Admin/User)
- Secure password hashing with bcrypt
- Protected API endpoints

## Quick Start

### Using Docker (Recommended)

1. Clone the repository and configure environment:
   ```bash
   git clone <repository-url>
   cd intellinet-orchestrator
   cp .env.example .env
   # Edit .env with your settings
   ```

2. Start all services:
   ```bash
   docker-compose up -d
   ```

3. Initialize the database:
   ```bash
   docker-compose exec backend python scripts/init_db.py
   ```

4. Access the application:
   - Frontend: http://localhost
   - API Docs: http://localhost:8000/api/docs

### Manual Setup

See the detailed setup instructions above for backend and frontend setup.

## Usage Examples

### Creating a Network Topology

1. **Login** to the application (default credentials: admin/admin123)

2. **Create devices** via API or UI:
   ```bash
   curl -X POST http://localhost:8000/api/topology/device \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "ROUTER01",
       "name": "Core Router 1",
       "type": "MPLS",
       "capacity": 100.0,
       "location": "NYC-DC1"
     }'
   ```

3. **Create links** between devices:
   ```bash
   curl -X POST http://localhost:8000/api/topology/link \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "LINK01",
       "source_device_id": "ROUTER01",
       "target_device_id": "ROUTER02",
       "bandwidth": 10.0,
       "type": "fiber",
       "latency": 2.5
     }'
   ```

4. **Provision a service**:
   ```bash
   curl -X POST http://localhost:8000/api/service/provision \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "VPN001",
       "service_type": "MPLS_VPN",
       "source_device_id": "ROUTER01",
       "target_device_id": "ROUTER02",
       "bandwidth": 5.0,
       "latency_requirement": 10.0
     }'
   ```

## Demo

Want to see IntelliNet Orchestrator in action? Follow our comprehensive demo guide:

```bash
# 1. Start the system
docker-compose up -d

# 2. Populate sample data
docker-compose exec backend python scripts/populate_sample_data.py

# 3. Run service provisioning demo
docker-compose exec backend python scripts/demo_service_provisioning.py

# 4. Access the UI
# Open http://localhost in your browser
# Login with: admin / admin123
```

See [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for detailed demo scenarios and walkthroughs.

## Documentation

- **Demo Guide**: See [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) - Complete demonstration scenarios
- **API Documentation**: See [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) or visit `/api/docs`
- **Developer Guide**: See [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) - Extending the system
- **Architecture**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design and patterns
- **Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- **Security Implementation**: See [SECURITY_IMPLEMENTATION.md](SECURITY_IMPLEMENTATION.md) - Security features

## Troubleshooting

### Backend won't start
- Check Neo4j is running: `docker ps | grep neo4j`
- Verify database credentials in `.env`
- Check logs: `docker-compose logs backend`

### Frontend can't connect to backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `config.yaml`
- Verify API URL in frontend environment

### Database connection errors
- Ensure Neo4j is accessible on port 7687
- Verify credentials match between `.env` and Neo4j
- Check Neo4j logs: `docker-compose logs neo4j`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests
4. Run tests: `pytest tests/`
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature/my-feature`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the documentation in the `docs/` directory
- Review the API documentation at `/api/docs`

## Acknowledgments

- FastAPI for the excellent web framework
- Neo4j for graph database capabilities
- Angular team for the frontend framework
- Cytoscape.js for network visualization
