import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ServiceProvisionComponent } from './service-provision.component';
import { ServiceProvisionService } from '../../core/services/service-provision.service';
import { of, throwError } from 'rxjs';

describe('ServiceProvisionComponent', () => {
  let component: ServiceProvisionComponent;
  let fixture: ComponentFixture<ServiceProvisionComponent>;
  let serviceProvisionService: jasmine.SpyObj<ServiceProvisionService>;

  beforeEach(async () => {
    const serviceSpy = jasmine.createSpyObj('ServiceProvisionService', [
      'provisionService',
      'findOptimalPath'
    ]);

    await TestBed.configureTestingModule({
      declarations: [ServiceProvisionComponent],
      imports: [ReactiveFormsModule, HttpClientTestingModule],
      providers: [
        { provide: ServiceProvisionService, useValue: serviceSpy }
      ]
    }).compileComponents();

    serviceProvisionService = TestBed.inject(ServiceProvisionService) as jasmine.SpyObj<ServiceProvisionService>;
    fixture = TestBed.createComponent(ServiceProvisionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize form with empty values', () => {
    expect(component.serviceForm.get('service_type')?.value).toBe('');
    expect(component.serviceForm.get('source')?.value).toBe('');
    expect(component.serviceForm.get('destination')?.value).toBe('');
    expect(component.serviceForm.get('bandwidth')?.value).toBe(0);
  });

  it('should validate required fields', () => {
    const form = component.serviceForm;
    
    expect(form.valid).toBeFalsy();
    
    form.patchValue({
      service_type: 'MPLS_VPN',
      source: 'R1',
      destination: 'R2',
      bandwidth: 10
    });
    
    expect(form.valid).toBeTruthy();
  });

  it('should provision service with valid data', () => {
    const mockResponse = { success: true, message: 'Service provisioned successfully' };
    serviceProvisionService.provisionService.and.returnValue(of(mockResponse));
    
    component.serviceForm.patchValue({
      service_type: 'MPLS_VPN',
      source: 'R1',
      destination: 'R2',
      bandwidth: 10
    });
    component.onSubmit();
    
    expect(serviceProvisionService.provisionService).toHaveBeenCalled();
    expect(component.successMessage).toBe(mockResponse.message);
  });

  it('should handle provisioning error', () => {
    const errorMessage = 'Failed to provision service';
    serviceProvisionService.provisionService.and.returnValue(throwError(() => new Error(errorMessage)));
    
    component.serviceForm.patchValue({
      service_type: 'MPLS_VPN',
      source: 'R1',
      destination: 'R2',
      bandwidth: 10
    });
    component.onSubmit();
    
    expect(component.errorMessage).toBe(errorMessage);
  });

  it('should find optimal path', () => {
    const mockPath = {
      path: ['R1', 'R3', 'R2'],
      latency: 15,
      available_bandwidth: 50
    };
    serviceProvisionService.findOptimalPath.and.returnValue(of(mockPath));
    
    component.serviceForm.patchValue({
      source: 'R1',
      destination: 'R2'
    });
    component.findPath();
    
    expect(serviceProvisionService.findOptimalPath).toHaveBeenCalledWith('R1', 'R2');
    expect(component.pathInfo).toEqual(mockPath);
  });

  it('should enable find path button when source and destination are set', () => {
    component.serviceForm.patchValue({
      source: '',
      destination: ''
    });
    expect(component.canFindPath()).toBeFalsy();
    
    component.serviceForm.patchValue({
      source: 'R1',
      destination: 'R2'
    });
    expect(component.canFindPath()).toBeTruthy();
  });
});
