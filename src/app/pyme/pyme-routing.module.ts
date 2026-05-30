import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MarketplaceComponent } from './components/marketplace.component';
import { LotDetailComponent } from './components/lot-detail.component';
import { ImpactDashboardComponent } from './components/impact-dashboard.component';

const routes: Routes = [
  { path: 'marketplace', component: MarketplaceComponent },
  { path: 'marketplace/:id', component: LotDetailComponent },
  { path: 'impact', component: ImpactDashboardComponent },
  { path: '', redirectTo: 'marketplace', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class PymeRoutingModule {}
