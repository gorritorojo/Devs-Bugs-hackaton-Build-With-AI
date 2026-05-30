import {
    ChangeDetectionStrategy,
    Component,
    computed,
    inject,
    signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
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

    step = signal<1 | 2 | 3>(1);
    selectedRole = signal<UserRole | null>(null);

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

    submitUserForm() {
        if (!this.isUserFormValid()) {
            return;
        }
        this.roleService.setUserProfile({
            email: this.email.trim(),
            companyName: this.companyName.trim(),
            contactName: this.contactName.trim(),
            phone: this.phone.trim(),
        });
        this.step.set(3);
    }

    isProfileValid(): boolean {
        if (!(this.area || this.customArea)) {
            return false;
        }
        return this.products.trim().length > 0 && this.businessSize.length > 0;
    }

    submitProfile() {
        if (!this.isProfileValid()) {
            return;
        }
        this.roleService.setProfile({
            area: this.area === 'Otro' ? this.customArea.trim() : this.area,
            products: this.products.trim(),
            businessSize: this.businessSize,
        });
        this.goToRoute();
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
