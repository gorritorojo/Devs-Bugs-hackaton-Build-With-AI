import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import type { PredictionResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class PredictionService {
    private readonly http = inject(HttpClient);
    private readonly apiUrl = inject(API_BASE_URL);

    readonly loading = signal(false);
    readonly data = signal<PredictionResponse | null>(null);
    readonly error = signal<string | null>(null);

    async loadDemandPrediction(product: string, months = 1): Promise<void> {
        this.loading.set(true);
        this.data.set(null);
        this.error.set(null);
        try {
            const res = await firstValueFrom(
                this.http.get<PredictionResponse>(
                    `${this.apiUrl}/predictions/${product}`,
                    { params: { months: months.toString() } }
                )
            );
            this.data.set(res);
        } catch (err) {
            this.error.set(
                err instanceof Error
                    ? err.message
                    : 'Error al obtener predicción'
            );
        } finally {
            this.loading.set(false);
        }
    }
}
