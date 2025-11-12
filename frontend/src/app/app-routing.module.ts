import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './core/guards/auth.guard';

const routes: Routes = [
  {
    path: 'login',
    loadChildren: () =>
      import('./features/auth/auth.module').then((m) => m.AuthModule)
  },
  {
    path: 'topology',
    loadChildren: () =>
      import('./features/topology/topology.module').then((m) => m.TopologyModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'services',
    loadChildren: () =>
      import('./features/services/services.module').then((m) => m.ServicesModule),
    canActivate: [AuthGuard]
  },
  {
    path: 'analytics',
    loadChildren: () =>
      import('./features/analytics/analytics.module').then((m) => m.AnalyticsModule),
    canActivate: [AuthGuard]
  },
  {
    path: '',
    redirectTo: '/topology',
    pathMatch: 'full'
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
