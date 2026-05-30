import { Component, OnInit } from '@angular/core';
import { PredictionService } from '../../core/services/prediction.service';

@Component({
  standalone: false,
  selector: 'app-ai-predictor',
  templateUrl: './ai-predictor.component.html',
})
export class AIPredictorComponent implements OnInit {
  chartOptions: any = {
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
        ticks: { callback: (v: any) => v + ' kg' },
      },
    },
  };

  constructor(public predictionService: PredictionService) {}

  ngOnInit() {
    this.predictionService.loadDemandPrediction('LOT-001');
  }
}
