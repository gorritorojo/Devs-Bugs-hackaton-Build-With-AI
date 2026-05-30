import { Injectable, signal } from '@angular/core';
import { Lot } from '../models';

const INITIAL_LOTS: Lot[] = [
  { id: 'LOT-001', product: 'Arroz Orgánico', targetKilos: 1000, currentKilos: 720, basePrice: 2.5, producer: 'Cooperativa La Esperanza' },
  { id: 'LOT-002', product: 'Frijol Negro', targetKilos: 500, currentKilos: 380, basePrice: 3.2, producer: 'Asociación El Progreso' },
  { id: 'LOT-003', product: 'Miel de Abeja', targetKilos: 300, currentKilos: 90, basePrice: 8.0, producer: 'Apiarios del Valle' },
];

@Injectable({ providedIn: 'root' })
export class MarketService {
  readonly lots = signal<Lot[]>(INITIAL_LOTS);

  addCommitment(lotId: string, kilos: number): void {
    this.lots.update(lots =>
      lots.map(lot =>
        lot.id === lotId
          ? { ...lot, currentKilos: Math.min(lot.currentKilos + kilos, lot.targetKilos) }
          : lot
      )
    );
  }

  createLot(data: { product: string; targetKilos: number; basePrice: number; producer: string }): void {
    const current = this.lots();
    const newLot: Lot = {
      id: `LOT-${String(current.length + 1).padStart(3, '0')}`,
      product: data.product,
      targetKilos: data.targetKilos,
      currentKilos: 0,
      basePrice: data.basePrice,
      producer: data.producer,
    };
    this.lots.set([...current, newLot]);
  }
}
