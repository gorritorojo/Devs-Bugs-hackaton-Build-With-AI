import { NgModule } from "@angular/core";
import { SharedModule } from "../shared/shared.module";
import { AgroRoutingModule } from "./agro-routing.module";
import { LotManagementComponent } from "./components/lot-management.component";
import { AIPredictorComponent } from "./components/ai-predictor.component";

@NgModule({
    declarations: [LotManagementComponent, AIPredictorComponent],
    imports: [SharedModule, AgroRoutingModule],
})
export class AgroModule {}
