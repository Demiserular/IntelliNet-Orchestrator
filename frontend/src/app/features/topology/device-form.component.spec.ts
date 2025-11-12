import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { DeviceFormComponent } from './device-form.component';
import { TopologyService } from '../../core/services/topology.service';
import { of, throwError } from 'rxjs';

describe('DeviceFormComponent', () => {
  let component: DeviceFormComponent;
  let fixture: ComponentFixture<DeviceFormComponent>;
  let topologyService: jasmine.SpyObj<TopologyService>;

  beforeEach(async () => {
    const topologyServiceSpy = jasmine.createSpyObj('TopologyService', ['createDevice']);

    await TestBed.configureTestingModule({
      declarations: [DeviceFormComponent],
      imports: [ReactiveFormsModule, HttpClientTestingModule],
      providers: [
        { provide: TopologyService, useValue: topologyServiceSpy }
      ]
    }).compileComponents();

    topologyService = TestBed.inject(TopologyService) as jasmine.SpyObj<TopologyService>;
    fixture = TestBed.createComponent(DeviceFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize form with empty values', () => {
    expect(component.deviceForm.get('id')?.value).toBe('');
    expect(component.deviceForm.get('name')?.value).toBe('');
    expect(component.deviceForm.get('type')?.value).toBe('');
    expect(component.deviceForm.get('capacity')?.value).toBe(0);
  });

  it('should validate required fields', () => {
    const form = component.deviceForm;
    
    expect(form.valid).toBeFalsy();
    
    form.patchValue({
      id: 'D1',
      name: 'Device 1',
      type: 'MPLS',
      capacity: 100
    });
    
    expect(form.valid).toBeTruthy();
  });

  it('should validate capacity minimum value', () => {
    const capacityControl = component.deviceForm.get('capacity');
    
    capacityControl?.setValue(-10);
    expect(capacityControl?.hasError('min')).toBeTruthy();
    
    capacityControl?.setValue(10);
    expect(capacityControl?.hasError('min')).toBeFalsy();
  });

  it('should submit form with valid data', () => {
    const mockDevice = { id: 'D1', name: 'Device 1', type: 'MPLS', capacity: 100 };
    topologyService.createDevice.and.returnValue(of(mockDevice));
    
    component.deviceForm.patchValue(mockDevice);
    component.onSubmit();
    
    expect(topologyService.createDevice).toHaveBeenCalledWith(jasmine.objectContaining(mockDevice));
    expect(component.successMessage).toContain('created successfully');
  });

  it('should handle form submission error', () => {
    const errorMessage = 'Failed to create device';
    topologyService.createDevice.and.returnValue(throwError(() => new Error(errorMessage)));
    
    component.deviceForm.patchValue({
      id: 'D1',
      name: 'Device 1',
      type: 'MPLS',
      capacity: 100
    });
    component.onSubmit();
    
    expect(component.errorMessage).toBe(errorMessage);
  });

  it('should reset form', () => {
    component.deviceForm.patchValue({
      id: 'D1',
      name: 'Device 1',
      type: 'MPLS',
      capacity: 100
    });
    
    component.resetForm();
    
    expect(component.deviceForm.get('id')?.value).toBe('');
    expect(component.deviceForm.get('name')?.value).toBe('');
  });
});
