import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface Device {
  id: string;
  name: string;
  type: string;
  capacity: number;
  location?: string;
  status?: string;
  utilization?: number;
}

export interface Link {
  id: string;
  source: string;
  target: string;
  bandwidth: number;
  type: string;
  latency: number;
  utilization?: number;
  status?: string;
}

export interface Topology {
  devices: Device[];
  links: Link[];
}

@Injectable({
  providedIn: 'root'
})
export class TopologyService {
  private apiUrl = environment.apiUrl !== undefined && environment.apiUrl !== null ? environment.apiUrl + '/api' : 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  /**
   * Get complete network topology
   */
  getTopology(): Observable<Topology> {
    return this.http.get<Topology>(`${this.apiUrl}/topology/`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Create a new network device
   */
  createDevice(device: Partial<Device>): Observable<Device> {
    return this.http.post<Device>(`${this.apiUrl}/topology/device`, device)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Get a specific device by ID
   */
  getDevice(deviceId: string): Observable<Device> {
    return this.http.get<Device>(`${this.apiUrl}/topology/device/${deviceId}`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Update device properties
   */
  updateDevice(deviceId: string, updates: Partial<Device>): Observable<Device> {
    return this.http.put<Device>(`${this.apiUrl}/topology/device/${deviceId}`, updates)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Delete a device
   */
  deleteDevice(deviceId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/topology/device/${deviceId}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Create a link between devices
   */
  createLink(link: Partial<Link>): Observable<Link> {
    return this.http.post<Link>(`${this.apiUrl}/topology/link`, link)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Delete a link
   */
  deleteLink(linkId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/topology/link/${linkId}`)
      .pipe(
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

    console.error('TopologyService error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
