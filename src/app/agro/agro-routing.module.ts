import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LotManagementComponent } from './components/lot-management.component';
import { AIPredictorComponent } from './components/ai-predictor.component';

const routes: Routes = [
  { path: 'lots', component: LotManagementComponent },
  { path: 'predict', component: AIPredictorComponent },
  { path: '', redirectTo: 'lots', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class AgroRoutingModule {}
