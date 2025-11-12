# IntelliNet Orchestrator - Developer Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Code Structure](#code-structure)
4. [Domain Models](#domain-models)
5. [Repository Layer](#repository-layer)
6. [Service Layer](#service-layer)
7. [API Layer](#api-layer)
8. [Frontend Development](#frontend-development)
9. [Testing](#testing)
10. [Extending the System](#extending-the-system)
11. [Best Practices](#best-practices)

---

## Architecture Overview

IntelliNet Orchestrator follows a layered architecture pattern:

```
┌─────────────────────────────────────────┐
│         Angular Frontend (UI)           │
└──────────────┬──────────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────────┐
│         FastAPI (API Layer)             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Service Layer (Business Logic)     │
│  - ServiceOrchestrator                  │
│  - RuleEngine                           │
│  - AuthService                          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Repository Layer (Data Access)     │
│  - Neo4jRepository                      │
│  - MetricsRepository                    │
│  - UserRepository                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Domain Models (Entities)        │
│  - Device, Link, Service                │
│  - Specialized Devices                  │
└─────────────────────────────────────────┘
```

### Key Design Patterns

- **Repository Pattern**: Abstracts data access logic
- **Dependency Injection**: Manages component dependencies
- **Factory Pattern**: Creates specialized device instances
- **Strategy Pattern**: Rule engine for validation
- **Observer Pattern**: Event logging and metrics

---

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git
- IDE (VS Code, PyCharm, or similar)

### Backend Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install development tools:**
   ```bash
   pip install black flake8 mypy pytest-watch
   ```

4. **Start Neo4j:**
   ```bash
   docker run -d --name neo4j-dev \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/devpassword \
     neo4j:5.12
   ```

5. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env for development
   ```

6. **Run the application:**
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Run in watch mode:**
   ```bash
   npm run watch
   ```

---

## Code Structure

### Backend Structure

```
src/
├── models/                    # Domain models
│   ├── device.py             # Base Device class
│   ├── specialized_devices.py # DWDM, MPLS, GPON devices
│   ├── link.py               # Link class
│   ├── service.py            # Service class
│   └── user.py               # User model
├── repositories/              # Data access layer
│   ├── neo4j_repository.py   # Neo4j operations
│   ├── metrics_repository.py # SQLite metrics
│   └── user_repository.py    # User data access
├── services/                  # Business logic
│   ├── service_orchestrator.py
│   ├── rule_engine.py
│   └── auth_service.py
├── api/                       # REST API
│   ├── app.py                # FastAPI application
│   ├── models.py             # Pydantic models
│   ├── routes/               # API endpoints
│   │   ├── topology.py
│   │   ├── services.py
│   │   ├── analytics.py
│   │   └── auth.py
│   ├── dependencies.py       # Auth dependencies
│   └── middleware.py         # Error handling
├── config.py                  # Configuration
├── dependencies.py            # DI container
└── logging_config.py          # Logging setup
```

### Frontend Structure

```
frontend/src/app/
├── core/                      # Core module
│   ├── services/             # Shared services
│   ├── guards/               # Route guards
│   └── interceptors/         # HTTP interceptors
├── features/                  # Feature modules
│   ├── topology/             # Topology management
│   ├── services/             # Service provisioning
│   ├── analytics/            # Analytics dashboard
│   └── auth/                 # Authentication
└── shared/                    # Shared components
```

---

## Domain Models

### Device Hierarchy

All devices inherit from the abstract `Device` base class:

```python
from abc import ABC, abstractmethod
from src.models import DeviceType, DeviceStatus

class Device(ABC):
    def __init__(self, id: str, name: str, device_type: DeviceType, 
                 capacity: float, location: str = None):
        self.id = id
        self.name = name
        self.device_type = device_type
        self.capacity = capacity
        self.location = location
        self.status = DeviceStatus.ACTIVE
        self.utilization = 0.0
    
    @abstractmethod
    def provision(self, service: 'Service') -> bool:
        """Provision a service on this device"""
        pass
    
    @abstractmethod
    def calculate_available_capacity(self) -> float:
        """Calculate remaining capacity"""
        pass
```

### Creating a New Device Type

1. **Define the device class:**
   ```python
   # src/models/specialized_devices.py
   
   class MyNewDevice(Device):
       def __init__(self, id: str, name: str, capacity: float,
                    custom_param: int, location: str = None):
           super().__init__(id, name, DeviceType.MY_NEW_TYPE, 
                          capacity, location)
           self.custom_param = custom_param
       
       def provision(self, service: 'Service') -> bool:
           # Implement provisioning logic
           if service.bandwidth <= self.calculate_available_capacity():
               self.utilization += service.bandwidth
               return True
           return False
       
       def calculate_available_capacity(self) -> float:
           return self.capacity - self.utilization
   ```

2. **Add to DeviceType enum:**
   ```python
   # src/models/device.py
   
   class DeviceType(Enum):
       # ... existing types
       MY_NEW_TYPE = "MY_NEW_TYPE"
   ```

3. **Update factory function:**
   ```python
   # src/api/routes/topology.py
   
   def create_device_from_request(device_data: DeviceCreate) -> Device:
       # ... existing code
       elif device_type == DeviceType.MY_NEW_TYPE:
           return MyNewDevice(
               id=device_data.id,
               name=device_data.name,
               capacity=device_data.capacity,
               custom_param=device_data.custom_param,
               location=device_data.location
           )
   ```

---

## Repository Layer

### Neo4j Repository

The `Neo4jRepository` handles all graph database operations:

```python
from src.repositories.neo4j_repository import Neo4jRepository

# Initialize
repo = Neo4jRepository(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Create device
device = MPLSRouter("R1", "Router 1", 100.0)
repo.create_device(device)

# Find path
path = repo.find_shortest_path("R1", "R2")

# Get topology
topology = repo.get_topology_json()

# Clean up
repo.close()
```

### Adding New Repository Methods

```python
# src/repositories/neo4j_repository.py

def get_devices_by_type(self, device_type: str) -> List[Dict]:
    """Get all devices of a specific type"""
    with self.driver.session() as session:
        query = """
        MATCH (d:Device {type: $device_type})
        RETURN d
        """
        result = session.run(query, device_type=device_type)
        return [dict(record["d"]) for record in result]
```

---

## Service Layer

### Service Orchestrator

The `ServiceOrchestrator` coordinates service provisioning:

```python
from src.services.service_orchestrator import ServiceOrchestrator

orchestrator = ServiceOrchestrator(
    neo4j_repo=neo4j_repo,
    metrics_repo=metrics_repo,
    rule_engine=rule_engine
)

# Provision service
service = Service(
    id="S1",
    service_type=ServiceType.MPLS_VPN,
    source_device_id="R1",
    target_device_id="R2",
    bandwidth=5.0
)

success, message = orchestrator.provision_service(service)
```

### Rule Engine

Add custom validation rules:

```python
from src.services.rule_engine import RuleEngine, RuleCondition

rule_engine = RuleEngine()

# Add custom rule
rule_engine.add_rule(RuleCondition(
    rule_id="CUSTOM001",
    name="Custom Validation Rule",
    condition=lambda service, device, link: 
        service.bandwidth > 50.0,  # Reject if > 50 Gbps
    action="reject",
    priority=10
))

# Evaluate rules
is_valid, violations = rule_engine.evaluate(service, device, link)
```

---

## API Layer

### Creating New Endpoints

1. **Define Pydantic models:**
   ```python
   # src/api/models.py
   
   class MyRequest(BaseModel):
       field1: str
       field2: int
       
       class Config:
           json_schema_extra = {
               "example": {
                   "field1": "value",
                   "field2": 42
               }
           }
   ```

2. **Create route:**
   ```python
   # src/api/routes/my_routes.py
   
   from fastapi import APIRouter, Depends
   from src.dependencies import get_neo4j_repository
   
   router = APIRouter(prefix="/api/my-feature", tags=["My Feature"])
   
   @router.post("/action")
   async def my_action(
       request: MyRequest,
       repo: Neo4jRepository = Depends(get_neo4j_repository)
   ):
       # Implementation
       return {"success": True}
   ```

3. **Register router:**
   ```python
   # src/api/app.py
   
   from src.api.routes import my_routes
   app.include_router(my_routes.router)
   ```

### Dependency Injection

Use the dependency container for consistent component access:

```python
from fastapi import Depends
from src.dependencies import (
    get_neo4j_repository,
    get_service_orchestrator,
    get_auth_service
)

@router.post("/endpoint")
async def my_endpoint(
    orchestrator: ServiceOrchestrator = Depends(get_service_orchestrator)
):
    # Use orchestrator
    pass
```

---

## Frontend Development

### Creating New Components

1. **Generate component:**
   ```bash
   cd frontend
   ng generate component features/my-feature/my-component
   ```

2. **Implement component:**
   ```typescript
   // my-component.component.ts
   
   import { Component, OnInit } from '@angular/core';
   import { MyService } from '../../core/services/my.service';
   
   @Component({
     selector: 'app-my-component',
     templateUrl: './my-component.component.html',
     styleUrls: ['./my-component.component.scss']
   })
   export class MyComponentComponent implements OnInit {
     data: any[] = [];
     
     constructor(private myService: MyService) {}
     
     ngOnInit(): void {
       this.loadData();
     }
     
     loadData(): void {
       this.myService.getData().subscribe({
         next: (data) => this.data = data,
         error: (error) => console.error('Error:', error)
       });
     }
   }
   ```

### Creating Services

```typescript
// core/services/my.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MyService {
  private apiUrl = 'http://localhost:8000/api';
  
  constructor(private http: HttpClient) {}
  
  getData(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/my-endpoint`);
  }
}
```

---

## Testing

### Backend Testing

#### Unit Tests

```python
# tests/test_models/test_my_device.py

import pytest
from src.models.specialized_devices import MyNewDevice
from src.models import Service, ServiceType

def test_my_device_provision():
    device = MyNewDevice("D1", "Device 1", 100.0, custom_param=10)
    service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
    
    result = device.provision(service)
    
    assert result == True
    assert device.utilization == 50.0
```

#### Integration Tests

```python
# tests/test_api/test_my_endpoints.py

import pytest
from httpx import AsyncClient
from src.api.app import app

@pytest.mark.asyncio
async def test_my_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/my-feature/action",
            json={"field1": "value", "field2": 42}
        )
    
    assert response.status_code == 200
    assert response.json()["success"] == True
```

### Frontend Testing

```typescript
// my-component.component.spec.ts

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MyComponentComponent } from './my-component.component';
import { MyService } from '../../core/services/my.service';
import { of } from 'rxjs';

describe('MyComponentComponent', () => {
  let component: MyComponentComponent;
  let fixture: ComponentFixture<MyComponentComponent>;
  let mockService: jasmine.SpyObj<MyService>;
  
  beforeEach(async () => {
    mockService = jasmine.createSpyObj('MyService', ['getData']);
    
    await TestBed.configureTestingModule({
      declarations: [ MyComponentComponent ],
      providers: [
        { provide: MyService, useValue: mockService }
      ]
    }).compileComponents();
    
    fixture = TestBed.createComponent(MyComponentComponent);
    component = fixture.componentInstance;
  });
  
  it('should load data on init', () => {
    const mockData = [{ id: 1, name: 'Test' }];
    mockService.getData.and.returnValue(of(mockData));
    
    component.ngOnInit();
    
    expect(component.data).toEqual(mockData);
  });
});
```

---

## Extending the System

### Adding New Service Types

1. **Add to ServiceType enum:**
   ```python
   class ServiceType(Enum):
       # ... existing types
       MY_NEW_SERVICE = "MY_NEW_SERVICE"
   ```

2. **Update provisioning logic:**
   ```python
   # src/services/service_orchestrator.py
   
   def provision_service(self, service: Service) -> tuple[bool, str]:
       if service.service_type == ServiceType.MY_NEW_SERVICE:
           # Custom provisioning logic
           pass
   ```

### Adding New Validation Rules

```python
# config/custom_rules.py

from src.services.rule_engine import RuleCondition

def get_custom_rules():
    return [
        RuleCondition(
            rule_id="CUSTOM001",
            name="My Custom Rule",
            condition=lambda service, device, link: 
                # Your validation logic
                True,
            action="reject",
            priority=5
        )
    ]
```

---

## Best Practices

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Follow Angular style guide
- **Naming**: Use descriptive names, avoid abbreviations
- **Comments**: Document complex logic, not obvious code

### Error Handling

```python
# Good
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(
        status_code=500,
        detail={"error": {"code": "OPERATION_FAILED", "message": str(e)}}
    )

# Bad
try:
    result = risky_operation()
except:
    pass
```

### Logging

```python
from src.logging_config import get_logger

logger = get_logger(__name__)

# Log at appropriate levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

### Database Operations

- Always use parameterized queries
- Close connections properly
- Use transactions for multi-step operations
- Handle connection failures gracefully

### Testing

- Write tests for all new features
- Aim for >80% code coverage
- Use meaningful test names
- Test edge cases and error conditions

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Angular Documentation](https://angular.io/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## Getting Help

- Check the API documentation at `/api/docs`
- Review existing code for patterns
- Open an issue on GitHub
- Contact the development team
