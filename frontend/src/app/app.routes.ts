import { Routes } from '@angular/router';
import { CreateOrderComponent } from './create-order/create-order.component';
import { ReadOrderComponent } from './read-order/read-order.component';

export const routes: Routes = [
  { path: '', redirectTo: 'create-order', pathMatch: 'full' },
  { path: 'create-order', component: CreateOrderComponent },
  { path: 'read-order', loadComponent: () => import('./read-order/read-order.component').then(m => m.ReadOrderComponent) }

];
