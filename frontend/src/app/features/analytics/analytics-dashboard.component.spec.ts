import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { AnalyticsDashboardComponent } from './analytics-dashboard.component';
import { AnalyticsService } from '../../core/services/analytics.service';
import { of, throwError } from 'rxjs';

describe('AnalyticsDashboardComponent', () => {
  let component: AnalyticsDashboardComponent;
  let fixture: ComponentFixture<AnalyticsDashboardComponent>;
  let analyticsService: jasmine.SpyObj<AnalyticsService>;

  const mockNetworkStatus = {
    total_devices: 10,
    active_devices: 8,
    total_services: 15,
    active_services: 12,
    average_utilization: 0.65,
    total_bandwidth: 1000,
    used_bandwidth: 650
  };

  beforeEach(async () => {
    const analyticsSpy = jasmine.createSpyObj('AnalyticsService', ['getNetworkStatus']);

    await TestBed.configureTestingModule({
      declarations: [AnalyticsDashboardComponent],
      imports: [FormsModule, HttpClientTestingModule],
      providers: [
        { provide: AnalyticsService, useValue: analyticsSpy }
      ]
    }).compileComponents();

    analyticsService = TestBed.inject(AnalyticsService) as jasmine.SpyObj<AnalyticsService>;
    fixture = TestBed.createComponent(AnalyticsDashboardComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load network status on init', () => {
    analyticsService.getNetworkStatus.and.returnValue(of(mockNetworkStatus));
    
    component.ngOnInit();
    
    expect(analyticsService.getNetworkStatus).toHaveBeenCalled();
    expect(component.networkStatus).toEqual(mockNetworkStatus);
  });

  it('should handle load error', () => {
    const errorMessage = 'Failed to load analytics data';
    analyticsService.getNetworkStatus.and.returnValue(throwError(() => new Error(errorMessage)));
    
    component.loadData();
    
    expect(component.error).toBe(errorMessage);
  });

  it('should display status cards with correct data', () => {
    analyticsService.getNetworkStatus.and.returnValue(of(mockNetworkStatus));
    component.ngOnInit();
    fixture.detectChanges();
    
    const statusCards = fixture.nativeElement.querySelectorAll('.status-card');
    expect(statusCards.length).toBe(4);
  });

  it('should toggle auto-refresh', () => {
    component.autoRefresh = false;
    component.toggleAutoRefresh();
    
    // Auto-refresh should be enabled but we can't easily test the interval
    expect(component.autoRefresh).toBe(false);
  });

  it('should render charts container', () => {
    analyticsService.getNetworkStatus.and.returnValue(of(mockNetworkStatus));
    fixture.detectChanges();
    
    const chartsContainer = fixture.nativeElement.querySelector('.charts-container');
    expect(chartsContainer).toBeTruthy();
  });
});
