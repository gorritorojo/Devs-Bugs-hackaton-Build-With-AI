import { ChangeDetectionStrategy, Component, type OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import type { ChartOptions } from 'chart.js';
import { ChartModule } from 'primeng/chart';
import { SelectModule } from 'primeng/select';
import { MarketService } from '../../core/services/market.service';
import { PredictionService } from '../../core/services/prediction.service';

@Component({
    selector: 'app-ai-predictor',
    templateUrl: './ai-predictor.component.html',
    imports: [ChartModule, SelectModule, FormsModule],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AIPredictorComponent implements OnInit {
    chartOptions: ChartOptions<'line'> = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { usePointStyle: true, padding: 20 },
            },
        },
        scales: {
            x: { grid: { display: false } },
            y: {
                beginAtZero: true,
                ticks: { callback: (v) => ` ${v}  kg` },
            },
        },
    };

    predictionService: PredictionService;
    marketService: MarketService;
    selectedLotId: string | null = null;

    constructor(
        predictionService: PredictionService,
        marketService: MarketService,
        route: ActivatedRoute
    ) {
        this.predictionService = predictionService;
        this.marketService = marketService;
        const lotId = route.snapshot.queryParamMap.get('lotId');
        if (lotId) {
            this.selectedLotId = lotId;
        }
    }

    ngOnInit() {
        this.marketService.loadLots();
        if (this.selectedLotId) {
            this.predictionService.loadDemandPrediction(this.selectedLotId);
        }
    }

    onLotChange(lotId: string) {
        this.selectedLotId = lotId;
        this.predictionService.loadDemandPrediction(lotId);
    }
}
