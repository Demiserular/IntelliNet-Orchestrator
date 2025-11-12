import { Component, OnInit, OnDestroy } from '@angular/core';
import { TopologyService, Device } from '../../core/services/topology.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-device-list',
  template: `
    <div class="device-list">
      <div class="header">
        <h2>Network Devices</h2>
        <div class="search-box">
          <input 
            type="text" 
            placeholder="Search devices..." 
            [(ngModel)]="searchTerm"
            (input)="filterDevices()"
            class="search-input"
          />
        </div>
      </div>

      <div class="error" *ngIf="error">{{ error }}</div>
      <div class="loading" *ngIf="loading">Loading devices...</div>

      <div class="device-grid" *ngIf="!loading && !error">
        <div class="device-card" *ngFor="let device of filteredDevices">
          <div class="device-header">
            <h3>{{ device.name }}</h3>
            <span class="status-badge" [class]="device.status">{{ device.status }}</span>
          </div>
          <div class="device-details">
            <p><strong>ID:</strong> {{ device.id }}</p>
            <p><strong>Type:</strong> {{ device.type }}</p>
            <p><strong>Capacity:</strong> {{ device.capacity }} Gbps</p>
            <p *ngIf="device.location"><strong>Location:</strong> {{ device.location }}</p>
            <p *ngIf="device.utilization !== undefined">
              <strong>Utilization:</strong> {{ (device.utilization * 100).toFixed(1) }}%
            </p>
          </div>
          <div class="device-actions">
            <button class="btn btn-danger" (click)="deleteDevice(device.id)">Delete</button>
          </div>
        </div>
      </div>

      <div class="empty-state" *ngIf="!loading && !error && filteredDevices.length === 0">
        <p>No devices found</p>
      </div>
    </div>
  `,
  styles: [`
    .device-list {
      padding: 20px;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .header h2 {
      margin: 0;
      color: #333;
    }

    .search-box {
      flex: 0 0 300px;
    }

    .search-input {
      width: 100%;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
    }

    .error {
      padding: 15px;
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

    .device-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
    }

    .device-card {
      background-color: white;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      transition: box-shadow 0.3s;
    }

    .device-card:hover {
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }

    .device-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      padding-bottom: 10px;
      border-bottom: 1px solid #eee;
    }

    .device-header h3 {
      margin: 0;
      color: #1976d2;
      font-size: 18px;
    }

    .status-badge {
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      text-transform: uppercase;
    }

    .status-badge.active {
      background-color: #c8e6c9;
      color: #2e7d32;
    }

    .status-badge.inactive {
      background-color: #e0e0e0;
      color: #616161;
    }

    .status-badge.maintenance {
      background-color: #ffe0b2;
      color: #e65100;
    }

    .status-badge.failed {
      background-color: #ffcdd2;
      color: #c62828;
    }

    .device-details p {
      margin: 8px 0;
      font-size: 14px;
      color: #666;
    }

    .device-actions {
      margin-top: 15px;
      padding-top: 15px;
      border-top: 1px solid #eee;
    }

    .btn {
      padding: 8px 16px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      transition: background-color 0.3s;
    }

    .btn-danger {
      background-color: #f44336;
      color: white;
    }

    .btn-danger:hover {
      background-color: #d32f2f;
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: #999;
    }

    .empty-state p {
      font-size: 18px;
      margin: 0;
    }
  `]
})
export class DeviceListComponent implements OnInit, OnDestroy {
  devices: Device[] = [];
  filteredDevices: Device[] = [];
  searchTerm = '';
  loading = false;
  error: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(private topologyService: TopologyService) {}

  ngOnInit(): void {
    this.loadDevices();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadDevices(): void {
    this.loading = true;
    this.error = null;

    this.topologyService.getTopology()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (topology) => {
          this.devices = topology.devices;
          this.filteredDevices = [...this.devices];
          this.loading = false;
        },
        error: (err) => {
          this.error = err.message || 'Failed to load devices';
          this.loading = false;
        }
      });
  }

  filterDevices(): void {
    const term = this.searchTerm.toLowerCase().trim();
    if (!term) {
      this.filteredDevices = [...this.devices];
      return;
    }

    this.filteredDevices = this.devices.filter(device =>
      device.name.toLowerCase().includes(term) ||
      device.id.toLowerCase().includes(term) ||
      device.type.toLowerCase().includes(term) ||
      (device.location && device.location.toLowerCase().includes(term))
    );
  }

  deleteDevice(deviceId: string): void {
    if (!confirm('Are you sure you want to delete this device?')) {
      return;
    }

    this.topologyService.deleteDevice(deviceId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.loadDevices();
        },
        error: (err) => {
          this.error = err.message || 'Failed to delete device';
        }
      });
  }
}
