import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputNumberModule } from 'primeng/inputnumber';
import { SelectModule } from 'primeng/select';
import { PRODUCTS } from '../../core/models';
import { PredictionService } from '../../core/services/prediction.service';

@Component({
    selector: 'app-ai-predictor',
    templateUrl: './ai-predictor.component.html',
    imports: [SelectModule, FormsModule, InputNumberModule, ButtonModule],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AIPredictorComponent {
    predictionService: PredictionService;

    readonly products = PRODUCTS.map((p) => ({ label: p, value: p }));
    readonly selectedProduct = signal<string | null>(null);
    readonly months = signal(3);

    constructor(predictionService: PredictionService) {
        this.predictionService = predictionService;
    }

    onProductChange(productId: string) {
        this.selectedProduct.set(productId);
        this.predictionService.loadDemandPrediction(productId, this.months());
    }

    onPredict() {
        const product = this.selectedProduct();
        if (product) {
            this.predictionService.loadDemandPrediction(product, this.months());
        }
    }

    getMonthName(month: number): string {
        const names = [
            'Enero',
            'Febrero',
            'Marzo',
            'Abril',
            'Mayo',
            'Junio',
            'Julio',
            'Agosto',
            'Septiembre',
            'Octubre',
            'Noviembre',
            'Diciembre',
        ];
        return names[month - 1] ?? '';
    }

    formatKg(value: number): string {
        return new Intl.NumberFormat('es-BO', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2,
        }).format(value);
    }
}
