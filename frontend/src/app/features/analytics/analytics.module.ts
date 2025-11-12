import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AnalyticsViewComponent } from './analytics-view.component';
import { AnalyticsDashboardComponent } from './analytics-dashboard.component';

const routes: Routes = [
  {
    path: '',
    component: AnalyticsViewComponent
  }
];

@NgModule({
  declarations: [
    AnalyticsViewComponent,
    AnalyticsDashboardComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    RouterModule.forChild(routes)
  ]
})
export class AnalyticsModule {}
