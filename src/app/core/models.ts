export interface Lot {
    basePrice: number;
    currentKilos: number;
    deadline: string;
    id: string;
    producer: string;
    product: string;
    targetKilos: number;
}

export interface ChartData {
    datasets: {
        label: string;
        data: number[];
        fill: boolean;
        borderColor: string;
        borderDash?: number[];
        tension: number;
    }[];
    labels: string[];
}
