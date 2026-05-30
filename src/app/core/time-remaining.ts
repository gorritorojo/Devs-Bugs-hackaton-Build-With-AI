export function timeRemaining(deadline: string): {
    expired: boolean;
    label: string;
    severity: 'danger' | 'warn' | 'info';
} {
    const now = Date.now();
    const end = new Date(deadline).getTime();
    const diffMs = end - now;
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffMs <= 0) {
        return { expired: true, label: 'Vencido', severity: 'danger' };
    }

    if (diffDays === 0) {
        return { expired: false, label: 'Hoy', severity: 'warn' };
    }

    if (diffDays === 1) {
        return { expired: false, label: '1 día restante', severity: 'warn' };
    }

    if (diffDays < 7) {
        return {
            expired: false,
            label: `${diffDays} días restantes`,
            severity: 'warn',
        };
    }

    if (diffDays < 30) {
        const weeks = Math.ceil(diffDays / 7);
        return {
            expired: false,
            label: `${weeks} ${weeks === 1 ? 'semana' : 'semanas'} restantes`,
            severity: 'info',
        };
    }

    return {
        expired: false,
        label: `${diffDays} días restantes`,
        severity: 'info',
    };
}
