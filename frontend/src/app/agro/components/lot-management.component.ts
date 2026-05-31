import {
    ChangeDetectionStrategy,
    Component,
    computed,
    inject,
    type OnInit,
    signal,
} from '@angular/core';
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
import { TagModule } from 'primeng/tag';
import { TooltipModule } from 'primeng/tooltip';
import type { Lot } from '../../core/models';
import { MarketService } from '../../core/services/market.service';
import { RoleService } from '../../core/services/role.service';
import { timeRemaining } from '../../core/time-remaining';

@Component({
    selector: 'app-lot-management',
    templateUrl: 'log-management.html',
    imports: [
        FormsModule,
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
    ],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LotManagementComponent implements OnInit {
    marketService = inject(MarketService);
    private readonly messageService = inject(MessageService);
    private readonly router = inject(Router);
    private readonly roleService = inject(RoleService);

    readonly hasUserProfile = computed(() => this.roleService.hasUserProfile());

    today = new Date();

    newLotDialogVisible = false;
    creating = signal(false);
    newLot = {
        product: '',
        producer: '',
        targetKilos: 0,
        basePrice: 0,
        deadline: null as Date | null,
    };

    ngOnInit(): void {
        const userId = this.roleService.userId();
        this.marketService.loadLots(true, userId ?? undefined);
    }

    progress(lot: Lot): number {
        return Math.round((lot.currentKilos / lot.targetKilos) * 100);
    }

    isFull(lot: Lot): boolean {
        return lot.currentKilos >= lot.targetKilos;
    }

    deadlineInfo(lot: Lot) {
        return timeRemaining(lot.deadline);
    }

    statusLabel(lot: Lot): string {
        switch (lot.status) {
            case 'completed':
                return 'Completado';
            case 'expired':
                return 'Expirado';
            case 'deactivated':
                return 'Desactivado';
            default:
                return 'Activo';
        }
    }

    statusSeverity(
        lot: Lot
    ): 'success' | 'info' | 'warn' | 'danger' | 'secondary' {
        switch (lot.status) {
            case 'completed':
                return 'success';
            case 'expired':
                return 'danger';
            case 'deactivated':
                return 'secondary';
            default:
                return 'info';
        }
    }

    goToPredict(lotId: string) {
        this.router.navigate(['/agro/predict'], {
            queryParams: { lotId },
        });
    }

    goToDetail(lotId: string) {
        this.router.navigate(['/agro/lots', lotId]);
    }

    showNewLotDialog() {
        if (!this.hasUserProfile()) {
            return;
        }
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

    async createLot() {
        if (!this.isNewLotValid()) {
            return;
        }
        this.creating.set(true);
        try {
            await this.marketService.createLot({
                product: this.newLot.product.trim(),
                producer: this.newLot.producer.trim(),
                targetKilos: this.newLot.targetKilos,
                basePrice: this.newLot.basePrice,
                deadline: (this.newLot.deadline as Date).toISOString(),
                createdBy: this.roleService.userId(),
            });
            this.messageService.add({
                severity: 'success',
                summary: 'Lote creado',
                detail: `El lote "${this.newLot.product}" ha sido creado exitosamente.`,
                life: 4000,
            });
            this.newLotDialogVisible = false;
        } catch {
            this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: 'No se pudo crear el lote.',
                life: 5000,
            });
        } finally {
            this.creating.set(false);
        }
    }

    async toggleVisibility(lot: Lot) {
        const userId = this.roleService.userId();
        if (!userId) {
            return;
        }
        const newStatus =
            lot.status === 'deactivated' ? 'active' : 'deactivated';
        try {
            await this.marketService.toggleLotStatus(lot.id, newStatus, userId);
            this.messageService.add({
                severity: 'success',
                summary:
                    newStatus === 'deactivated'
                        ? 'Lote ocultado'
                        : 'Lote visible',
                detail:
                    newStatus === 'deactivated'
                        ? `"${lot.product}" ya no es visible en el mercado.`
                        : `"${lot.product}" ahora es visible en el mercado.`,
                life: 3000,
            });
        } catch {
            this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: 'No se pudo cambiar la visibilidad del lote.',
                life: 5000,
            });
        }
    }
}
