import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface Service {
  id: string;
  service_type: string;
  source_device_id: string;
  target_device_id: string;
  bandwidth: number;
  latency_requirement?: number;
  status?: string;
  path?: string[];
  created_at?: string;
  activated_at?: string;
}

export interface ServiceProvisionRequest {
  id: string;
  service_type: string;
  source_device_id: string;
  target_device_id: string;
  bandwidth: number;
  latency_requirement?: number;
}

export interface ServiceProvisionResponse {
  success: boolean;
  message: string;
  service?: Service;
}

@Injectable({
  providedIn: 'root'
})
export class ServiceProvisionService {
  private apiUrl = environment.apiUrl !== undefined && environment.apiUrl !== null ? environment.apiUrl + '/api' : 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  /**
   * Provision a new network service
   */
  provisionService(request: ServiceProvisionRequest): Observable<ServiceProvisionResponse> {
    return this.http.post<ServiceProvisionResponse>(`${this.apiUrl}/service/provision`, request)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Get service details by ID
   */
  getService(serviceId: string): Observable<Service> {
    return this.http.get<Service>(`${this.apiUrl}/service/${serviceId}`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Get all services
   */
  getAllServices(): Observable<Service[]> {
    return this.http.get<Service[]>(`${this.apiUrl}/service`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Get all services (alias for getAllServices)
   */
  getServices(): Observable<Service[]> {
    return this.getAllServices();
  }

  /**
   * Decommission a service
   */
  decommissionService(serviceId: string): Observable<{ success: boolean; message: string }> {
    return this.http.delete<{ success: boolean; message: string }>(`${this.apiUrl}/service/${serviceId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Find optimal path between two devices
   */
  findOptimalPath(source: string, target: string): Observable<{
    path: string[];
    latency: number;
    available_bandwidth: number;
  }> {
    return this.http.get<{
      path: string[];
      latency: number;
      available_bandwidth: number;
    }>(`${this.apiUrl}/optimization/path/${source}/${target}`)
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

    console.error('ServiceProvisionService error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
