# IntelliNet Orchestrator - Frontend

Angular-based frontend for the IntelliNet Orchestrator network service orchestration system.

## Features Implemented

### 1. Project Structure and Routing
- Angular 16+ application with modular architecture
- Three feature modules: Topology, Services, Analytics
- Lazy-loaded routes for optimal performance
- Core module for shared services

### 2. API Service Layer
- **TopologyService**: Device and link management operations
- **ServiceProvisionService**: Service provisioning and path optimization
- **AnalyticsService**: Network metrics and analytics retrieval
- HTTP error handling with retry logic
- Environment-based API configuration

### 3. Topology Visualization
- Interactive network topology visualization using Cytoscape.js
- Real-time graph rendering from topology JSON
- Color-coded device status indicators (active, inactive, maintenance, failed)
- Zoom, pan, and node selection interactions
- Device information panel on selection

### 4. Device and Service Management UI
- **Device List Component**: Searchable device grid with filtering
- **Device Form Component**: Reactive form for device creation with validation
- **Service Provision Component**: Service provisioning form with path finding
- Form validation and error handling
- Success/error notifications

### 5. Analytics Dashboard
- Network status summary cards (devices, services, utilization, bandwidth)
- Interactive charts using Plotly.js:
  - Bandwidth utilization time series
  - Device status distribution (pie chart)
  - Service type distribution (bar chart)
- Auto-refresh capability (30-second intervals)
- Real-time metrics display

### 6. Component Tests
- Unit tests for all major components
- Service integration tests with mock data
- Form validation tests
- HTTP client testing with HttpClientTestingModule

## Technology Stack

- **Framework**: Angular 16+
- **Visualization**: Cytoscape.js (topology), Plotly.js (charts)
- **Forms**: Reactive Forms with validation
- **HTTP**: HttpClient with RxJS
- **Testing**: Jasmine, Karma

## Getting Started

### Prerequisites
- Node.js 16+ and npm
- Angular CLI 16+

### Installation
```bash
npm install
```

### Development Server
```bash
npm start
```
Navigate to `http://localhost:4200/`

### Build
```bash
npm run build
```
Build artifacts will be stored in the `dist/` directory.

### Running Tests
```bash
npm test
```

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── core/                    # Core module with shared services
│   │   │   └── services/            # API services
│   │   │       ├── topology.service.ts
│   │   │       ├── service-provision.service.ts
│   │   │       └── analytics.service.ts
│   │   ├── features/                # Feature modules
│   │   │   ├── topology/            # Topology management
│   │   │   │   ├── topology-visualizer.component.ts
│   │   │   │   ├── device-list.component.ts
│   │   │   │   └── device-form.component.ts
│   │   │   ├── services/            # Service provisioning
│   │   │   │   └── service-provision.component.ts
│   │   │   └── analytics/           # Analytics dashboard
│   │   │       └── analytics-dashboard.component.ts
│   │   ├── app-routing.module.ts    # Main routing configuration
│   │   └── app.module.ts            # Root module
│   ├── environments/                # Environment configurations
│   └── styles.scss                  # Global styles
└── package.json
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000/api` (configurable via environment files).

### Available Endpoints
- `GET /api/topology` - Get complete network topology
- `POST /api/topology/device` - Create a device
- `DELETE /api/topology/device/{id}` - Delete a device
- `POST /api/service/provision` - Provision a service
- `GET /api/optimization/path/{source}/{target}` - Find optimal path
- `GET /api/analytics/status` - Get network status

## Features by Route

### /topology
- Interactive network topology visualization
- Device management (list, create, delete)
- Real-time topology updates

### /services
- Service provisioning form
- Path optimization
- Service validation

### /analytics
- Network status overview
- Bandwidth utilization charts
- Device and service statistics
- Auto-refresh capability

## Development Notes

- All services use RxJS observables for async operations
- Error handling implemented at service and component levels
- Retry logic (2 retries) for GET requests
- TypeScript strict mode enabled
- Responsive design for various screen sizes

## Future Enhancements

- User authentication and authorization
- Real-time WebSocket updates
- Advanced filtering and search
- Export topology to various formats
- Service history and audit logs
- Performance optimization for large topologies
