import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ServiceProvisionService } from '../../core/services/service-provision.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-service-provision',
  template: `
    <div class="service-provision">
      <h2>Provision Network Service</h2>

      <div class="success" *ngIf="successMessage">
        <strong>Success!</strong> {{ successMessage }}
      </div>
      <div class="error" *ngIf="errorMessage">
        <strong>Error:</strong> {{ errorMessage }}
      </div>

      <form [formGroup]="serviceForm" (ngSubmit)="onSubmit()">
        <div class="form-group">
          <label for="serviceId">Service ID *</label>
          <input 
            id="serviceId" 
            type="text" 
            formControlName="id" 
            class="form-control"
            placeholder="e.g., VPN-001"
            [class.invalid]="serviceForm.get('id')?.invalid && serviceForm.get('id')?.touched"
          />
          <div class="error-message" *ngIf="serviceForm.get('id')?.invalid && serviceForm.get('id')?.touched">
            Service ID is required
          </div>
        </div>

        <div class="form-group">
          <label for="serviceType">Service Type *</label>
          <select 
            id="serviceType" 
            formControlName="service_type" 
            class="form-control"
            [class.invalid]="serviceForm.get('service_type')?.invalid && serviceForm.get('service_type')?.touched"
          >
            <option value="">Select a service type</option>
            <option value="MPLS_VPN">MPLS VPN</option>
            <option value="OTN_CIRCUIT">OTN Circuit</option>
            <option value="GPON_ACCESS">GPON Access</option>
            <option value="FTTH_SERVICE">FTTH Service</option>
          </select>
          <div class="error-message" *ngIf="serviceForm.get('service_type')?.invalid && serviceForm.get('service_type')?.touched">
            Service type is required
          </div>
        </div>

        <div class="form-group">
          <label for="source">Source Device ID *</label>
          <input 
            id="source" 
            type="text" 
            formControlName="source_device_id" 
            class="form-control"
            placeholder="e.g., EDGE-R1"
            [class.invalid]="serviceForm.get('source_device_id')?.invalid && serviceForm.get('source_device_id')?.touched"
          />
          <div class="error-message" *ngIf="serviceForm.get('source_device_id')?.invalid && serviceForm.get('source_device_id')?.touched">
            Source device ID is required
          </div>
        </div>

        <div class="form-group">
          <label for="destination">Target Device ID *</label>
          <input 
            id="destination" 
            type="text" 
            formControlName="target_device_id" 
            class="form-control"
            placeholder="e.g., EDGE-R2"
            [class.invalid]="serviceForm.get('target_device_id')?.invalid && serviceForm.get('target_device_id')?.touched"
          />
          <div class="error-message" *ngIf="serviceForm.get('target_device_id')?.invalid && serviceForm.get('target_device_id')?.touched">
            Target device ID is required
          </div>
        </div>

        <div class="form-group">
          <label for="bandwidth">Bandwidth (Gbps) *</label>
          <input 
            id="bandwidth" 
            type="number" 
            formControlName="bandwidth" 
            class="form-control"
            min="0"
            step="0.1"
            placeholder="e.g., 10"
            [class.invalid]="serviceForm.get('bandwidth')?.invalid && serviceForm.get('bandwidth')?.touched"
          />
          <div class="error-message" *ngIf="serviceForm.get('bandwidth')?.invalid && serviceForm.get('bandwidth')?.touched">
            <span *ngIf="serviceForm.get('bandwidth')?.errors?.['required']">Bandwidth is required</span>
            <span *ngIf="serviceForm.get('bandwidth')?.errors?.['min']">Bandwidth must be greater than 0</span>
          </div>
        </div>

        <div class="form-group">
          <label for="latency">Latency Requirement (ms)</label>
          <input 
            id="latency" 
            type="number" 
            formControlName="latency_requirement" 
            class="form-control"
            min="0"
            step="0.1"
            placeholder="Optional"
          />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" [disabled]="serviceForm.invalid || submitting">
            {{ submitting ? 'Provisioning...' : 'Provision Service' }}
          </button>
          <button type="button" class="btn btn-secondary" (click)="resetForm()">
            Reset
          </button>
          <button type="button" class="btn btn-info" (click)="findPath()" [disabled]="!canFindPath()">
            Find Optimal Path
          </button>
        </div>
      </form>

      <div class="path-info" *ngIf="pathInfo">
        <h3>Optimal Path Found</h3>
        <p><strong>Path:</strong> {{ pathInfo.path.join(' → ') }}</p>
        <p><strong>Total Latency:</strong> {{ pathInfo.latency }} ms</p>
        <p><strong>Available Bandwidth:</strong> {{ pathInfo.available_bandwidth }} Gbps</p>
      </div>
    </div>
  `,
  styles: [`
    .service-provision {
      max-width: 700px;
      margin: 0 auto;
      padding: 20px;
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    h2 {
      margin: 0 0 20px 0;
      color: #333;
    }

    .success {
      padding: 12px;
      background-color: #c8e6c9;
      color: #2e7d32;
      border-radius: 4px;
      margin-bottom: 20px;
    }

    .error {
      padding: 12px;
      background-color: #ffebee;
      color: #c62828;
      border-radius: 4px;
      margin-bottom: 20px;
    }

    .form-group {
      margin-bottom: 20px;
    }

    label {
      display: block;
      margin-bottom: 5px;
      font-weight: 500;
      color: #555;
    }

    .form-control {
      width: 100%;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
      transition: border-color 0.3s;
    }

    .form-control:focus {
      outline: none;
      border-color: #1976d2;
    }

    .form-control.invalid {
      border-color: #f44336;
    }

    .error-message {
      margin-top: 5px;
      color: #f44336;
      font-size: 12px;
    }

    .form-actions {
      display: flex;
      gap: 10px;
      margin-top: 30px;
      flex-wrap: wrap;
    }

    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      transition: background-color 0.3s;
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-primary {
      background-color: #1976d2;
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      background-color: #1565c0;
    }

    .btn-secondary {
      background-color: #757575;
      color: white;
    }

    .btn-secondary:hover {
      background-color: #616161;
    }

    .btn-info {
      background-color: #0288d1;
      color: white;
    }

    .btn-info:hover:not(:disabled) {
      background-color: #0277bd;
    }

    .path-info {
      margin-top: 30px;
      padding: 20px;
      background-color: #e3f2fd;
      border-radius: 4px;
      border-left: 4px solid #1976d2;
    }

    .path-info h3 {
      margin: 0 0 15px 0;
      color: #1976d2;
    }

    .path-info p {
      margin: 8px 0;
      color: #555;
    }
  `]
})
export class ServiceProvisionComponent implements OnInit, OnDestroy {
  serviceForm: FormGroup;
  submitting = false;
  successMessage: string | null = null;
  errorMessage: string | null = null;
  pathInfo: { path: string[]; latency: number; available_bandwidth: number } | null = null;

