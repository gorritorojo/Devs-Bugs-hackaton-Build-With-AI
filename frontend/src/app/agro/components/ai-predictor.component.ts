import { ChangeDetectionStrategy, Component, type OnInit } from '@angular/core';
import type { ChartOptions } from 'chart.js';
import { ChartModule } from 'primeng/chart';
import { PredictionService } from '../../core/services/prediction.service';

@Component({
    selector: 'app-ai-predictor',
    templateUrl: './ai-predictor.component.html',
    imports: [ChartModule],
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

    constructor(predictionService: PredictionService) {
        this.predictionService = predictionService;
    }

    ngOnInit() {
        this.predictionService.loadDemandPrediction('LOT-001');
    }
}
