# IntelliNet Orchestrator API Documentation

## Overview

The IntelliNet Orchestrator API is a RESTful API built with FastAPI that provides comprehensive network service orchestration capabilities for telecommunication infrastructure.

**Base URL:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/api/docs` (Swagger UI)

**Alternative Documentation:** `http://localhost:8000/api/redoc` (ReDoc)

**OpenAPI Schema:** `http://localhost:8000/api/openapi.json`

## Authentication

The API uses JWT (JSON Web Token) based authentication. Include the token in the Authorization header for protected endpoints.

### Login

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

**Usage:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Using the Token

Include the token in subsequent requests:

```bash
curl -X GET http://localhost:8000/api/topology \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## API Endpoints

### Health Check

#### GET /health

Check if the API is running.

**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy",
  "service": "IntelliNet Orchestrator",
  "version": "1.0.0"
}
```

---

## Topology Management

### Create Device

#### POST /api/topology/device

Create a new network device in the topology.

**Authentication:** Admin role required

**Request Body:**
```json
{
  "id": "DEVICE001",
  "name": "Core Router 1",
  "type": "MPLS",
  "capacity": 100.0,
  "location": "Data Center A",
  "wavelengths": 80,
  "is_olt": true
}
```

**Field Descriptions:**
- `id` (string, required): Unique device identifier
- `name` (string, required): Human-readable device name
- `type` (string, required): Device type - one of: `DWDM`, `OTN`, `SONET`, `MPLS`, `GPON_OLT`, `GPON_ONT`, `FTTH`
- `capacity` (number, required): Device capacity in Gbps
- `location` (string, optional): Physical location
- `wavelengths` (integer, optional): Number of wavelengths (DWDM devices only)
- `is_olt` (boolean, optional): Whether device is OLT or ONT (GPON devices only)

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Device created successfully",
  "data": {
    "id": "DEVICE001",
    "name": "Core Router 1",
    "type": "MPLS"
  }
}
```

**Error Response (409 Conflict):**
```json
{
  "error": {
    "code": "DEVICE_EXISTS",
    "message": "Device with ID DEVICE001 already exists",
    "details": {
      "device_id": "DEVICE001"
    }
  }
}
```

**Example:**
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

### Create Link

#### POST /api/topology/link

Create a link between two devices.

**Authentication:** Admin role required

**Request Body:**
```json
{
  "id": "LINK001",
  "source_device_id": "DEVICE001",
  "target_device_id": "DEVICE002",
  "bandwidth": 10.0,
  "type": "fiber",
  "latency": 5.0
}
```

**Field Descriptions:**
- `id` (string, required): Unique link identifier
- `source_device_id` (string, required): Source device ID
- `target_device_id` (string, required): Target device ID
- `bandwidth` (number, required): Link bandwidth in Gbps
- `type` (string, required): Link type - one of: `fiber`, `ethernet`, `wireless`
- `latency` (number, optional): Link latency in milliseconds (default: 0.0)

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Link created successfully",
  "data": {
    "id": "LINK001",
    "source": "DEVICE001",
    "target": "DEVICE002"
  }
}
```

**Example:**
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

### Get Topology

#### GET /api/topology

Retrieve the complete network topology including all devices and links.

**Authentication:** User or Admin role required

