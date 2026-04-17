# atlaspi-client (JavaScript/TypeScript)

Official JS/TS client for the **AtlasPI Historical Geography API** — free,
public, no-auth REST API with 862 historical entities, 490 events, 94 dynasty
chains from 4500 BCE to 2024.

## Install

```bash
npm install atlaspi-client
# or
pnpm add atlaspi-client
# or
yarn add atlaspi-client
```

## Quick start

```ts
import { AtlasPI } from "atlaspi-client";

const client = new AtlasPI();

// What was happening in 1250 globally?
const snap = await client.snapshot(1250);
console.log(snap.periods.items);

// Find entities similar to a given one
const similar = await client.entities.similar(1, { limit: 5 });

// Events on a given day
const today = await client.events.onThisDay("07-14"); // Bastille Day

// Batch fetch
const batch = await client.entities.batch([1, 2, 3, 42, 100]);
console.log(`Got ${batch.found} of ${batch.requested}`);
```

## Works in

- Node.js 18+
- Deno
- Bun
- Modern browsers (no bundler required — ESM)

## Custom options

```ts
const client = new AtlasPI({
  baseUrl: "https://atlaspi.cra-srl.com",
  timeout: 30_000,
  userAgent: "my-app/1.0",
});
```

## API

Namespaced, mirrors the REST API structure:

- `client.entities.*` — `list`, `get`, `batch`, `similar`, `events`, `periods`,
  `successors`, `predecessors`, `timeline`, `nearby`
- `client.events.*` — `list`, `get`, `onThisDay`, `atDate`, `dateCoverage`, `periods`
- `client.periods.*` — `list`, `get`, `bySlug`, `atYear`
- `client.chains.*`, `client.cities.*`, `client.routes.*`, `client.search.*`
- Top-level: `snapshot`, `stats`, `compare`, `health`, `types`, `continents`

## License

Apache 2.0.

## Links

- **API**: https://atlaspi.cra-srl.com
- **Docs**: https://atlaspi.cra-srl.com/docs
- **Source**: https://github.com/Soil911/AtlasPI
