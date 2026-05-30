import {
    ChangeDetectionStrategy,
    Component,
    computed,
    effect,
} from '@angular/core';
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
import { RoleService, type UserRole } from '../core/services/role.service';

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
    private readonly roleService: RoleService;
    private readonly router: Router;

    private readonly allNavItems: Record<UserRole, NavItem[]> = {
        pyme: [
            {
                label: 'Marketplace',
                icon: 'pi pi-shop',
                route: '/pyme/marketplace',
            },
            {
                label: 'Impacto',
                icon: 'pi pi-chart-bar',
                route: '/pyme/impact',
            },
        ],
        agro: [
            { label: 'Lotes', icon: 'pi pi-box', route: '/agro/lots' },
            {
                label: 'Predictor IA',
                icon: 'pi pi-chart-line',
                route: '/agro/predict',
            },
        ],
    };

    readonly navItems = computed<NavItem[]>(() => {
        const role = this.currentRole;
        if (!role) {
            return [];
        }
        return this.allNavItems[role];
    });

    readonly hasUserProfile = computed(() => this.roleService.hasUserProfile());

    readonly accentColor = computed(() => {
        const role = this.currentRole;
        if (!role) {
            return '#61BAC2';
        }
        return role === 'pyme' ? '#61BAC2' : '#C29A61';
    });

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
        this.roleService.clear();
        this.router.navigate(['/auth']);
    }
}
