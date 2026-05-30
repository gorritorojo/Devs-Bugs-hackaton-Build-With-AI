import { Component, computed, inject } from '@angular/core';
import { MarketService } from '../../core/services/market.service';

@Component({
  standalone: false,
  selector: 'app-impact-dashboard',
  templateUrl: './impact-dashboard.component.html',
})
export class ImpactDashboardComponent {
  private marketService = inject(MarketService);

  totalKilos = computed(() =>
    this.marketService.lots().reduce((sum, l) => sum + l.currentKilos, 0)
  );

  activeLotes = computed(() => this.marketService.lots().length);

  totalProgress = computed(() => {
    const lots = this.marketService.lots();
    const totalKilos = lots.reduce((sum, l) => sum + l.currentKilos, 0);
    const totalTarget = lots.reduce((sum, l) => sum + l.targetKilos, 0);
    return totalTarget > 0 ? Math.round((totalKilos / totalTarget) * 100) : 0;
  });

  uniqueProducers = computed(() =>
    [...new Set(this.marketService.lots().map(l => l.producer))]
  );
}
