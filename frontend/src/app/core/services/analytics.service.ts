import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface DeviceMetric {
  timestamp: string;
  utilization: number;
  status: string;
}

export interface LinkMetric {
  timestamp: string;
  utilization: number;
  latency: number;
}

export interface ServiceLog {
  timestamp: string;
  service_id: string;
  event_type: string;
  details: string;
}

export interface NetworkStatus {
  total_devices: number;
  active_devices: number;
  total_services: number;
  active_services: number;
  average_utilization: number;
  total_bandwidth: number;
  used_bandwidth: number;
}

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  private apiUrl = environment.apiUrl ? environment.apiUrl + '/api' : '/api';

  constructor(private http: HttpClient) { }

  /**
   * Get overall network status and metrics
   */
  getNetworkStatus(): Observable<NetworkStatus> {
    return this.http.get<NetworkStatus>(`${this.apiUrl}/analytics/status`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Get device metrics history
   */
  getDeviceMetrics(deviceId: string, limit: number = 100): Observable<DeviceMetric[]> {
    return this.http.get<DeviceMetric[]>(`${this.apiUrl}/analytics/device/${deviceId}/metrics`, {
      params: { limit: limit.toString() }
    })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Get link metrics history
   */
  getLinkMetrics(linkId: string, limit: number = 100): Observable<LinkMetric[]> {
    return this.http.get<LinkMetric[]>(`${this.apiUrl}/analytics/link/${linkId}/metrics`, {
      params: { limit: limit.toString() }
    })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Get service logs
   */
  getServiceLogs(serviceId?: string, eventType?: string): Observable<ServiceLog[]> {
    let params: any = {};
    if (serviceId) params.service_id = serviceId;
    if (eventType) params.event_type = eventType;

    return this.http.get<ServiceLog[]>(`${this.apiUrl}/analytics/service-logs`, { params })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Get bandwidth utilization trends
   */
  getBandwidthTrends(timeRange: string = '24h'): Observable<{
    timestamps: string[];
    utilization: number[];
  }> {
    return this.http.get<{
      timestamps: string[];
      utilization: number[];
    }>(`${this.apiUrl}/analytics/bandwidth-trends`, {
      params: { time_range: timeRange }
    })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
      if (error.error?.error?.message) {
        errorMessage = error.error.error.message;
      }
    }

    console.error('AnalyticsService error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
