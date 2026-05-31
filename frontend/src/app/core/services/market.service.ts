import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import type { CommitmentResponse, Lot } from '../models';

@Injectable({ providedIn: 'root' })
export class MarketService {
    private readonly http = inject(HttpClient);
    private readonly apiUrl = inject(API_BASE_URL);

    readonly lots = signal<Lot[]>([]);
    readonly loading = signal(false);

    async loadLots(all = false, createdBy?: string): Promise<void> {
        this.loading.set(true);
        try {
            const params: Record<string, string> = {};
            if (all) {
                // biome-ignore lint/complexity/useLiteralKeys: required for Record<string, string>
                params['all'] = 'true';
            }
            if (createdBy) {
                // biome-ignore lint/complexity/useLiteralKeys: required for Record<string, string>
                params['created_by'] = createdBy;
            }
            const options = Object.keys(params).length > 0 ? { params } : {};
            const data = await firstValueFrom(
                this.http.get<Lot[]>(`${this.apiUrl}/lots`, options)
            );
            this.lots.set(data);
        } finally {
            this.loading.set(false);
        }
    }

    async loadLot(id: string): Promise<Lot | null> {
        try {
            const lot = await firstValueFrom(
                this.http.get<Lot>(`${this.apiUrl}/lots/${id}`)
            );
            this.lots.update((lots) => {
                const idx = lots.findIndex((l) => l.id === id);
                if (idx >= 0) {
                    const copy = [...lots];
                    copy[idx] = lot;
                    return copy;
                }
                return [...lots, lot];
            });
            return lot;
        } catch {
            return null;
        }
    }

    async commitToLot(
        lotId: string,
        kilos: number,
        userId: string | null
    ): Promise<CommitmentResponse> {
        const res = await firstValueFrom(
            this.http.post<CommitmentResponse>(
                `${this.apiUrl}/lots/${lotId}/commit`,
                { kilos, userId }
            )
        );
        this.lots.update((lots) =>
            lots.map((l) => (l.id === lotId ? res.lot : l))
        );
        return res;
    }

    async createLot(data: {
        product: string;
        producer: string;
        targetKilos: number;
        basePrice: number;
        deadline: string;
        createdBy?: string | null;
    }): Promise<Lot> {
        const lot = await firstValueFrom(
            this.http.post<Lot>(`${this.apiUrl}/lots`, {
                product: data.product,
                producer: data.producer,
                targetKilos: data.targetKilos,
                basePrice: data.basePrice,
                deadline: data.deadline,
                createdBy: data.createdBy ?? null,
            })
        );
        this.lots.update((lots) => [...lots, lot]);
        return lot;
    }

    async toggleLotStatus(
        lotId: string,
        status: string,
        userId: string
    ): Promise<Lot> {
        const lot = await firstValueFrom(
            this.http.patch<Lot>(`${this.apiUrl}/lots/${lotId}/status`, {
                status,
                userId,
            })
        );
        this.lots.update((lots) => lots.map((l) => (l.id === lotId ? lot : l)));
        return lot;
    }
}
