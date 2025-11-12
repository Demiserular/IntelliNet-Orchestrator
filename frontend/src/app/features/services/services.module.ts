import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ServicesViewComponent } from './services-view.component';
import { ServiceProvisionComponent } from './service-provision.component';

const routes: Routes = [
  {
    path: '',
    component: ServicesViewComponent
  },
  {
    path: 'provision',
    component: ServiceProvisionComponent
  }
];

@NgModule({
  declarations: [
    ServicesViewComponent,
    ServiceProvisionComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule.forChild(routes)
  ]
})
export class ServicesModule {}
