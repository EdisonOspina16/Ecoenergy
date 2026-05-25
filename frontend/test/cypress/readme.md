# pruebas E2E con cypress

```
e2e/
├── ui/           login, logout, perfil-hogar, recuperar, suscripción, dispositivos-home, tomacorrientes
├── api/          auth, perfil, dispositivos, subscribe
├── security/     auth, recuperar
├── regression/   flujos críticos
└── accessibility/ paginas (cypress-axe)
support/
├── apiMocks.js   interceptores + loginByUi + fillControlledInput
└── e2e.js
fixtures/         hogar, dispositivos, usuario
```

### Cómo ejecutar

```
cd frontend
npm run cy:open    # modo interactivo
npm run cy:run     # headless (requiere app en :3000)
npm run cy:test    # levanta Next + ejecuta todo
```


| Comando                    | Qué hace                            |
| -------------------------- | ----------------------------------- |
| `npm run cy:test`          | Ejecuta todo automático/headless    |
| `npx cypress open`         | Abre interfaz visual de Cypress     |
| `npx cypress run --headed` | Ejecuta pruebas mostrando navegador |
