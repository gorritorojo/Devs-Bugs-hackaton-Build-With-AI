import { Component, computed } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { MarketService } from '../../core/services/market.service';

@Component({
  standalone: false,
  selector: 'app-lot-detail',
  templateUrl: './lot-detail.component.html',
})
export class LotDetailComponent {
  lotId: string | null = null;
  commitKilos = 0;

  lot = computed(() => {
    const id = this.lotId;
    return id ? this.marketService.lots().find(l => l.id === id) ?? null : null;
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

  constructor(
    route: ActivatedRoute,
    private router: Router,
    private marketService: MarketService,
    private messageService: MessageService,
  ) {
    this.lotId = route.snapshot.paramMap.get('id');
  }

  goBack() {
    this.router.navigate(['/pyme/marketplace']);
  }

  confirmCommit() {
    const l = this.lot();
    if (!l || this.commitKilos <= 0) return;
    this.marketService.addCommitment(l.id, this.commitKilos);
    this.messageService.add({
      severity: 'success',
      summary: 'Compromiso confirmado',
      detail: `Has comprometido ${this.commitKilos} kg de ${l.product}. ¡Gracias por apoyar a ${l.producer}!`,
      life: 4000,
    });
    this.commitKilos = 0;
  }
}
