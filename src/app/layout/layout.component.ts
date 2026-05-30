import { Component, effect } from '@angular/core';
import { Router } from '@angular/router';
import { RoleService, UserRole } from '../core/services/role.service';

interface NavItem {
  label: string;
  icon: string;
  route: string;
}

@Component({
  standalone: false,
  selector: 'app-layout',
  templateUrl: './layout.component.html',
})
export class LayoutComponent {
  currentRole: UserRole | null = null;

  navItems: NavItem[] = [
    { label: 'Marketplace', icon: 'pi pi-shop', route: '/pyme/marketplace' },
    { label: 'Impacto', icon: 'pi pi-chart-bar', route: '/pyme/impact' },
    { label: 'Lotes', icon: 'pi pi-box', route: '/agro/lots' },
    { label: 'Predictor IA', icon: 'pi pi-chart-line', route: '/agro/predict' },
  ];

  constructor(
    private roleService: RoleService,
    private router: Router,
  ) {
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
