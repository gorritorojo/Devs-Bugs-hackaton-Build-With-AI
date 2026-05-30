import { ChangeDetectionStrategy, Component, effect } from '@angular/core';
import {
    Router,
    RouterLink,
    RouterLinkActive,
    RouterOutlet,
} from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { RippleModule } from 'primeng/ripple';
import { TagModule } from 'primeng/tag';
import { ToastModule } from 'primeng/toast';
import { RoleService, UserRole } from '../core/services/role.service';

interface NavItem {
    icon: string;
    label: string;
    route: string;
}

@Component({
    selector: 'app-layout',
    templateUrl: './layout.component.html',
    imports: [
        ToastModule,
        RouterOutlet,
        RouterLink,
        RouterLinkActive,
        TagModule,
        ButtonModule,
        RippleModule,
    ],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LayoutComponent {
    currentRole: UserRole | null = null;

    navItems: NavItem[] = [
        {
            label: 'Marketplace',
            icon: 'pi pi-shop',
            route: '/pyme/marketplace',
        },
        { label: 'Impacto', icon: 'pi pi-chart-bar', route: '/pyme/impact' },
        { label: 'Lotes', icon: 'pi pi-box', route: '/agro/lots' },
        {
            label: 'Predictor IA',
            icon: 'pi pi-chart-line',
            route: '/agro/predict',
        },
    ];
    private readonly roleService: RoleService;
    private readonly router: Router;

    constructor(roleService: RoleService, router: Router) {
        this.roleService = roleService;
        this.router = router;
        effect(() => {
            this.currentRole = this.roleService.role();
        });

        if (!this.roleService.role()) {
            const url = this.router.url;
            if (url.startsWith('/pyme')) {
                this.roleService.setRole('pyme');
            } else if (url.startsWith('/agro')) {
                this.roleService.setRole('agro');
            }
        }
    }

    logout() {
        this.router.navigate(['/auth']);
    }
}
