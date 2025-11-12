import { Component, OnInit, OnDestroy, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { AnalyticsService, NetworkStatus } from '../../core/services/analytics.service';
import { Subject, takeUntil, interval } from 'rxjs';
import Plotly from 'plotly.js-dist-min';

@Component({
  selector: 'app-analytics-dashboard',
  template: `
    <div class="analytics-dashboard">
      <div class="header">
        <h1>Analytics Dashboard</h1>
        <div class="refresh-controls">
          <label>
            <input type="checkbox" [(ngModel)]="autoRefresh" (change)="toggleAutoRefresh()" />
            Auto-refresh (30s)
          </label>
          <button class="btn btn-primary" (click)="loadData()">Refresh Now</button>
        </div>
      </div>

      <div class="error" *ngIf="error">{{ error }}</div>

      <div class="status-cards" *ngIf="networkStatus">
        <div class="status-card">
          <div class="card-icon devices"></div>
          <div class="card-content">
            <h3>{{ networkStatus.active_devices }} / {{ networkStatus.total_devices }}</h3>
            <p>Active Devices</p>
          </div>
        </div>

        <div class="status-card">
          <div class="card-icon services"></div>
          <div class="card-content">
            <h3>{{ networkStatus.active_services }} / {{ networkStatus.total_services }}</h3>
            <p>Active Services</p>
          </div>
        </div>

        <div class="status-card">
          <div class="card-icon bandwidth"></div>
          <div class="card-content">
            <h3>{{ (networkStatus.average_utilization * 100).toFixed(1) }}%</h3>
            <p>Avg Utilization</p>
          </div>
        </div>

        <div class="status-card">
          <div class="card-icon capacity"></div>
          <div class="card-content">
            <h3>{{ networkStatus.used_bandwidth.toFixed(1) }} / {{ networkStatus.total_bandwidth.toFixed(1) }} Gbps</h3>
            <p>Bandwidth Usage</p>
          </div>
        </div>
      </div>

      <div class="charts-container">
        <div class="chart-card">
          <h2>Bandwidth Utilization Over Time</h2>
          <div #bandwidthChart class="chart"></div>
        </div>

        <div class="chart-card">
          <h2>Device Status Distribution</h2>
          <div #deviceStatusChart class="chart"></div>
        </div>

        <div class="chart-card">
          <h2>Service Type Distribution</h2>
          <div #serviceTypeChart class="chart"></div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .analytics-dashboard {
      padding: 20px;
      background-color: #f5f5f5;
      min-height: 100%;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 30px;
      background-color: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .header h1 {
      margin: 0;
      color: #333;
    }

    .refresh-controls {
      display: flex;
      align-items: center;
      gap: 15px;
    }

    .refresh-controls label {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
    }

    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      transition: background-color 0.3s;
    }

    .btn-primary {
      background-color: #1976d2;
      color: white;
    }

    .btn-primary:hover {
      background-color: #1565c0;
    }

    .error {
      padding: 15px;
      background-color: #ffebee;
      color: #c62828;
      border-radius: 4px;
      margin-bottom: 20px;
    }

    .status-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }

    .status-card {
      background-color: white;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      display: flex;
      align-items: center;
      gap: 15px;
    }

    .card-icon {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
    }

    .card-icon.devices {
      background-color: #e3f2fd;
      color: #1976d2;
    }

    .card-icon.services {
      background-color: #f3e5f5;
      color: #7b1fa2;
    }

    .card-icon.bandwidth {
      background-color: #e8f5e9;
      color: #388e3c;
    }

    .card-icon.capacity {
      background-color: #fff3e0;
      color: #f57c00;
    }

    .card-content h3 {
      margin: 0 0 5px 0;
      font-size: 24px;
      color: #333;
    }

    .card-content p {
      margin: 0;
      color: #666;
      font-size: 14px;
    }

    .charts-container {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 20px;
    }

    .chart-card {
      background-color: white;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .chart-card h2 {
      margin: 0 0 20px 0;
      font-size: 18px;
      color: #333;
    }

    .chart {
      width: 100%;
      height: 300px;
    }
  `]
})
export class AnalyticsDashboardComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('bandwidthChart', { static: false }) bandwidthChartRef!: ElementRef;
  @ViewChild('deviceStatusChart', { static: false }) deviceStatusChartRef!: ElementRef;
  @ViewChild('serviceTypeChart', { static: false }) serviceTypeChartRef!: ElementRef;

  networkStatus: NetworkStatus | null = null;
  autoRefresh = false;
  error: string | null = null;

  private destroy$ = new Subject<void>();
  private refreshInterval$ = new Subject<void>();

  constructor(private analyticsService: AnalyticsService) {}

  ngOnInit(): void {
    this.loadData();
  }

  ngAfterViewInit(): void {
    // Initialize charts after view is ready
    setTimeout(() => {
      this.renderCharts();
    }, 100);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.refreshInterval$.next();
    this.refreshInterval$.complete();
  }

  loadData(): void {
    this.error = null;

    this.analyticsService.getNetworkStatus()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (status) => {
          this.networkStatus = status;
          this.renderCharts();
        },
        error: (err) => {
          this.error = err.message || 'Failed to load analytics data';
          console.error('Error loading analytics:', err);
        }
      });
  }

  toggleAutoRefresh(): void {
    if (this.autoRefresh) {
      // Start auto-refresh every 30 seconds
      interval(30000)
        .pipe(takeUntil(this.refreshInterval$))
        .subscribe(() => {
          this.loadData();
        });
    } else {
      // Stop auto-refresh
      this.refreshInterval$.next();
    }
  }

  private renderCharts(): void {
    if (!this.networkStatus) return;

    this.renderBandwidthChart();
    this.renderDeviceStatusChart();
    this.renderServiceTypeChart();
  }

  private renderBandwidthChart(): void {
    if (!this.bandwidthChartRef) return;

    // Generate sample time series data (in real app, this would come from API)
    const now = new Date();
    const timestamps = [];
    const utilization = [];

    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 3600000);
      timestamps.push(time.toLocaleTimeString());
      // Generate sample data with some variation
      utilization.push(Math.random() * 30 + 40);
    }

    const data = [{
      x: timestamps,
      y: utilization,
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: '#1976d2', width: 2 },
      marker: { size: 6 }
    }];

    const layout: any = {
      margin: { t: 10, r: 10, b: 40, l: 50 },
      xaxis: { title: 'Time' },
      yaxis: { title: 'Utilization (%)', range: [0, 100] },
      showlegend: false
    };

    Plotly.newPlot(this.bandwidthChartRef.nativeElement, data as any, layout, { responsive: true });
  }

  private renderDeviceStatusChart(): void {
    if (!this.deviceStatusChartRef || !this.networkStatus) return;

    const data = [{
      values: [
        this.networkStatus.active_devices,
        this.networkStatus.total_devices - this.networkStatus.active_devices
      ],
      labels: ['Active', 'Inactive'],
      type: 'pie',
      marker: {
        colors: ['#4caf50', '#9e9e9e']
      }
    }];

    const layout: any = {
      margin: { t: 10, r: 10, b: 10, l: 10 },
      showlegend: true,
      legend: { orientation: 'h', y: -0.1 }
    };

    Plotly.newPlot(this.deviceStatusChartRef.nativeElement, data as any, layout, { responsive: true });
  }

  private renderServiceTypeChart(): void {
    if (!this.serviceTypeChartRef || !this.networkStatus) return;

    // Sample service type distribution
    const data = [{
      x: ['MPLS VPN', 'OTN Circuit', 'GPON Access', 'FTTH Service'],
      y: [12, 8, 15, 10],
      type: 'bar',
      marker: {
        color: ['#1976d2', '#7b1fa2', '#388e3c', '#f57c00']
      }
    }];

    const layout: any = {
      margin: { t: 10, r: 10, b: 60, l: 50 },
      xaxis: { title: 'Service Type' },
      yaxis: { title: 'Count' },
      showlegend: false
    };

    Plotly.newPlot(this.serviceTypeChartRef.nativeElement, data as any, layout, { responsive: true });
  }
}
