import { HttpClient, HttpParams } from '@angular/common/http';
import {
    ChangeDetectionStrategy,
    Component,
    inject,
    type OnInit,
    signal,
} from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { API_BASE_URL } from '../../core/api.config';
import type { ImpactData } from '../../core/models';
import { RoleService } from '../../core/services/role.service';

@Component({
    selector: 'app-impact-dashboard',
    templateUrl: './impact-dashboard.component.html',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ImpactDashboardComponent implements OnInit {
    private readonly http = inject(HttpClient);
    private readonly apiUrl = inject(API_BASE_URL);
    private readonly roleService = inject(RoleService);

    loading = signal(false);
    data = signal<ImpactData | null>(null);

    async ngOnInit(): Promise<void> {
        this.loading.set(true);
        try {
            let params = new HttpParams();
            const userId = this.roleService.userId();
            if (userId) {
                params = params.set('userId', userId);
            }
            const res = await firstValueFrom(
                this.http.get<ImpactData>(`${this.apiUrl}/pyme/impact`, {
                    params,
                })
            );
            this.data.set(res);
        } finally {
            this.loading.set(false);
        }
    }
}