  private destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private serviceProvisionService: ServiceProvisionService
  ) {
    this.serviceForm = this.fb.group({
      id: ['', Validators.required],
      service_type: ['', Validators.required],
      source_device_id: ['', Validators.required],
      target_device_id: ['', Validators.required],
      bandwidth: [0, [Validators.required, Validators.min(0.1)]],
      latency_requirement: [null]
    });
  }

  ngOnInit(): void { }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  canFindPath(): boolean {
    return !!(this.serviceForm.get('source_device_id')?.value && this.serviceForm.get('target_device_id')?.value);
  }

  findPath(): void {
    const source = this.serviceForm.get('source_device_id')?.value;
    const destination = this.serviceForm.get('target_device_id')?.value;

    if (!source || !destination) {
      return;
    }

    this.serviceProvisionService.findOptimalPath(source, destination)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (pathData) => {
          this.pathInfo = pathData;
          this.errorMessage = null;
        },
        error: (err) => {
          this.errorMessage = err.message || 'Failed to find path';
          this.pathInfo = null;
        }
      });
  }

  onSubmit(): void {
    if (this.serviceForm.invalid) {
      Object.keys(this.serviceForm.controls).forEach(key => {
        this.serviceForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.submitting = true;
    this.successMessage = null;
    this.errorMessage = null;

    const serviceData = this.serviceForm.value;

    this.serviceProvisionService.provisionService(serviceData)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          if (response.success) {
            this.successMessage = response.message;
            this.resetForm();

            // Clear success message after 5 seconds
            setTimeout(() => {
              this.successMessage = null;
            }, 5000);
          } else {
            this.errorMessage = response.message;
          }
          this.submitting = false;
        },
        error: (err) => {
          this.errorMessage = err.message || 'Failed to provision service';
          this.submitting = false;
        }
      });
  }

  resetForm(): void {
    this.serviceForm.reset({
      id: '',
      service_type: '',
      source_device_id: '',
      target_device_id: '',
      bandwidth: 0,
      latency_requirement: null
    });
    this.errorMessage = null;
    this.pathInfo = null;
  }
}
