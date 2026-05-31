import { HttpClient } from '@angular/common/http';
import { computed, Injectable, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import type { BusinessProfile, User, UserProfile } from '../models';

export type UserRole = 'pyme' | 'agro';

@Injectable({ providedIn: 'root' })
export class RoleService {
    private readonly http = inject(HttpClient);
    private readonly apiUrl = inject(API_BASE_URL);

    readonly role = signal<UserRole | null>(null);
    readonly userId = signal<string | null>(null);

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

    async login(role: UserRole, profile: UserProfile): Promise<User> {
        const user = await firstValueFrom(
            this.http.post<User>(`${this.apiUrl}/auth/login`, {
                role,
                email: profile.email || null,
                phone: profile.phone || null,
            })
        );
        this.role.set(role);
        this.userId.set(user.id);
        this.userProfile.set({
            companyName: user.companyName ?? '',
            contactName: user.contactName ?? '',
            email: user.email ?? '',
            phone: user.phone ?? '',
        });
        this.businessProfile.set({
            area: user.area ?? '',
            products: user.products ?? '',
            businessSize: user.businessSize ?? '',
        });
        return user;
    }

    async register(role: UserRole, profile: UserProfile): Promise<User> {
        const user = await firstValueFrom(
            this.http.post<User>(`${this.apiUrl}/auth/register`, {
                role,
                contactName: profile.contactName,
                email: profile.email || null,
                companyName: profile.companyName || null,
                phone: profile.phone || null,
            })
        );
        this.userId.set(user.id);
        return user;
    }

    async updateProfile(profile: BusinessProfile): Promise<User> {
        const id = this.userId();
        if (!id) {
            throw new Error('No user ID available');
        }
        const user = await firstValueFrom(
            this.http.put<User>(`${this.apiUrl}/users/${id}/profile`, {
                area: profile.area,
                products: profile.products,
                businessSize: profile.businessSize,
            })
        );
        return user;
    }

    clear() {
        this.role.set(null);
        this.userId.set(null);
        this.userProfile.set({
            companyName: '',
            contactName: '',
            email: '',
            phone: '',
        });
        this.businessProfile.set({ area: '', products: '', businessSize: '' });
    }
}
