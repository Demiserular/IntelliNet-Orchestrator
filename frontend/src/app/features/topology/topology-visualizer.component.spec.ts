import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TopologyVisualizerComponent } from './topology-visualizer.component';
import { TopologyService } from '../../core/services/topology.service';
import { of, throwError } from 'rxjs';

describe('TopologyVisualizerComponent', () => {
  let component: TopologyVisualizerComponent;
  let fixture: ComponentFixture<TopologyVisualizerComponent>;
  let topologyService: jasmine.SpyObj<TopologyService>;

  const mockTopology = {
    devices: [
      { id: 'D1', name: 'Device 1', type: 'MPLS', capacity: 100, status: 'active' },
      { id: 'D2', name: 'Device 2', type: 'DWDM', capacity: 200, status: 'active' }
    ],
    links: [
      { id: 'L1', source: 'D1', target: 'D2', bandwidth: 50, type: 'fiber', latency: 5 }
    ]
  };

  beforeEach(async () => {
    const topologyServiceSpy = jasmine.createSpyObj('TopologyService', ['getTopology', 'deleteDevice']);

    await TestBed.configureTestingModule({
      declarations: [TopologyVisualizerComponent],
      imports: [HttpClientTestingModule],
      providers: [
        { provide: TopologyService, useValue: topologyServiceSpy }
      ]
    }).compileComponents();

    topologyService = TestBed.inject(TopologyService) as jasmine.SpyObj<TopologyService>;
    fixture = TestBed.createComponent(TopologyVisualizerComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load topology on init', () => {
    topologyService.getTopology.and.returnValue(of(mockTopology));
    
    component.ngOnInit();
    
    expect(topologyService.getTopology).toHaveBeenCalled();
    expect(component.loading).toBe(false);
  });

  it('should handle topology load error', () => {
    const errorMessage = 'Failed to load topology';
    topologyService.getTopology.and.returnValue(throwError(() => new Error(errorMessage)));
    
    component.loadTopology();
    
    expect(component.error).toBe(errorMessage);
    expect(component.loading).toBe(false);
  });

  it('should render Cytoscape graph', () => {
    topologyService.getTopology.and.returnValue(of(mockTopology));
    
    fixture.detectChanges();
    
    const cytoscapeContainer = fixture.nativeElement.querySelector('.cytoscape-container');
    expect(cytoscapeContainer).toBeTruthy();
  });
});
