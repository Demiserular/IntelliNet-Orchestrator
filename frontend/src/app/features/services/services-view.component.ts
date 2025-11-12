import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { ServiceProvisionService, Service } from '../../core/services/service-provision.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-services-view',
  template: `
    <div class="services-view">
      <div class="header">
        <h1>Service Management</h1>
        <button (click)="navigateToProvision()" class="btn btn-primary">
          <span class="icon">➕</span> Provision New Service
        </button>
      </div>

      <div class="error" *ngIf="error">
        <strong>Error:</strong> {{ error }}
      </div>

      <div class="loading" *ngIf="loading">
        Loading services...
      </div>

      <div class="services-stats" *ngIf="!loading && services.length > 0">
        <div class="stat-card">
          <h3>{{ services.length }}</h3>
          <p>Total Services</p>
        </div>
        <div class="stat-card">
          <h3>{{ getActiveServicesCount() }}</h3>
          <p>Active Services</p>
        </div>
        <div class="stat-card">
          <h3>{{ getTotalBandwidth() }} Gbps</h3>
          <p>Total Bandwidth</p>
        </div>
      </div>

      <div class="services-table" *ngIf="!loading && services.length > 0">
        <table>
          <thead>
            <tr>
              <th>Service ID</th>
              <th>Type</th>
              <th>Source</th>
              <th>Target</th>
              <th>Bandwidth</th>
              <th>Status</th>
              <th>Path</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let service of services">
              <td><strong>{{ service.id }}</strong></td>
              <td>
                <span class="service-type">{{ formatServiceType(service.service_type) }}</span>
              </td>
              <td>{{ service.source_device_id }}</td>
              <td>{{ service.target_device_id }}</td>
              <td>{{ service.bandwidth }} Gbps</td>
              <td>
                <span class="status-badge" [ngClass]="'status-' + service.status">
                  {{ service.status }}
                </span>
              </td>
              <td>
                <span class="path-info" *ngIf="service.path && service.path.length > 0">
                  {{ service.path.length }} hops
                </span>
                <span class="path-info" *ngIf="!service.path || service.path.length === 0">
                  No path
                </span>
              </td>
              <td>
                <button class="btn-icon" (click)="viewServiceDetails(service)" title="View Details">
                  👁️
                </button>
                <button class="btn-icon" (click)="decommissionService(service.id)" 
                        title="Decommission"
                        *ngIf="service.status === 'active'">
                  ⛔
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="empty-state" *ngIf="!loading && services.length === 0">
        <div class="empty-icon">📦</div>
        <h2>No Services Found</h2>
        <p>Get started by provisioning your first network service</p>
        <button (click)="navigateToProvision()" class="btn btn-primary">
          Provision Service
        </button>
      </div>

      <!-- Service Details Modal -->
      <div class="modal" *ngIf="selectedService" (click)="closeModal()">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h2>Service Details: {{ selectedService.id }}</h2>
            <button class="close-btn" (click)="closeModal()">✕</button>
          </div>
          <div class="modal-body">
            <div class="detail-row">
              <span class="label">Service Type:</span>
              <span class="value">{{ formatServiceType(selectedService.service_type) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Source Device:</span>
              <span class="value">{{ selectedService.source_device_id }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Target Device:</span>
              <span class="value">{{ selectedService.target_device_id }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Bandwidth:</span>
              <span class="value">{{ selectedService.bandwidth }} Gbps</span>
            </div>
            <div class="detail-row" *ngIf="selectedService.latency_requirement">
              <span class="label">Latency Requirement:</span>
              <span class="value">{{ selectedService.latency_requirement }} ms</span>
            </div>
            <div class="detail-row">
              <span class="label">Status:</span>
              <span class="value">
                <span class="status-badge" [ngClass]="'status-' + selectedService.status">
                  {{ selectedService.status }}
                </span>
              </span>
            </div>
            <div class="detail-row" *ngIf="selectedService.path && selectedService.path.length > 0">
              <span class="label">Path:</span>
              <span class="value path-display">
                {{ selectedService.path.join(' → ') }}
              </span>
            </div>
            <div class="detail-row" *ngIf="selectedService.created_at">
              <span class="label">Created:</span>
              <span class="value">{{ formatDate(selectedService.created_at) }}</span>
            </div>
            <div class="detail-row" *ngIf="selectedService.activated_at">
              <span class="label">Activated:</span>
              <span class="value">{{ formatDate(selectedService.activated_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .services-view {
      padding: 20px;
      max-width: 1400px;
      margin: 0 auto;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 30px;
    }

    .header h1 {
      margin: 0;
      color: #333;
    }

    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: background-color 0.3s;
    }

    .btn-primary {
      background-color: #1976d2;
      color: white;
    }

    .btn-primary:hover {
      background-color: #1565c0;
    }

    .icon {
      font-size: 16px;
    }

    .error {
      padding: 12px;
      background-color: #ffebee;
      color: #c62828;
      border-radius: 4px;
      margin-bottom: 20px;
    }

    .loading {
      text-align: center;
      padding: 40px;
      color: #666;
    }

    .services-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }

    .stat-card {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      text-align: center;
    }

    .stat-card h3 {
      margin: 0 0 8px 0;
      font-size: 2rem;
      color: #1976d2;
    }

    .stat-card p {
      margin: 0;
      color: #666;
      font-size: 0.9rem;
    }

    .services-table {
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      overflow: hidden;
    }

    table {
      width: 100%;
      border-collapse: collapse;
    }

    thead {
      background-color: #f5f5f5;
    }

    th {
      padding: 15px;
      text-align: left;
      font-weight: 600;
      color: #333;
      border-bottom: 2px solid #e0e0e0;
    }

    td {
      padding: 15px;
      border-bottom: 1px solid #f0f0f0;
    }

    tbody tr:hover {
      background-color: #fafafa;
    }

    .service-type {
      display: inline-block;
      padding: 4px 8px;
      background-color: #e3f2fd;
      color: #1976d2;
      border-radius: 4px;
      font-size: 0.85rem;
      font-weight: 500;
    }

    .status-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 0.85rem;
      font-weight: 500;
      text-transform: capitalize;
    }

    .status-active {
      background-color: #c8e6c9;
      color: #2e7d32;
    }

    .status-provisioning {
      background-color: #fff9c4;
      color: #f57f17;
    }

    .status-decommissioned {
      background-color: #ffcdd2;
      color: #c62828;
    }

    .status-failed {
      background-color: #ffebee;
      color: #c62828;
    }

    .path-info {
      color: #666;
      font-size: 0.9rem;
    }

    .btn-icon {
      background: none;
      border: none;
      cursor: pointer;
      font-size: 1.2rem;
      padding: 4px 8px;
      margin: 0 2px;
      transition: transform 0.2s;
    }

    .btn-icon:hover {
      transform: scale(1.2);
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .empty-icon {
      font-size: 4rem;
      margin-bottom: 20px;
    }

    .empty-state h2 {
      color: #333;
      margin-bottom: 10px;
    }

    .empty-state p {
      color: #666;
      margin-bottom: 30px;
    }

    /* Modal Styles */
    .modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.5);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
    }

    .modal-content {
      background: white;
      border-radius: 8px;
      max-width: 600px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px;
      border-bottom: 1px solid #e0e0e0;
    }

    .modal-header h2 {
      margin: 0;
      color: #333;
    }

    .close-btn {
      background: none;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: #666;
      padding: 0;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 4px;
    }

    .close-btn:hover {
      background-color: #f0f0f0;
    }

    .modal-body {
      padding: 20px;
    }

    .detail-row {
      display: flex;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
    }

    .detail-row:last-child {
      border-bottom: none;
    }

    .detail-row .label {
      font-weight: 600;
      color: #666;
      min-width: 180px;
    }

    .detail-row .value {
      flex: 1;
      color: #333;
    }

    .path-display {
      font-family: monospace;
      font-size: 0.9rem;
    }
  `]
})
export class ServicesViewComponent implements OnInit, OnDestroy {
  services: Service[] = [];
  loading = false;
  error: string | null = null;
  selectedService: Service | null = null;

