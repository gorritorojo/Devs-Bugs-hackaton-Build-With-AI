import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DialogModule } from 'primeng/dialog';
import { InputNumberModule } from 'primeng/inputnumber';
import { ProgressBarModule } from 'primeng/progressbar';
import { RippleModule } from 'primeng/ripple';
import { TagModule } from 'primeng/tag';
import type { Lot } from '../../core/models';
import { MarketService } from '../../core/services/market.service';
import { timeRemaining } from '../../core/time-remaining';

@Component({
    selector: 'app-marketplace',
    templateUrl: './marketplace.component.html',
    imports: [
        FormsModule,
        ButtonModule,
        RippleModule,
        TagModule,
        ProgressBarModule,
        DialogModule,
        InputNumberModule,
    ],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MarketplaceComponent {
    marketService = inject(MarketService);
    private readonly messageService = inject(MessageService);
    private readonly router = inject(Router);

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

    deadlineInfo(lot: Lot) {
        return timeRemaining(lot.deadline);
    }

    goToDetail(id: string) {
        this.router.navigate(['/pyme/marketplace', id]);
    }

    openCommitDialog(lot: Lot, event: Event) {
        event.stopPropagation();
        if (this.isFull(lot)) {
            return;
        }
        this.selectedLot = lot;
        this.commitKilos = 0;
        this.commitDialogVisible = true;
    }

    confirmCommit() {
        if (!this.selectedLot || this.commitKilos <= 0) {
            return;
        }
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
