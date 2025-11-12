import { Component } from '@angular/core';

@Component({
  selector: 'app-analytics-view',
  template: `
    <div class="analytics-view">
      <app-analytics-dashboard></app-analytics-dashboard>
    </div>
  `,
  styles: [`
    .analytics-view {
      height: 100%;
      display: flex;
      flex-direction: column;
    }
  `]
})
export class AnalyticsViewComponent {}
