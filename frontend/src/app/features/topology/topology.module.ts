import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TopologyViewComponent } from './topology-view.component';
import { TopologyVisualizerComponent } from './topology-visualizer.component';
import { DeviceListComponent } from './device-list.component';
import { DeviceFormComponent } from './device-form.component';

const routes: Routes = [
  {
    path: '',
    component: TopologyViewComponent
  },
  {
    path: 'devices',
    component: DeviceListComponent
  },
  {
    path: 'devices/new',
    component: DeviceFormComponent
  }
];

@NgModule({
  declarations: [
    TopologyViewComponent,
    TopologyVisualizerComponent,
    DeviceListComponent,
    DeviceFormComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule.forChild(routes)
  ]
})
export class TopologyModule {}
