import { NgModule } from '@angular/core';
import { SharedModule } from '../shared/shared.module';
import { PymeRoutingModule } from './pyme-routing.module';
import { MarketplaceComponent } from './components/marketplace.component';
import { LotDetailComponent } from './components/lot-detail.component';
import { ImpactDashboardComponent } from './components/impact-dashboard.component';

@NgModule({
  declarations: [MarketplaceComponent, LotDetailComponent, ImpactDashboardComponent],
  imports: [SharedModule, PymeRoutingModule],
})
export class PymeModule {}
