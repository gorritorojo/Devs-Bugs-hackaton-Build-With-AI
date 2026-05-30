import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { ProgressBarModule } from 'primeng/progressbar';
import { ButtonModule } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { ChartModule } from 'primeng/chart';
import { TagModule } from 'primeng/tag';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { ToastModule } from 'primeng/toast';
import { RippleModule } from 'primeng/ripple';
import { TooltipModule } from 'primeng/tooltip';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';

@NgModule({
  imports: [CommonModule],
  exports: [
    CommonModule,
    RouterModule,
    FormsModule,
    CardModule,
    ProgressBarModule,
    ButtonModule,
    TableModule,
    ChartModule,
    TagModule,
    DialogModule,
    InputTextModule,
    InputNumberModule,
    ToastModule,
    RippleModule,
    TooltipModule,
    IconFieldModule,
    InputIconModule,
  ],
})
export class SharedModule {}
