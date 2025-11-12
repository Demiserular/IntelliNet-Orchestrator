# IntelliNet Orchestrator - Architecture Documentation

## Overview

IntelliNet Orchestrator is a full-stack network service orchestration platform built with Python (FastAPI) backend and Angular frontend. The system demonstrates enterprise-grade software engineering practices including object-oriented design, graph database modeling, RESTful APIs, and automated testing.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client Layer (Browser)                       │
│                    Angular SPA (Port 4200)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST + JSON
                             │ JWT Authentication
┌────────────────────────────▼────────────────────────────────────┐
│                      API Gateway Layer                           │
│                   FastAPI (Port 8000)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Routes: /api/topology, /api/service, /api/analytics    │   │
│  │  Middleware: CORS, Logging, Error Handling, Auth        │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Service Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Service    │  │     Rule     │  │   Auth Service       │  │
│  │ Orchestrator │  │    Engine    │  │   (JWT + RBAC)       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   Repository Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │    Neo4j     │  │   Metrics    │  │   User Repository    │  │
│  │  Repository  │  │  Repository  │  │   (SQLite)           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Data Layer                                    │
│  ┌──────────────┐           ┌──────────────────────────────┐    │
│  │    Neo4j     │           │         SQLite               │    │
│  │  (Topology)  │           │  (Metrics, Users, Logs)      │    │
│  │  Port 7687   │           │                              │    │
│  └──────────────┘           └──────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Backend Components

#### 1. Domain Model Layer

**Purpose**: Represents core business entities using object-oriented design.

**Key Classes**:
- `Device` (Abstract Base Class)
  - `DWDMDevice`: Dense Wavelength Division Multiplexing
  - `MPLSRouter`: MPLS Label Switching Router
  - `GPONDevice`: Gigabit Passive Optical Network (OLT/ONT)
- `Link`: Network connections between devices
- `Service`: Network services (VPN, Circuit, Access)
- `User`: System users with roles

**Design Patterns**:
- **Inheritance**: Device hierarchy with polymorphic behavior
- **Factory Pattern**: Device creation based on type
- **Value Objects**: Enums for types and statuses

**Example**:
```python
class Device(ABC):
    @abstractmethod
    def provision(self, service: Service) -> bool:
        pass
    
    @abstractmethod
    def calculate_available_capacity(self) -> float:
        pass

class MPLSRouter(Device):
    def provision(self, service: Service) -> bool:
        # MPLS-specific provisioning logic
        pass
```

#### 2. Repository Layer

**Purpose**: Abstracts data access and persistence logic.

**Components**:

**Neo4jRepository**:
- Manages graph database operations
- Stores topology (devices and links)
- Implements path-finding algorithms
- Uses Cypher query language

**MetricsRepository**:
- Stores time-series metrics in SQLite
- Tracks device utilization
- Records link performance
- Logs service events

**UserRepository**:
- Manages user authentication data
- Stores hashed passwords
- Handles user roles

**Design Patterns**:
- **Repository Pattern**: Encapsulates data access
- **Connection Pooling**: Efficient database connections
- **Retry Logic**: Handles transient failures

#### 3. Service Layer

**Purpose**: Implements business logic and orchestration.

**ServiceOrchestrator**:
- Coordinates service provisioning workflow
- Finds optimal paths between devices
- Updates device utilization
- Records metrics and logs

**RuleEngine**:
- Validates service requests
- Enforces capacity constraints
- Checks QoS requirements
- Supports dynamic rule loading

**AuthService**:
- Handles user authentication
- Generates JWT tokens
- Validates credentials
- Manages sessions

**Design Patterns**:
- **Strategy Pattern**: Pluggable validation rules
- **Chain of Responsibility**: Rule evaluation pipeline
- **Observer Pattern**: Event logging

#### 4. API Layer

**Purpose**: Exposes RESTful endpoints for client interaction.

**FastAPI Application**:
- Route handlers for all operations
- Request/response validation with Pydantic
- OpenAPI documentation generation
- CORS middleware for frontend access

**Endpoints**:
- `/api/topology/*`: Device and link management
- `/api/service/*`: Service provisioning
- `/api/analytics/*`: Metrics and monitoring
- `/api/auth/*`: Authentication

**Design Patterns**:
- **Dependency Injection**: Service and repository injection
- **Middleware Pattern**: Cross-cutting concerns
- **DTO Pattern**: Pydantic models for data transfer

### Frontend Components

#### 1. Core Module

**Services**:
- `TopologyService`: Device and link operations
- `ServiceProvisionService`: Service management
- `AnalyticsService`: Metrics retrieval
- `AuthService`: Authentication and token management

**Guards**:
- `AuthGuard`: Protects authenticated routes
- `AdminGuard`: Restricts admin-only routes

**Interceptors**:
- `AuthInterceptor`: Adds JWT token to requests
- `ErrorInterceptor`: Handles API errors

#### 2. Feature Modules

**Topology Module**:
- `TopologyVisualizerComponent`: Cytoscape.js graph
- `DeviceListComponent`: Device management
- `DeviceFormComponent`: Device creation

**Services Module**:
- `ServiceProvisionComponent`: Service creation
- `ServiceListComponent`: Active services

**Analytics Module**:
- `AnalyticsDashboardComponent`: Metrics visualization
- Plotly.js charts for utilization

**Auth Module**:
- `LoginComponent`: User authentication
- Token storage and management

## Data Architecture

### Neo4j Graph Schema

