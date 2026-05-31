import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import type { ChartData } from '../models';

@Injectable({ providedIn: 'root' })
export class PredictionService {
    private readonly http = inject(HttpClient);
    private readonly apiUrl = inject(API_BASE_URL);

    readonly loading = signal(false);
    readonly data = signal<ChartData | null>(null);

    async loadDemandPrediction(lotId: string): Promise<void> {
        this.loading.set(true);
        this.data.set(null);
        try {
            const res = await firstValueFrom(
                this.http.get<{
                    labels: string[];
                    datasets: ChartData['datasets'];
                }>(`${this.apiUrl}/lots/${lotId}/prediction`)
            );
            this.data.set({
                labels: res.labels,
                datasets: res.datasets,
            });
        } finally {
            this.loading.set(false);
        }
    }
}
