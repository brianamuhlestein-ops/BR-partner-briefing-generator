# Partner Briefing Generator UI

Vue 3, TypeScript, Vuetify, and Vite frontend for the SWIFT Partner Briefing Generator.

```powershell
npm install
npm run dev
```

The development server listens on `http://127.0.0.1:5179` and proxies `/api` to the Falcon service on port `8089`.

Verification:

```powershell
npm test
npm run build
```

The active workspaces are Impact & Risk Matrix, Core Distribution Brief, Partner Tailored Brief, and Media Generator. The Compact interface preference is persisted locally without remounting these workspaces.
