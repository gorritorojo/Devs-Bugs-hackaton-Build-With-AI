import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DatePickerModule } from 'primeng/datepicker';
import { DialogModule } from 'primeng/dialog';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputNumberModule } from 'primeng/inputnumber';
import { InputTextModule } from 'primeng/inputtext';
import { ProgressBarModule } from 'primeng/progressbar';
import { RippleModule } from 'primeng/ripple';
import { TableModule } from 'primeng/table';
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import type { Lot } from '../../core/models';
import { MarketService } from '../../core/services/market.service';

@Component({
    selector: 'app-lot-management',
    templateUrl: 'log-management.html',
    imports: [
        FormsModule,
        TableModule,
        ProgressBarModule,
        TagModule,
        ButtonModule,
        RippleModule,
        TooltipModule,
        DialogModule,
        IconFieldModule,
        InputIconModule,
        InputTextModule,
        InputNumberModule,
        DatePickerModule,
        DatePipe,
    ],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LotManagementComponent {
    marketService = inject(MarketService);
    private readonly messageService = inject(MessageService);
    private readonly router = inject(Router);

    today = new Date();

    newLotDialogVisible = false;
    newLot = {
        product: '',
        producer: '',
        targetKilos: 0,
        basePrice: 0,
        deadline: null as Date | null,
    };

    progress(lot: Lot): number {
        return Math.round((lot.currentKilos / lot.targetKilos) * 100);
    }

    goToPredict(_lotId: string) {
        this.router.navigate(['/agro/predict']);
    }

    goToDetail(lotId: string) {
        this.router.navigate(['/pyme/marketplace', lotId]);
    }

    showNewLotDialog() {
        this.newLot = {
            product: '',
            producer: '',
            targetKilos: 0,
            basePrice: 0,
            deadline: null,
        };
        this.newLotDialogVisible = true;
    }

    isNewLotValid(): boolean {
        return (
            this.newLot.product.trim().length > 0 &&
            this.newLot.producer.trim().length > 0 &&
            this.newLot.targetKilos > 0 &&
            this.newLot.basePrice > 0 &&
            this.newLot.deadline instanceof Date
        );
    }

    createLot() {
        if (!this.isNewLotValid()) {
            return;
        }
        this.marketService.createLot({
            product: this.newLot.product.trim(),
            producer: this.newLot.producer.trim(),
            targetKilos: this.newLot.targetKilos,
            basePrice: this.newLot.basePrice,
            deadline: (this.newLot.deadline as Date).toISOString(),
        });
        this.messageService.add({
            severity: 'success',
            summary: 'Lote creado',
            detail: `El lote "${this.newLot.product}" ha sido creado exitosamente.`,
            life: 4000,
        });
        this.newLotDialogVisible = false;
    }
}
