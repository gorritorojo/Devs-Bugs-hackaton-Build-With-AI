import type { Routes } from '@angular/router';
import { AIPredictorComponent } from './components/ai-predictor.component';
import { LotManagementComponent } from './components/lot-management.component';

export const agroRoutes: Routes = [
    { path: 'lots', component: LotManagementComponent },
    { path: 'predict', component: AIPredictorComponent },
    { path: '', redirectTo: 'lots', pathMatch: 'full' },
];
