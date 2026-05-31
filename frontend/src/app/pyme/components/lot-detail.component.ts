import {
    ChangeDetectionStrategy,
    Component,
    computed,
    type OnInit,
    signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { InputNumberModule } from 'primeng/inputnumber';
import { ProgressBarModule } from 'primeng/progressbar';
import { RippleModule } from 'primeng/ripple';
import { TagModule } from 'primeng/tag';
import { MarketService } from '../../core/services/market.service';
import { RoleService } from '../../core/services/role.service';
import { timeRemaining } from '../../core/time-remaining';

@Component({
    selector: 'app-lot-detail',
    templateUrl: './lot-detail.component.html',
    imports: [
        FormsModule,
        ButtonModule,
        RippleModule,
        TagModule,
        ProgressBarModule,
        InputNumberModule,
    ],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LotDetailComponent implements OnInit {
    lotId: string | null = null;
    commitKilos = 0;
    committing = signal(false);

    lot = computed(() => {
        const id = this.lotId;
        return id
            ? (this.marketService.lots().find((l) => l.id === id) ?? null)
            : null;
    });

    progress = computed(() => {
        const l = this.lot();
        return l ? Math.round((l.currentKilos / l.targetKilos) * 100) : 0;
    });

    isFull = computed(() => {
        const l = this.lot();
        return l ? l.currentKilos >= l.targetKilos : false;
    });

    remaining = computed(() => {
        const l = this.lot();
        return l ? l.targetKilos - l.currentKilos : 0;
    });

    deadlineInfo = computed(() => {
        const l = this.lot();
        return l ? timeRemaining(l.deadline) : null;
    });

    private readonly router: Router;
    private readonly marketService: MarketService;
    private readonly messageService: MessageService;
    private readonly roleService: RoleService;
    private readonly backRoute: string;

    constructor(
        route: ActivatedRoute,
        router: Router,
        marketService: MarketService,
        messageService: MessageService,
        roleService: RoleService
    ) {
        this.router = router;
        this.marketService = marketService;
        this.messageService = messageService;
        this.roleService = roleService;
        this.lotId = route.snapshot.paramMap.get('id');
        this.backRoute =
            route.snapshot.url[0]?.path === 'pyme'
                ? '/pyme/marketplace'
                : '/agro/lots';
    }

    ngOnInit(): void {
        if (this.lotId) {
            this.marketService.loadLot(this.lotId);
        }
    }

    goBack() {
        this.router.navigate([this.backRoute]);
    }

    async confirmCommit() {
        const l = this.lot();
        if (!l || this.commitKilos <= 0) {
            return;
        }
        this.committing.set(true);
        try {
            await this.marketService.commitToLot(
                l.id,
                this.commitKilos,
                this.roleService.userId()
            );
            this.messageService.add({
                severity: 'success',
                summary: 'Compromiso confirmado',
                detail: `Has comprometido ${this.commitKilos} kg de ${l.product}. ¡Gracias por apoyar a ${l.producer}!`,
                life: 4000,
            });
            this.commitKilos = 0;
        } catch {
            this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: 'No se pudo confirmar el compromiso.',
                life: 5000,
            });
        } finally {
            this.committing.set(false);
        }
    }
}
