export interface Lot {
  id: string;
  product: string;
  targetKilos: number;
  currentKilos: number;
  basePrice: number;
  producer: string;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    fill: boolean;
    borderColor: string;
    borderDash?: number[];
    tension: number;
  }[];
}
