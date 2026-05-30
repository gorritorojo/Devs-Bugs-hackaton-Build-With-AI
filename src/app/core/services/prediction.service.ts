import { Injectable, signal } from '@angular/core';
import type { ChartData } from '../models';

@Injectable({ providedIn: 'root' })
export class PredictionService {
    readonly loading = signal(false);
    readonly data = signal<ChartData | null>(null);

    loadDemandPrediction(_productId: string): void {
        this.loading.set(true);
        this.data.set(null);

        setTimeout(() => {
            const chartData: ChartData = {
                labels: [
                    'Ene',
                    'Feb',
                    'Mar',
                    'Abr',
                    'May',
                    'Jun',
                    'Jul',
                    'Ago',
                    'Sep',
                    'Oct',
                    'Nov',
                    'Dic',
                ],
                datasets: [
                    {
                        label: 'Histórico',
                        data: [
                            120, 135, 110, 160, 180, 200, 190, 210, 170, 150,
                            140, 130,
                        ],
                        fill: false,
                        borderColor: '#61BAC2',
                        tension: 0.4,
                    },
                    {
                        label: 'Predicción',
                        data: [
                            null,
                            null,
                            null,
                            null,
                            null,
                            null,
                            190,
                            210,
                            220,
                            250,
                            270,
                            300,
                        ].map((v) => v ?? Number.NaN),
                        fill: false,
                        borderColor: '#C29A61',
                        borderDash: [5, 5],
                        tension: 0.4,
                    },
                ],
            };
            this.data.set(chartData);
            this.loading.set(false);
        }, 600);
    }
}
