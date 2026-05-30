# Esquemas de Base de Datos - CrowdBuy

## `users`

```json
{
  "id": "uuid",
  "role": "'pyme' | 'agro'",
  "contact_name": "string",
  "email": "string | null",
  "company_name": "string | null",
  "phone": "string | null",
  "area": "string | null",
  "products": "string | null",
  "business_size": "string | null",
  "created_at": "datetime"
}
```

| Campo | Obligatorio | Notas |
|---|---|---|
| `id` | si | UUID |
| `role` | si | `pyme` o `agro` |
| `contact_name` | ambos | PYME: contacto. Productor: nombre completo |
| `email` | PYME | |
| `company_name` | PYME | |
| `phone` | Productor | |
| `area` | no | dropdown + "Otro" |
| `products` | no | texto libre |
| `business_size` | no | dropdown |

---

## `lots`

```json
{
  "id": "string",
  "product": "string",
  "producer": "string",
  "target_kilos": "number",
  "current_kilos": "number",
  "base_price": "number",
  "deadline": "datetime",
  "status": "'active' | 'completed' | 'expired'",
  "created_by": "uuid",
  "created_at": "datetime"
}
```

| Campo | Notas |
|---|---|
| `id` | `LOT-XXX` (autoincremental) |
| `product` | nombre del producto |
| `producer` | nombre del productor (texto libre) |
| `target_kilos` | meta en kg |
| `current_kilos` | kilos comprometidos acumulados |
| `base_price` | precio por kg |
| `deadline` | fecha limite ISO 8601 |
| `status` | derivado: `current >= target` → completed, `deadline < now` → expired |
| `created_by` | FK → `users.id` (productor que creo el lote) |

---

## `commitments`

```json
{
  "id": "uuid",
  "lot_id": "string",
  "user_id": "uuid",
  "kilos": "number",
  "created_at": "datetime"
}
```

| Campo | Notas |
|---|---|
| `lot_id` | FK → `lots.id` |
| `user_id` | FK → `users.id` (debe ser rol `pyme`) |
| `kilos` | cantidad comprometida |
| `created_at` | timestamp |

Regla: `SUM(kilos)` por lote = `lots.current_kilos`.

---

## `demand_predictions`

```json
{
  "id": "uuid",
  "lot_id": "string",
  "labels": ["string"],
  "datasets": [
    {
      "label": "string",
      "data": ["number"],
      "fill": "boolean",
      "border_color": "string",
      "border_dash": ["number"] | null,
      "tension": "number"
    }
  ],
  "created_at": "datetime"
}
```

| Campo | Notas |
|---|---|
| `lot_id` | FK → `lots.id` |
| `labels` | meses o periodos (12 valores) |
| `datasets[].data` | `null` donde no hay dato historico |
| `border_dash` | `[5,5]` para prediccion, `null` para historico |

---

## Endpoints esperados

| Metodo | Ruta | Descripcion |
|---|---|---|
| `POST` | `/auth/register` | Crear usuario (paso 2: datos requeridos) |
| `PUT` | `/users/:id/profile` | Actualizar perfil de negocio (paso 3: opcional) |
| `GET` | `/lots` | Listar lotes activos |
| `GET` | `/lots/:id` | Detalle de un lote |
| `POST` | `/lots` | Crear lote (requiere `hasUserProfile`) |
| `POST` | `/lots/:id/commit` | Comprometerse a kilos (requiere `hasUserProfile`) |
| `GET` | `/lots/:id/prediction` | Prediccion de demanda IA |
| `GET` | `/pyme/impact` | Metricas de impacto para PYME |
