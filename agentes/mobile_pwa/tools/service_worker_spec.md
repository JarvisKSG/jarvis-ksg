# MOB-001 — Service Worker Architecture Spec
**Agente:** `mobile_pwa`
**Fecha:** 2026-03-24
**Version:** v1.0
**Aprobacion:** Pendiente `api_backend` + `qc`

---

## Objetivo

Permitir que Jeff vea los 4 KPIs de Nivel 1 (gasto_total_cop_mes, proyeccion_cierre_mes, facturas_pendientes, anomalias_count) **sin conexion a internet** en Finca Barbosa, mientras el resto del dashboard se degrada graciosamente.

---

## Estrategia de Cache por Recurso

```
┌─────────────────────────────────────────────────────────────────┐
│  CACHE FIRST (assets estaticos)                                  │
│  JS bundles, CSS, fonts, iconos, imagenes                        │
│  → Sirve desde cache. Actualiza en background tras deploy.       │
├─────────────────────────────────────────────────────────────────┤
│  STALE-WHILE-REVALIDATE (KPIs Nivel 1 — offline target)         │
│  GET /api/v1/dashboard/health                                    │
│  GET /api/v1/dashboard/kpis/nivel1                               │
│  TTL cache: 5 minutos. Muestra cached, actualiza en background.  │
│  → Jeff ve numeros reales aunque este sin conexion.              │
├─────────────────────────────────────────────────────────────────┤
│  NETWORK FIRST (datos transaccionales)                           │
│  GET /api/v1/recibos/*                                           │
│  GET /api/v1/anomalias/*                                         │
│  → Intenta red primero. Si falla, muestra cache con badge        │
│    "[Datos de hace X minutos — sin conexion]"                    │
├─────────────────────────────────────────────────────────────────┤
│  NETWORK ONLY (seguridad — NUNCA cachear)                        │
│  POST /api/v1/auth/*                                             │
│  Cualquier header Authorization: Bearer                          │
│  POST /api/v1/recibos/submit                                     │
│  → Sin cache. Si no hay red, retornar error claro al usuario.    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pseudocodigo Service Worker (Next.js con next-pwa o Workbox)

```javascript
// sw.js — Keystone KSG Service Worker v1.0
// IMPORTANTE: Este archivo es generado por mobile_pwa
// NO modificar directamente — editar esta spec y regenerar

import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { CacheFirst, NetworkFirst, StaleWhileRevalidate, NetworkOnly } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';
import { BackgroundSyncPlugin } from 'workbox-background-sync';

const CACHE_NAME = 'keystone-v1';
const KPI_CACHE = 'keystone-kpis-v1';

// 1. Precachear App Shell (assets estaticos)
precacheAndRoute(self.__WB_MANIFEST);

// 2. Cache First — assets estaticos con larga vida
registerRoute(
  ({ request }) => request.destination === 'image' ||
                   request.destination === 'font' ||
                   request.destination === 'script' ||
                   request.destination === 'style',
  new CacheFirst({
    cacheName: 'keystone-static-v1',
    plugins: [
      new ExpirationPlugin({ maxAgeSeconds: 30 * 24 * 60 * 60 }) // 30 dias
    ]
  })
);

// 3. Stale-While-Revalidate — KPIs Nivel 1 (offline target de Jeff)
// COORDINACION REQUERIDA: api_backend debe confirmar que estos endpoints
// no requieren logica especial de autenticacion en el cache layer
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/v1/dashboard/'),
  new StaleWhileRevalidate({
    cacheName: KPI_CACHE,
    plugins: [
      new ExpirationPlugin({ maxAgeSeconds: 5 * 60 }) // 5 minutos TTL
    ]
  })
);

// 4. Network First — datos transaccionales con fallback a cache
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/v1/recibos/') ||
               url.pathname.startsWith('/api/v1/anomalias/'),
  new NetworkFirst({
    cacheName: 'keystone-transactional-v1',
    networkTimeoutSeconds: 10,
    plugins: [
      new ExpirationPlugin({ maxAgeSeconds: 60 * 60 }) // 1 hora max stale
    ]
  })
);

// 5. Network Only — autenticacion y escrituras (NUNCA cachear)
registerRoute(
  ({ url, request }) => url.pathname.startsWith('/api/v1/auth/') ||
                        request.headers.get('Authorization') ||
                        request.method === 'POST',
  new NetworkOnly()
);

// 6. Offline fallback — pagina de degradacion graceful
self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => caches.match('/offline.html'))
    );
  }
});
```

---

## Criterios de Aprobacion Lighthouse

| Criterio | Valor Minimo | Estado |
|----------|-------------|--------|
| PWA Installability | 100/100 | Pendiente audit |
| Offline capability | PASS | Pendiente audit |
| HTTPS | PASS | Requerido en deploy |
| manifest.json valido | PASS | Draft listo |
| Service Worker registrado | PASS | Pendiente implementacion |
| Icons 192x192 + 512x512 | PASS | Pendiente crear iconos |

---

## Pendientes antes de implementacion

- [ ] `api_backend` debe aprobar la estrategia de cache para `/api/v1/dashboard/*`
- [ ] `frontend_engineer` debe confirmar que Next.js version soporta Workbox v7
- [ ] Crear iconos: keystone-icon-192.png, keystone-icon-512.png, keystone-icon-512-maskable.png
- [ ] Crear `/public/offline.html` — pagina de fallback sin conexion
- [ ] `tester_automation` debe agregar Lighthouse CI al pipeline de PR

---

*Generado por: `mobile_pwa` | Coordinacion requerida: `api_backend`, `frontend_engineer`, `tester_automation`*
