export interface Lot {
    basePrice: number;
    createdAt?: string;
    createdBy?: string;
    currentKilos: number;
    deadline: string;
    id: string;
    producer: string;
    product: string;
    status?: string;
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

export interface User {
    area: string | null;
    businessSize: string | null;
    companyName: string | null;
    contactName: string;
    createdAt: string;
    email: string | null;
    id: string;
    phone: string | null;
    products: string | null;
    role: string;
}

export interface ImpactData {
    activeLotes: number;
    producerCount: number;
    totalKilos: number;
    totalProgress: number;
    uniqueProducers: string[];
}

export interface CommitmentResponse {
    commitment: {
        id: string;
        lotId: string;
        userId: string | null;
        kilos: number;
        createdAt: string;
    };
    lot: Lot;
}

export interface BusinessProfile {
    area: string;
    businessSize: string;
    products: string;
}

export interface UserProfile {
    companyName: string;
    contactName: string;
    email: string;
    phone: string;
}

export const AGRO_AREA_OPTIONS = [
    'Agricultura',
    'Ganadería',
    'Apicultura',
    'Pesca',
    'Avicultura',
    'Fruticultura',
    'Caficultura',
] as const;

export const PYME_AREA_OPTIONS = [
    'Restaurante',
    'Panadería',
    'Supermercado',
    'Tienda',
    'Distribuidora',
    'Exportación',
    'Catering',
] as const;

export const AGRO_SIZE_OPTIONS = [
    'Pequeño (1-5 ha)',
    'Mediano (5-20 ha)',
    'Grande (20+ ha)',
    'Industrial',
] as const;

export const PYME_SIZE_OPTIONS = [
    'Micro (1-5 empleados)',
    'Pequeño (6-20)',
    'Mediano (21-50)',
    'Grande (50+)',
] as const;
