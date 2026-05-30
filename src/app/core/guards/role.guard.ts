import { inject } from '@angular/core';
import { type CanActivateChildFn, Router } from '@angular/router';
import type { UserRole } from '../services/role.service';
import { RoleService } from '../services/role.service';

export function roleGuard(required: UserRole): CanActivateChildFn {
    return () => {
        const roleService = inject(RoleService);
        const router = inject(Router);

        const currentRole = roleService.role();
        if (!currentRole) {
            return router.parseUrl('/auth');
        }

        if (currentRole !== required) {
            const route =
                currentRole === 'pyme' ? '/pyme/marketplace' : '/agro/lots';
            return router.parseUrl(route);
        }

        return true;
    };
}
