import { Injectable, signal } from '@angular/core';

export type UserRole = 'pyme' | 'agro';

@Injectable({ providedIn: 'root' })
export class RoleService {
    readonly role = signal<UserRole | null>(null);

    setRole(role: UserRole): void {
        this.role.set(role);
    }
}
