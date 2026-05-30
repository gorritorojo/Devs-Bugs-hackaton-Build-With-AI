import { Component, inject } from "@angular/core";
import { Router } from "@angular/router";
import { MessageService } from "primeng/api";
import { MarketService } from "../../core/services/market.service";
import { Lot } from "../../core/models";

@Component({
  standalone: false,
  selector: "app-lot-management",
  templateUrl: "log-management.html",
})
export class LotManagementComponent {
  marketService = inject(MarketService);
  private messageService = inject(MessageService);
  private router = inject(Router);

  newLotDialogVisible = false;
  newLot = { product: "", producer: "", targetKilos: 0, basePrice: 0 };

  progress(lot: Lot): number {
    return Math.round((lot.currentKilos / lot.targetKilos) * 100);
  }

  goToPredict(_lotId: string) {
    this.router.navigate(["/agro/predict"]);
  }

  goToDetail(lotId: string) {
    this.router.navigate(["/pyme/marketplace", lotId]);
  }

  showNewLotDialog() {
    this.newLot = { product: "", producer: "", targetKilos: 0, basePrice: 0 };
    this.newLotDialogVisible = true;
  }

  isNewLotValid(): boolean {
    return (
      this.newLot.product.trim().length > 0 &&
      this.newLot.producer.trim().length > 0 &&
      this.newLot.targetKilos > 0 &&
      this.newLot.basePrice > 0
    );
  }

  createLot() {
    if (!this.isNewLotValid()) return;
    this.marketService.createLot({
      product: this.newLot.product.trim(),
      producer: this.newLot.producer.trim(),
      targetKilos: this.newLot.targetKilos,
      basePrice: this.newLot.basePrice,
    });
    this.messageService.add({
      severity: "success",
      summary: "Lote creado",
      detail: `El lote "${this.newLot.product}" ha sido creado exitosamente.`,
      life: 4000,
    });
    this.newLotDialogVisible = false;
  }
}