**Response (200 OK):**
```json
{
  "devices": [
    {
      "id": "DEVICE001",
      "name": "Core Router 1",
      "type": "MPLS",
      "capacity": 100.0,
      "location": "Data Center A",
      "status": "active",
      "utilization": 0.0
    }
  ],
  "links": [
    {
      "id": "LINK001",
      "source": "DEVICE001",
      "target": "DEVICE002",
      "bandwidth": 10.0,
      "type": "fiber",
      "latency": 5.0,
      "utilization": 0.0,
      "status": "active"
    }
  ]
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/topology \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Device

#### GET /api/topology/device/{device_id}

Retrieve a specific device by ID.

**Authentication:** User or Admin role required

**Path Parameters:**
- `device_id` (string): Device identifier

**Response (200 OK):**
```json
{
  "id": "DEVICE001",
  "name": "Core Router 1",
  "type": "MPLS",
  "capacity": 100.0,
  "location": "Data Center A",
  "status": "active",
  "utilization": 0.0
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/topology/device/ROUTER01 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Delete Device

#### DELETE /api/topology/device/{device_id}

Delete a device and all its associated links.

**Authentication:** Admin role required

**Path Parameters:**
- `device_id` (string): Device identifier

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Device deleted successfully",
  "data": {
    "id": "DEVICE001"
  }
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/topology/device/ROUTER01 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Service Provisioning

### Provision Service

#### POST /api/service/provision

Provision a new network service.

**Authentication:** User or Admin role required

**Request Body:**
```json
{
  "id": "SERVICE001",
  "service_type": "MPLS_VPN",
  "source_device_id": "DEVICE001",
  "target_device_id": "DEVICE002",
  "bandwidth": 5.0,
  "latency_requirement": 10.0
}
```

**Field Descriptions:**
- `id` (string, required): Unique service identifier
- `service_type` (string, required): Service type - one of: `MPLS_VPN`, `OTN_CIRCUIT`, `GPON_ACCESS`, `FTTH_SERVICE`
- `source_device_id` (string, required): Source device ID
- `target_device_id` (string, required): Target device ID
- `bandwidth` (number, required): Required bandwidth in Gbps
- `latency_requirement` (number, optional): Maximum acceptable latency in milliseconds

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Service SERVICE001 provisioned successfully",
  "data": {
    "service_id": "SERVICE001",
    "status": "active",
    "path": ["DEVICE001", "DEVICE002"]
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed: BW001: Bandwidth Capacity Check",
    "details": {
      "violations": ["BW001: Bandwidth Capacity Check"],
      "requested_bandwidth": 50.0,
      "available_capacity": 30.0
    }
  }
}
```

**Example:**
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

### Get Service

#### GET /api/service/{service_id}

Retrieve a specific service by ID.

**Authentication:** User or Admin role required

**Path Parameters:**
- `service_id` (string): Service identifier

**Response (200 OK):**
```json
{
  "id": "SERVICE001",
  "service_type": "MPLS_VPN",
  "source": "DEVICE001",
  "target": "DEVICE002",
  "bandwidth": 5.0,
  "latency_requirement": 10.0,
  "status": "active",
  "path": ["DEVICE001", "DEVICE002"]
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/service/VPN001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Decommission Service

#### DELETE /api/service/{service_id}

Decommission an active service.

**Authentication:** User or Admin role required

**Path Parameters:**
- `service_id` (string): Service identifier

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Service decommissioned successfully",
  "data": {
    "service_id": "SERVICE001"
  }
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/service/VPN001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Analytics and Optimization

### Get Network Status

#### GET /api/analytics/status

Get aggregated network status and metrics.

**Authentication:** User or Admin role required

**Response (200 OK):**
```json
{
  "total_devices": 10,
  "active_devices": 9,
  "total_links": 15,
  "active_services": 5,
  "average_utilization": 45.5,
  "network_health": "healthy"
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/analytics/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Device Metrics

#### GET /api/analytics/device/{device_id}/metrics

Get historical metrics for a specific device.

**Authentication:** User or Admin role required

**Path Parameters:**
- `device_id` (string): Device identifier

**Query Parameters:**
- `limit` (integer, optional): Maximum number of records to return (default: 100)

**Response (200 OK):**
```json
{
  "device_id": "DEVICE001",
  "metrics": [
    {
      "timestamp": "2025-11-12T10:30:00Z",
      "utilization": 45.5,
      "status": "active"
    }
  ]
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/analytics/device/ROUTER01/metrics?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Find Optimal Path

#### GET /api/optimization/path/{source}/{target}

Find the optimal path between two devices considering utilization and latency.

**Authentication:** User or Admin role required

**Path Parameters:**
- `source` (string): Source device ID
- `target` (string): Target device ID

**Response (200 OK):**
```json
{
  "source": "DEVICE001",
  "target": "DEVICE002",
  "path": ["DEVICE001", "DEVICE003", "DEVICE002"],
  "total_latency": 15.5,
  "average_utilization": 35.2,
  "path_quality": "optimal"
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/optimization/path/ROUTER01/ROUTER05 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Error Responses

All error responses follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "additional": "context"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `INVALID_DEVICE_TYPE` | 400 | Invalid device type specified |
| `INVALID_LINK_TYPE` | 400 | Invalid link type specified |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `DEVICE_NOT_FOUND` | 404 | Device not found |
| `SERVICE_NOT_FOUND` | 404 | Service not found |
| `PATH_NOT_FOUND` | 404 | No path found between devices |
| `DEVICE_EXISTS` | 409 | Device already exists |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Rate Limiting

Currently, no rate limiting is implemented. This may be added in future versions.

---

## Versioning

The API is currently at version 1.0.0. Future versions will maintain backward compatibility or provide migration paths.

---

## Support

For issues or questions:
- Check the interactive API documentation at `/api/docs`
- Review the developer guide in the repository
- Open an issue on the project repository