  private destroy$ = new Subject<void>();

  constructor(
    private serviceProvisionService: ServiceProvisionService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadServices();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadServices(): void {
    this.loading = true;
    this.error = null;

    this.serviceProvisionService.getServices()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (services) => {
          this.services = services;
          this.loading = false;
        },
        error: (err) => {
          this.error = err.message || 'Failed to load services';
          this.loading = false;
        }
      });
  }

  navigateToProvision(): void {
    this.router.navigate(['/services/provision']);
  }

  viewServiceDetails(service: Service): void {
    this.selectedService = service;
  }

  closeModal(): void {
    this.selectedService = null;
  }

  decommissionService(serviceId: string): void {
    if (confirm(`Are you sure you want to decommission service ${serviceId}?`)) {
      this.serviceProvisionService.decommissionService(serviceId)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.loadServices(); // Reload the list
          },
          error: (err) => {
            this.error = err.message || 'Failed to decommission service';
          }
        });
    }
  }

  getActiveServicesCount(): number {
    return this.services.filter(s => s.status === 'active').length;
  }

  getTotalBandwidth(): number {
    return this.services.reduce((sum, s) => sum + (s.bandwidth || 0), 0);
  }

  formatServiceType(type: string): string {
    return type.replace(/_/g, ' ');
  }

  formatDate(dateString: string): string {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  }
}
