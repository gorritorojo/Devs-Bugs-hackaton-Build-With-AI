import {
    ChangeDetectionStrategy,
    Component,
    computed,
    inject,
    signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { RippleModule } from 'primeng/ripple';
import { SelectModule } from 'primeng/select';
import { TextareaModule } from 'primeng/textarea';
import {
    AGRO_AREA_OPTIONS,
    AGRO_SIZE_OPTIONS,
    PYME_AREA_OPTIONS,
    PYME_SIZE_OPTIONS,
} from '../core/models';
import { RoleService, type UserRole } from '../core/services/role.service';

type AuthMode = 'register' | 'login';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    imports: [
        CardModule,
        ButtonModule,
        RippleModule,
        FormsModule,
        SelectModule,
        TextareaModule,
        InputTextModule,
    ],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginComponent {
    private readonly router = inject(Router);
    private readonly roleService = inject(RoleService);
    private readonly messageService = inject(MessageService);

    authMode = signal<AuthMode>('register');
    step = signal<1 | 2 | 3>(1);
    selectedRole = signal<UserRole | null>(null);
    submitting = signal(false);

    email = '';
    companyName = '';
    contactName = '';
    phone = '';

    area = '';
    products = '';
    businessSize = '';
    customArea = '';

    readonly areaOptions = computed(() => {
        const role = this.selectedRole();
        const base =
            role === 'agro' ? [...AGRO_AREA_OPTIONS] : [...PYME_AREA_OPTIONS];
        return [...base, 'Otro'];
    });

    readonly sizeOptions = computed(() =>
        this.selectedRole() === 'agro'
            ? [...AGRO_SIZE_OPTIONS]
            : [...PYME_SIZE_OPTIONS]
    );

    toggleMode(mode: AuthMode) {
        this.authMode.set(mode);
        this.step.set(1);
        this.selectedRole.set(null);
        this.email = '';
        this.companyName = '';
        this.contactName = '';
        this.phone = '';
        this.area = '';
        this.products = '';
        this.businessSize = '';
        this.customArea = '';
    }

    selectRole(role: UserRole) {
        this.selectedRole.set(role);
        this.roleService.setRole(role);
        this.step.set(2);
    }

    goToRoute() {
        const route =
            this.selectedRole() === 'pyme' ? '/pyme/marketplace' : '/agro/lots';
        this.router.navigate([route]);
    }

    isLoginFormValid(): boolean {
        if (this.selectedRole() === 'pyme') {
            return this.email.trim().length > 0;
        }
        return this.phone.trim().length > 0;
    }

    async submitLogin() {
        if (!(this.isLoginFormValid() && this.selectedRole())) {
            return;
        }
        const role = this.selectedRole();
        if (!role) {
            return;
        }
        const profile = {
            email: this.email.trim(),
            companyName: '',
            contactName: '',
            phone: this.phone.trim(),
        };
        this.submitting.set(true);
        try {
            await this.roleService.login(role, profile);
            this.goToRoute();
        } catch {
            this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: 'No se encontro una cuenta con esos datos. Verifica e intenta de nuevo.',
                life: 5000,
            });
        } finally {
            this.submitting.set(false);
        }
    }

    isUserFormValid(): boolean {
        if (this.selectedRole() === 'pyme') {
            return (
                this.email.trim().length > 0 &&
                this.companyName.trim().length > 0 &&
                this.contactName.trim().length > 0
            );
        }
        return (
            this.contactName.trim().length > 0 && this.phone.trim().length > 0
        );
    }

    async submitUserForm() {
        if (!(this.isUserFormValid() && this.selectedRole())) {
            return;
        }
        const role = this.selectedRole();
        if (!role) {
            return;
        }
        const profile = {
            email: this.email.trim(),
            companyName: this.companyName.trim(),
            contactName: this.contactName.trim(),
            phone: this.phone.trim(),
        };
        this.submitting.set(true);
        try {
            await this.roleService.register(role, profile);
            this.roleService.setRole(role);
            this.roleService.setUserProfile(profile);
            this.step.set(3);
        } catch {
            this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: 'No se pudo completar el registro. Intenta de nuevo.',
                life: 5000,
            });
        } finally {
            this.submitting.set(false);
        }
    }

    isProfileValid(): boolean {
        if (!(this.area || this.customArea)) {
            return false;
        }
        return this.products.trim().length > 0 && this.businessSize.length > 0;
    }

    async submitProfile() {
        if (!this.isProfileValid()) {
            return;
        }
        const profile = {
            area: this.area === 'Otro' ? this.customArea.trim() : this.area,
            products: this.products.trim(),
            businessSize: this.businessSize,
        };
        this.submitting.set(true);
        try {
            await this.roleService.updateProfile(profile);
            this.roleService.setProfile(profile);
            this.goToRoute();
        } catch {
            this.messageService.add({
                severity: 'error',
                summary: 'Error',
                detail: 'No se pudo guardar el perfil. Intenta de nuevo.',
                life: 5000,
            });
        } finally {
            this.submitting.set(false);
        }
    }

    skipProfile() {
        this.goToRoute();
    }

    goBack() {
        if (this.step() === 2) {
            this.email = '';
            this.companyName = '';
            this.contactName = '';
            this.phone = '';
            this.step.set(1);
        } else if (this.step() === 3) {
            this.area = '';
            this.products = '';
            this.businessSize = '';
            this.customArea = '';
            this.step.set(2);
        }
    }
}
