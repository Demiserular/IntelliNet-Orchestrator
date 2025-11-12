import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TopologyService } from './topology.service';

describe('TopologyService', () => {
  let service: TopologyService;
  let httpMock: HttpTestingController;
  const apiUrl = 'http://localhost:8000/api';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [TopologyService]
    });
    service = TestBed.inject(TopologyService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should get topology', () => {
    const mockTopology = {
      devices: [{ id: 'D1', name: 'Device 1', type: 'MPLS', capacity: 100 }],
      links: [{ id: 'L1', source: 'D1', target: 'D2', bandwidth: 50, type: 'fiber', latency: 5 }]
    };

    service.getTopology().subscribe(topology => {
      expect(topology).toEqual(mockTopology);
    });

    const req = httpMock.expectOne(`${apiUrl}/topology`);
    expect(req.request.method).toBe('GET');
    req.flush(mockTopology);
  });

  it('should create device', () => {
    const mockDevice = { id: 'D1', name: 'Device 1', type: 'MPLS', capacity: 100 };

    service.createDevice(mockDevice).subscribe(device => {
      expect(device).toEqual(mockDevice);
    });

    const req = httpMock.expectOne(`${apiUrl}/topology/device`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(mockDevice);
    req.flush(mockDevice);
  });

  it('should delete device', () => {
    const deviceId = 'D1';

    service.deleteDevice(deviceId).subscribe();

    const req = httpMock.expectOne(`${apiUrl}/topology/device/${deviceId}`);
    expect(req.request.method).toBe('DELETE');
    req.flush(null);
  });

  it('should handle HTTP errors', () => {
    service.getTopology().subscribe({
      next: () => fail('should have failed'),
      error: (error) => {
        expect(error.message).toContain('Error');
      }
    });

    const req = httpMock.expectOne(`${apiUrl}/topology`);
    req.flush('Error', { status: 500, statusText: 'Server Error' });
  });
});
