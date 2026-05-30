import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { RippleModule } from 'primeng/ripple';
import { RoleService } from '../core/services/role.service';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    imports: [CardModule, ButtonModule, RippleModule],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginComponent {
    private readonly router: Router;

    private readonly roleService: RoleService;

    constructor(router: Router, roleService: RoleService) {
        this.router = router;
        this.roleService = roleService;
    }

    login(role: string) {
        this.roleService.setRole(role as 'pyme' | 'agro');
        const route = role === 'pyme' ? '/pyme/marketplace' : '/agro/lots';
        this.router.navigate([route]);
    }
}
