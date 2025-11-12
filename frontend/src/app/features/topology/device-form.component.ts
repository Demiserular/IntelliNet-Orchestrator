import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { TopologyService } from '../../core/services/topology.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-device-form',
  template: `
    <div class="device-form">
      <h2>Create Network Device</h2>

      <div class="success" *ngIf="successMessage">{{ successMessage }}</div>
      <div class="error" *ngIf="errorMessage">{{ errorMessage }}</div>

      <form [formGroup]="deviceForm" (ngSubmit)="onSubmit()">
        <div class="form-group">
          <label for="id">Device ID *</label>
          <input 
            id="id" 
            type="text" 
            formControlName="id" 
            class="form-control"
            [class.invalid]="deviceForm.get('id')?.invalid && deviceForm.get('id')?.touched"
          />
          <div class="error-message" *ngIf="deviceForm.get('id')?.invalid && deviceForm.get('id')?.touched">
            Device ID is required
          </div>
        </div>

        <div class="form-group">
          <label for="name">Device Name *</label>
          <input 
            id="name" 
            type="text" 
            formControlName="name" 
            class="form-control"
            [class.invalid]="deviceForm.get('name')?.invalid && deviceForm.get('name')?.touched"
          />
          <div class="error-message" *ngIf="deviceForm.get('name')?.invalid && deviceForm.get('name')?.touched">
            Device name is required
          </div>
        </div>

        <div class="form-group">
          <label for="type">Device Type *</label>
          <select 
            id="type" 
            formControlName="type" 
            class="form-control"
            [class.invalid]="deviceForm.get('type')?.invalid && deviceForm.get('type')?.touched"
          >
            <option value="">Select a type</option>
            <option value="DWDM">DWDM</option>
            <option value="OTN">OTN</option>
            <option value="SONET">SONET</option>
            <option value="MPLS">MPLS</option>
            <option value="GPON_OLT">GPON OLT</option>
            <option value="GPON_ONT">GPON ONT</option>
            <option value="FTTH">FTTH</option>
          </select>
          <div class="error-message" *ngIf="deviceForm.get('type')?.invalid && deviceForm.get('type')?.touched">
            Device type is required
          </div>
        </div>

        <div class="form-group">
          <label for="capacity">Capacity (Gbps) *</label>
          <input 
            id="capacity" 
            type="number" 
            formControlName="capacity" 
            class="form-control"
            min="0"
            step="0.1"
            [class.invalid]="deviceForm.get('capacity')?.invalid && deviceForm.get('capacity')?.touched"
          />
          <div class="error-message" *ngIf="deviceForm.get('capacity')?.invalid && deviceForm.get('capacity')?.touched">
            <span *ngIf="deviceForm.get('capacity')?.errors?.['required']">Capacity is required</span>
            <span *ngIf="deviceForm.get('capacity')?.errors?.['min']">Capacity must be greater than 0</span>
          </div>
        </div>

        <div class="form-group">
          <label for="location">Location</label>
          <input 
            id="location" 
            type="text" 
            formControlName="location" 
            class="form-control"
          />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" [disabled]="deviceForm.invalid || submitting">
            {{ submitting ? 'Creating...' : 'Create Device' }}
          </button>
          <button type="button" class="btn btn-secondary" (click)="resetForm()">
            Reset
          </button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .device-form {
      max-width: 600px;
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
  `]
})
export class DeviceFormComponent implements OnInit, OnDestroy {
  deviceForm: FormGroup;
  submitting = false;
  successMessage: string | null = null;
  errorMessage: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private topologyService: TopologyService
  ) {
    this.deviceForm = this.fb.group({
      id: ['', Validators.required],
      name: ['', Validators.required],
      type: ['', Validators.required],
      capacity: [0, [Validators.required, Validators.min(0.1)]],
      location: ['']
    });
  }

  ngOnInit(): void {}

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onSubmit(): void {
    if (this.deviceForm.invalid) {
      Object.keys(this.deviceForm.controls).forEach(key => {
        this.deviceForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.submitting = true;
    this.successMessage = null;
    this.errorMessage = null;

    const deviceData = this.deviceForm.value;

    this.topologyService.createDevice(deviceData)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (device) => {
          this.successMessage = `Device "${device.name}" created successfully!`;
          this.submitting = false;
          this.resetForm();
          
          // Clear success message after 5 seconds
          setTimeout(() => {
            this.successMessage = null;
          }, 5000);
        },
        error: (err) => {
          this.errorMessage = err.message || 'Failed to create device';
          this.submitting = false;
        }
      });
  }

  resetForm(): void {
    this.deviceForm.reset({
      id: '',
      name: '',
      type: '',
      capacity: 0,
      location: ''
    });
    this.errorMessage = null;
  }
}
