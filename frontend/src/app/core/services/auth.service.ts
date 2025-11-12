import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  username: string;
  role: string;
}

export interface UserInfo {
  username: string;
  role: string;
  email?: string;
  full_name?: string;
  disabled: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'intellinet_access_token';
  private readonly USER_KEY = 'intellinet_user_info';
  private readonly API_URL = environment.apiUrl !== undefined && environment.apiUrl !== null ? environment.apiUrl : 'http://localhost:8000';

  private currentUserSubject = new BehaviorSubject<UserInfo | null>(this.getUserFromStorage());
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) { }

  /**
   * Login with username and password
   */
  login(username: string, password: string): Observable<TokenResponse> {
    const loginRequest: LoginRequest = { username, password };

    return this.http.post<TokenResponse>(`${this.API_URL}/api/auth/login`, loginRequest)
      .pipe(
        tap(response => {
          this.setToken(response.access_token);
          const userInfo: UserInfo = {
            username: response.username,
            role: response.role,
            disabled: false
          };
          this.setUserInfo(userInfo);
          this.currentUserSubject.next(userInfo);
        })
      );
  }

  /**
   * Logout and clear stored credentials
   */
  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.currentUserSubject.next(null);
  }

  /**
   * Get current authentication token
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Set authentication token
   */
  private setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  /**
   * Get current user information
   */
  getCurrentUser(): UserInfo | null {
    return this.currentUserSubject.value;
  }

  /**
   * Get user info from storage
   */
  private getUserFromStorage(): UserInfo | null {
    const userJson = localStorage.getItem(this.USER_KEY);
    if (userJson) {
      try {
        return JSON.parse(userJson);
      } catch {
        return null;
      }
    }
    return null;
  }

  /**
   * Set user information
   */
  private setUserInfo(user: UserInfo): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  /**
   * Check if current user is admin
   */
  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.role === 'admin';
  }

  /**
   * Get current user information from API
   */
  getUserInfo(): Observable<UserInfo> {
    return this.http.get<UserInfo>(`${this.API_URL}/api/auth/me`)
      .pipe(
        tap(userInfo => {
          this.setUserInfo(userInfo);
          this.currentUserSubject.next(userInfo);
        })
      );
  }
}
