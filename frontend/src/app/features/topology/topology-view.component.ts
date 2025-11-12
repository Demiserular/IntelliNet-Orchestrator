import { Component } from '@angular/core';

@Component({
  selector: 'app-topology-view',
  template: `
    <div class="topology-view">
      <app-topology-visualizer></app-topology-visualizer>
    </div>
  `,
  styles: [`
    .topology-view {
      height: 100%;
      display: flex;
      flex-direction: column;
    }
  `]
})
export class TopologyViewComponent {}
