import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RoleService } from '../core/services/role.service';

@Component({
  standalone: false,
  selector: 'app-login',
  templateUrl: './login.component.html',
})
export class LoginComponent {
  constructor(
    private router: Router,
    private roleService: RoleService,
  ) {}

  login(role: string) {
    this.roleService.setRole(role as 'pyme' | 'agro');
    const route = role === 'pyme' ? '/pyme/marketplace' : '/agro/lots';
    this.router.navigate([route]);
  }
}
