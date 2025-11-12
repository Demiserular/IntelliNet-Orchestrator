import { Component, OnInit, OnDestroy, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import cytoscape, { Core, NodeSingular } from 'cytoscape';
import { TopologyService, Topology, Device, Link } from '../../core/services/topology.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-topology-visualizer',
  template: `
    <div class="topology-visualizer">
      <div class="toolbar">
        <button (click)="loadTopology()" class="btn btn-primary">Refresh Topology</button>
        <button (click)="fitGraph()" class="btn btn-secondary">Fit to Screen</button>
        <button (click)="resetZoom()" class="btn btn-secondary">Reset Zoom</button>
        <div class="status" *ngIf="loading">Loading...</div>
        <div class="status error" *ngIf="error">{{ error }}</div>
      </div>
      <div class="legend">
        <div class="legend-item">
          <span class="legend-color active"></span>
          <span>Active</span>
        </div>
        <div class="legend-item">
          <span class="legend-color inactive"></span>
          <span>Inactive</span>
        </div>
        <div class="legend-item">
          <span class="legend-color maintenance"></span>
          <span>Maintenance</span>
        </div>
        <div class="legend-item">
          <span class="legend-color failed"></span>
          <span>Failed</span>
        </div>
      </div>
      <div #cytoscapeContainer class="cytoscape-container"></div>
      <div class="node-info" *ngIf="selectedNode">
        <h3>{{ selectedNode.name }}</h3>
        <p><strong>ID:</strong> {{ selectedNode.id }}</p>
        <p><strong>Type:</strong> {{ selectedNode.type }}</p>
        <p><strong>Capacity:</strong> {{ selectedNode.capacity }} Gbps</p>
        <p><strong>Status:</strong> {{ selectedNode.status }}</p>
        <p *ngIf="selectedNode.utilization !== undefined">
          <strong>Utilization:</strong> {{ (selectedNode.utilization * 100).toFixed(1) }}%
        </p>
        <p *ngIf="selectedNode.location"><strong>Location:</strong> {{ selectedNode.location }}</p>
      </div>
    </div>
  `,
  styles: [`
    .topology-visualizer {
      display: flex;
      flex-direction: column;
      height: 100%;
      position: relative;
    }

    .toolbar {
      display: flex;
      gap: 10px;
      padding: 15px;
      background-color: white;
      border-bottom: 1px solid #ddd;
      align-items: center;
    }

    .btn {
      padding: 8px 16px;
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

    .btn-secondary {
      background-color: #757575;
      color: white;
    }

    .btn-secondary:hover {
      background-color: #616161;
    }

    .status {
      margin-left: auto;
      padding: 8px 16px;
      border-radius: 4px;
      background-color: #e3f2fd;
      color: #1976d2;
    }

    .status.error {
      background-color: #ffebee;
      color: #c62828;
    }

    .legend {
      position: absolute;
      top: 80px;
      right: 20px;
      background-color: white;
      padding: 15px;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      z-index: 10;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 8px;
    }

    .legend-item:last-child {
      margin-bottom: 0;
    }

    .legend-color {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      border: 2px solid #333;
    }

    .legend-color.active {
      background-color: #4caf50;
    }

    .legend-color.inactive {
      background-color: #9e9e9e;
    }

    .legend-color.maintenance {
      background-color: #ff9800;
    }

    .legend-color.failed {
      background-color: #f44336;
    }

    .cytoscape-container {
      flex: 1;
      background-color: #fafafa;
      min-height: 500px;
      height: 100%;
    }

    .node-info {
      position: absolute;
      bottom: 20px;
      left: 20px;
      background-color: white;
      padding: 15px;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      min-width: 250px;
      z-index: 10;
    }

    .node-info h3 {
      margin: 0 0 10px 0;
      color: #1976d2;
    }

    .node-info p {
      margin: 5px 0;
      font-size: 14px;
    }
  `]
})
export class TopologyVisualizerComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('cytoscapeContainer', { static: true }) cytoscapeContainer!: ElementRef;

  private cy: Core | null = null;
  private destroy$ = new Subject<void>();

  loading = false;
  error: string | null = null;
  selectedNode: Device | null = null;

  constructor(private topologyService: TopologyService) { }

  ngOnInit(): void {
    // Don't initialize here, wait for AfterViewInit
  }

  ngAfterViewInit(): void {
    // Use setTimeout to ensure the view is fully rendered
    setTimeout(() => {
      console.log('Initializing cytoscape after view init');
      this.initializeCytoscape();
      this.loadTopology();
    }, 100);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.cy) {
      this.cy.destroy();
    }
  }

  private initializeCytoscape(): void {
    const container = this.cytoscapeContainer.nativeElement;
    console.log('Container dimensions:', {
      width: container.clientWidth,
      height: container.clientHeight,
      offsetWidth: container.offsetWidth,
      offsetHeight: container.offsetHeight
    });

    if (container.clientHeight === 0) {
      console.warn('Container height is 0, setting minimum height');
      container.style.minHeight = '500px';
      container.style.height = '100%';
    }

    this.cy = cytoscape({
      container: container,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'background-color': 'data(color)',
            'width': 60,
            'height': 60,
            'border-width': 3,
            'border-color': '#333',
            'font-size': 12,
            'color': '#000'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 3,
            'line-color': '#999',
            'target-arrow-color': '#999',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': 10,
            'text-rotation': 'autorotate',
            'text-margin-y': -10
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 5,
            'border-color': '#1976d2'
          }
        }
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 500
      }
    });

    // Add event listeners
    if (this.cy) {
      this.cy.on('tap', 'node', (event) => {
        const node = event.target;
        this.onNodeSelected(node);
      });

      this.cy.on('tap', (event) => {
        if (event.target === this.cy) {
          this.selectedNode = null;
        }
      });

      // Force resize after initialization
      setTimeout(() => {
        this.cy?.resize();
        this.cy?.fit(undefined, 50);
      }, 200);
    }
  }

  loadTopology(): void {
    this.loading = true;
    this.error = null;
    console.log('Loading topology...');

    this.topologyService.getTopology()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (topology) => {
          console.log('Topology loaded successfully:', topology);
          this.renderTopology(topology);
          this.loading = false;
        },
        error: (err) => {
          console.error('Error loading topology:', err);
          this.error = `Failed to load topology: ${err.message || err.status || 'Unknown error'}`;
          this.loading = false;
        }
      });
  }

  private renderTopology(topology: Topology): void {
    if (!this.cy) return;

    // Clear existing elements
    this.cy.elements().remove();

    // Add nodes
    const nodes = topology.devices.map(device => ({
      data: {
        id: device.id,
        label: device.name,
        color: this.getDeviceColor(device.status || 'active'),
        device: device
      }
    }));

    // Add edges
    const edges = topology.links.map(link => ({
      data: {
        id: link.id,
        source: link.source,
        target: link.target,
        label: `${link.bandwidth} Gbps`,
        link: link
      }
    }));

    this.cy.add([...nodes, ...edges]);

    // Apply layout
    this.cy.layout({
      name: 'cose',
      animate: true,
      animationDuration: 500,
      nodeRepulsion: 8000,
      idealEdgeLength: 100
    }).run();

    // Fit to screen
    this.fitGraph();
  }

  private getDeviceColor(status: string): string {
    const colorMap: { [key: string]: string } = {
      'active': '#4caf50',
      'inactive': '#9e9e9e',
      'maintenance': '#ff9800',
      'failed': '#f44336'
    };
    return colorMap[status.toLowerCase()] || '#9e9e9e';
  }

  private onNodeSelected(node: NodeSingular): void {
    const device = node.data('device') as Device;
    this.selectedNode = device;
  }

  fitGraph(): void {
    if (this.cy) {
      this.cy.fit(undefined, 50);
    }
  }

  resetZoom(): void {
    if (this.cy) {
      this.cy.zoom(1);
      this.cy.center();
    }
  }
}
