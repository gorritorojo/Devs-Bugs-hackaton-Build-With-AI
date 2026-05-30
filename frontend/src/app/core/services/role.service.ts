import { computed, Injectable, signal } from '@angular/core';
import type { BusinessProfile, UserProfile } from '../models';

export type UserRole = 'pyme' | 'agro';

@Injectable({ providedIn: 'root' })
export class RoleService {
    readonly role = signal<UserRole | null>(null);

    readonly userProfile = signal<UserProfile>({
        companyName: '',
        contactName: '',
        email: '',
        phone: '',
    });

    readonly businessProfile = signal<BusinessProfile>({
        area: '',
        products: '',
        businessSize: '',
    });

    readonly hasUserProfile = computed(() => {
        const p = this.userProfile();
        const role = this.role();
        if (role === 'pyme') {
            return (
                p.email.length > 0 &&
                p.companyName.length > 0 &&
                p.contactName.length > 0
            );
        }
        if (role === 'agro') {
            return p.contactName.length > 0 && p.phone.length > 0;
        }
        return false;
    });

    readonly hasProfile = computed(() => {
        const p = this.businessProfile();
        return (
            p.area.length > 0 &&
            p.products.length > 0 &&
            p.businessSize.length > 0
        );
    });

    setRole(role: UserRole): void {
        this.role.set(role);
    }

    setUserProfile(profile: UserProfile): void {
        this.userProfile.set(profile);
    }

    setProfile(profile: BusinessProfile): void {
        this.businessProfile.set(profile);
    }

    clear() {
        this.role.set(null);
        this.userProfile.set({
            companyName: '',
            contactName: '',
            email: '',
            phone: '',
        });
        this.businessProfile.set({ area: '', products: '', businessSize: '' });
    }
}
