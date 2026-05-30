import {
    type ApplicationConfig,
    provideZonelessChangeDetection,
} from '@angular/core';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideRouter, type Routes } from '@angular/router';
import Aura from '@primeng/themes/aura';
import { MessageService } from 'primeng/api';
import { providePrimeNG } from 'primeng/config';
import { roleGuard } from './core/guards/role.guard';

const routes: Routes = [
    { path: '', redirectTo: '/auth', pathMatch: 'full' },
    {
        path: 'auth',
        loadComponent: () =>
            import('./auth/login.component').then((m) => m.LoginComponent),
    },
    {
        path: '',
        loadComponent: () =>
            import('./layout/layout.component').then((m) => m.LayoutComponent),
        children: [
            {
                path: 'pyme',
                loadChildren: () =>
                    import('./pyme/pyme.routes').then((m) => m.pymeRoutes),
                canActivateChild: [roleGuard('pyme')],
            },
            {
                path: 'agro',
                loadChildren: () =>
                    import('./agro/agro.routes').then((m) => m.agroRoutes),
                canActivateChild: [roleGuard('agro')],
            },
        ],
    },
];

export const appConfig: ApplicationConfig = {
    providers: [
        provideZonelessChangeDetection(),
        provideRouter(routes),
        provideAnimations(),
        MessageService,
        providePrimeNG({
            theme: {
                preset: Aura,
                options: {
                    darkModeSelector: false,
                },
            },
        }),
    ],
};
