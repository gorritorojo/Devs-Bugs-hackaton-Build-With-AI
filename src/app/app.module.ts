import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";

import { MessageService } from "primeng/api";
import { providePrimeNG } from "primeng/config";
import Aura from "@primeng/themes/aura";

import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { CoreModule } from "./core/core.module";
import { SharedModule } from "./shared/shared.module";
import { LayoutComponent } from "./layout/layout.component";

@NgModule({
    declarations: [AppComponent, LayoutComponent],
    imports: [
        BrowserModule,
        BrowserAnimationsModule,
        AppRoutingModule,
        CoreModule,
        SharedModule,
    ],
    providers: [
        MessageService,
        providePrimeNG({
            theme: {
                preset: Aura,
                options: {
                    darkModeSelector: false,
                },
            },
        }),
    ],
    bootstrap: [AppComponent],
})
export class AppModule {}
