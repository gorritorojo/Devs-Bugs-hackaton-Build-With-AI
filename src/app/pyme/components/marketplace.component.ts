import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { MarketService } from '../../core/services/market.service';
import { Lot } from '../../core/models';

@Component({
  standalone: false,
  selector: 'app-marketplace',
  templateUrl: './marketplace.component.html',
})
export class MarketplaceComponent {
  marketService = inject(MarketService);
  private messageService = inject(MessageService);
  private router = inject(Router);

  commitDialogVisible = false;
  selectedLot: Lot | null = null;
  commitKilos = 0;

  progress(lot: Lot): number {
    return Math.round((lot.currentKilos / lot.targetKilos) * 100);
  }

  isFull(lot: Lot): boolean {
    return lot.currentKilos >= lot.targetKilos;
  }

  getRemaining(lot: Lot): number {
    return lot.targetKilos - lot.currentKilos;
  }

  goToDetail(id: string) {
    this.router.navigate(['/pyme/marketplace', id]);
  }

  openCommitDialog(lot: Lot, event: Event) {
    event.stopPropagation();
    if (this.isFull(lot)) return;
    this.selectedLot = lot;
    this.commitKilos = 0;
    this.commitDialogVisible = true;
  }

  confirmCommit() {
    if (!this.selectedLot || this.commitKilos <= 0) return;
    this.marketService.addCommitment(this.selectedLot.id, this.commitKilos);
    this.messageService.add({
      severity: 'success',
      summary: 'Compromiso confirmado',
      detail: `Has comprometido ${this.commitKilos} kg de ${this.selectedLot.product}. ¡Gracias por participar!`,
      life: 4000,
    });
    this.commitDialogVisible = false;
    this.selectedLot = null;
    this.commitKilos = 0;
  }
}
