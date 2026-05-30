import type { Routes } from '@angular/router';
import { LoginComponent } from '../auth/login.component';
import { ImpactDashboardComponent } from './components/impact-dashboard.component';
import { LotDetailComponent } from './components/lot-detail.component';
import { MarketplaceComponent } from './components/marketplace.component';

export const pymeRoutes: Routes = [
    // {path: '/', component: }
    { path: 'marketplace', component: MarketplaceComponent },
    { path: 'marketplace/:id', component: LotDetailComponent },
    { path: 'impact', component: ImpactDashboardComponent },
    { path: '', component: LoginComponent },
];