**Node Labels**:
```cypher
(:Device {
  id: string,
  name: string,
  type: string,
  capacity: float,
  location: string,
  status: string,
  utilization: float
})

(:Service {
  id: string,
  service_type: string,
  bandwidth: float,
  status: string
})
```

**Relationships**:
```cypher
(Device)-[:LINK {
  id: string,
  bandwidth: float,
  latency: float,
  utilization: float,
  type: string
}]->(Device)

(Service)-[:USES]->(Device)
(Service)-[:TRAVERSES]->(Link)
```

**Indexes**:
```cypher
CREATE INDEX device_id_index FOR (d:Device) ON (d.id);
CREATE INDEX device_type_index FOR (d:Device) ON (d.type);
CREATE INDEX service_id_index FOR (s:Service) ON (s.id);
```

### SQLite Schema

**Tables**:

```sql
-- Device metrics
CREATE TABLE device_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    utilization REAL,
    status TEXT
);

-- Link metrics
CREATE TABLE link_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    utilization REAL,
    latency REAL
);

-- Service logs
CREATE TABLE service_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT,
    details TEXT
);

-- Users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT,
    full_name TEXT,
    disabled BOOLEAN DEFAULT 0
);
```

## Security Architecture

### Authentication Flow

```
1. User submits credentials
   ↓
2. AuthService validates credentials
   ↓
3. Generate JWT token with user claims
   ↓
4. Return token to client
   ↓
5. Client stores token (localStorage)
   ↓
6. Client includes token in Authorization header
   ↓
7. API validates token and extracts user info
   ↓
8. Check user role for authorization
   ↓
9. Process request or return 403
```

### Security Measures

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: HS256 algorithm, configurable expiry
- **Role-Based Access Control**: Admin and User roles
- **CORS**: Configured allowed origins
- **Input Validation**: Pydantic models
- **SQL Injection Prevention**: Parameterized queries
- **Cypher Injection Prevention**: Parameterized Neo4j queries

## Deployment Architecture

### Docker Compose Deployment

```
┌─────────────────────────────────────────────┐
│              Nginx (Port 80)                │
│         Reverse Proxy + Static Files        │
└──────────┬──────────────────────────────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼────┐   ┌───▼────────┐
│Frontend│   │  Backend   │
│Angular │   │  FastAPI   │
│  SPA   │   │ Port 8000  │
└────────┘   └───┬────────┘
                 │
         ┌───────┴────────┐
         │                │
    ┌────▼─────┐    ┌────▼──────┐
    │  Neo4j   │    │  SQLite   │
    │Port 7687 │    │   File    │
    └──────────┘    └───────────┘
```

### Container Configuration

**Backend Container**:
- Python 3.11 slim image
- Installs dependencies from requirements.txt
- Exposes port 8000
- Health check endpoint

**Frontend Container**:
- Node 18 for build
- Nginx alpine for serving
- Compiled Angular app
- Gzip compression enabled

**Neo4j Container**:
- Official Neo4j 5.12 image
- Persistent volume for data
- Exposed ports: 7474 (HTTP), 7687 (Bolt)

## Performance Considerations

### Database Optimization

**Neo4j**:
- Indexes on frequently queried properties
- Connection pooling
- Query result caching
- Limit result sets

**SQLite**:
- Indexes on timestamp and foreign keys
- Batch inserts for metrics
- Regular VACUUM operations
- Write-ahead logging (WAL) mode

### API Optimization

- Async endpoint handlers
- Response compression
- Pagination for large result sets
- Caching headers for static data

### Frontend Optimization

- Lazy loading of feature modules
- Virtual scrolling for large lists
- OnPush change detection strategy
- Production build with AOT compilation

## Scalability Considerations

### Horizontal Scaling

**Backend**:
- Stateless API servers
- Load balancer distribution
- Shared database connections

**Database**:
- Neo4j clustering for high availability
- PostgreSQL instead of SQLite for production
- Read replicas for analytics queries

### Vertical Scaling

- Increase container resources
- Optimize database queries
- Add caching layer (Redis)

## Monitoring and Observability

### Logging

- Structured logging with timestamps
- Log levels: DEBUG, INFO, WARNING, ERROR
- Rotating file handlers
- Centralized log aggregation (future)

### Metrics

- Request/response times
- Error rates
- Database query performance
- Resource utilization

### Health Checks

- `/health` endpoint for liveness
- Database connectivity checks
- Dependency health status

## Technology Decisions

### Why Neo4j?

- Natural representation of network topology
- Efficient path-finding algorithms
- Flexible schema for diverse device types
- Cypher query language for graph operations

### Why FastAPI?

- High performance (async support)
- Automatic OpenAPI documentation
- Type safety with Pydantic
- Modern Python features

### Why Angular?

- Enterprise-grade framework
- TypeScript for type safety
- Rich ecosystem of libraries
- Strong CLI tooling

### Why SQLite?

- Zero configuration for development
- Sufficient for metrics storage
- Easy migration to PostgreSQL
- File-based portability

## Future Enhancements

1. **Caching Layer**: Redis for frequently accessed data
2. **Message Queue**: RabbitMQ for async operations
3. **Microservices**: Split into smaller services
4. **GraphQL**: Alternative API interface
5. **Real-time Updates**: WebSocket support
6. **Advanced Analytics**: Machine learning for optimization
7. **Multi-tenancy**: Support for multiple organizations
8. **Audit Trail**: Comprehensive change tracking

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j Graph Database](https://neo4j.com/docs/)
- [Angular Framework](https://angular.io/)
- [Cytoscape.js](https://js.cytoscape.org/)
- [Pydantic](https://docs.pydantic.dev/)
