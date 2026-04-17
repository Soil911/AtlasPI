/**
 * atlaspi-client — JavaScript/TypeScript client for the AtlasPI API.
 *
 * Quick start:
 *
 *   import { AtlasPI } from 'atlaspi-client';
 *   const client = new AtlasPI();
 *   const snapshot = await client.snapshot(1250);
 *   const similar = await client.entities.similar(1, { limit: 5 });
 *   const today = await client.events.onThisDay('07-14');
 *
 * Free, public, no-auth API. 862 entities + 490 events + 94 dynasty chains
 * from 4500 BCE to 2024.
 *
 * Docs: https://atlaspi.cra-srl.com/docs
 * Source: https://github.com/Soil911/AtlasPI
 */

export const VERSION = "0.1.0";
export const DEFAULT_BASE_URL = "https://atlaspi.cra-srl.com";

export class AtlasPIError extends Error {
  public readonly statusCode?: number;
  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = "AtlasPIError";
    this.statusCode = statusCode;
  }
}

export interface ClientOptions {
  baseUrl?: string;
  timeout?: number; // ms
  userAgent?: string;
  fetch?: typeof fetch;
}

// ─── Minimal types for common responses (loose — the API is evolving) ────

export interface EntitySummary {
  id: number;
  name_original: string;
  entity_type: string;
  year_start: number;
  year_end?: number | null;
  confidence_score?: number;
  status?: string;
}

export interface EntityDetail extends EntitySummary {
  name_original_lang: string;
  capital?: { name: string; lat: number; lon: number } | null;
  boundary_geojson?: Record<string, unknown> | null;
  boundary_source?: string | null;
  name_variants?: Array<{ name: string; lang: string }>;
  sources?: Array<Record<string, unknown>>;
  ethical_notes?: string | null;
  continent?: string;
}

export interface BatchResponse {
  requested: number;
  found: number;
  not_found: number[];
  entities: EntityDetail[];
}

export interface SnapshotResponse {
  year: number;
  year_display: string;
  periods: { total: number; items: Array<Record<string, unknown>> };
  entities: { total_active: number; by_type: Record<string, number>; top_by_confidence: EntitySummary[] };
  events_that_year: { total: number; items: Array<Record<string, unknown>> };
  cities: { total_active: number; by_type: Record<string, number>; top: Array<Record<string, unknown>> };
  chains: { total_active: number; items: Array<Record<string, unknown>> };
}

// ─── Main client ──────────────────────────────────────────────────────────

export class AtlasPI {
  private readonly baseUrl: string;
  private readonly timeout: number;
  private readonly userAgent: string;
  private readonly fetchFn: typeof fetch;

  public readonly entities: EntitiesNamespace;
  public readonly events: EventsNamespace;
  public readonly periods: PeriodsNamespace;
  public readonly chains: ChainsNamespace;
  public readonly cities: CitiesNamespace;
  public readonly routes: RoutesNamespace;
  public readonly search: SearchNamespace;

  constructor(options: ClientOptions = {}) {
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, "");
    this.timeout = options.timeout ?? 30_000;
    this.userAgent = options.userAgent ?? `atlaspi-client-js/${VERSION}`;
    this.fetchFn = options.fetch ?? fetch;
    this.entities = new EntitiesNamespace(this);
    this.events = new EventsNamespace(this);
    this.periods = new PeriodsNamespace(this);
    this.chains = new ChainsNamespace(this);
    this.cities = new CitiesNamespace(this);
    this.routes = new RoutesNamespace(this);
    this.search = new SearchNamespace(this);
  }

  // ─── Top-level shortcuts ─────────────────────────────────────────────

  async snapshot(year: number, options: { topN?: number } = {}): Promise<SnapshotResponse> {
    const params: Record<string, unknown> = {};
    if (options.topN !== undefined) params.top_n = options.topN;
    return this._get<SnapshotResponse>(`/v1/snapshot/year/${year}`, params);
  }

  async stats(): Promise<Record<string, unknown>> {
    return this._get("/v1/stats");
  }

  async compare(idA: number, idB: number): Promise<Record<string, unknown>> {
    return this._get(`/v1/compare/${idA}/${idB}`);
  }

  async health(): Promise<{ status: string; version: string }> {
    return this._get("/health");
  }

  async types(): Promise<Array<{ type: string; count: number }>> {
    return this._get("/v1/types");
  }

  async continents(): Promise<Array<{ continent: string; count: number }>> {
    return this._get("/v1/continents");
  }

  // ─── Internal HTTP ───────────────────────────────────────────────────

  async _get<T = unknown>(path: string, params?: Record<string, unknown>): Promise<T> {
    const url = new URL(this.baseUrl + path);
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
      }
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);
    try {
      const res = await this.fetchFn(url.toString(), {
        headers: { "User-Agent": this.userAgent, Accept: "application/json" },
        signal: controller.signal,
      });
      if (!res.ok) {
        let detail = "";
        try { detail = await res.text(); } catch {}
        throw new AtlasPIError(
          `HTTP ${res.status} for ${path}: ${detail.substring(0, 200)}`,
          res.status,
        );
      }
      const ct = res.headers.get("content-type") ?? "";
      if (ct.includes("application/json")) {
        return (await res.json()) as T;
      }
      return (await res.text()) as unknown as T;
    } catch (e: unknown) {
      if (e instanceof AtlasPIError) throw e;
      const msg = e instanceof Error ? e.message : String(e);
      throw new AtlasPIError(`Network error for ${path}: ${msg}`);
    } finally {
      clearTimeout(timer);
    }
  }
}

// ─── Namespaces ──────────────────────────────────────────────────────────

class EntitiesNamespace {
  constructor(private readonly client: AtlasPI) {}

  async list(params: Record<string, unknown> = {}): Promise<{ entities: EntitySummary[]; count: number }> {
    return this.client._get("/v1/entities", params);
  }

  async get(id: number): Promise<EntityDetail> {
    return this.client._get(`/v1/entities/${id}`);
  }

  async batch(ids: number[]): Promise<BatchResponse> {
    return this.client._get("/v1/entities/batch", { ids: ids.join(",") });
  }

  async similar(
    id: number,
    options: { limit?: number; minScore?: number } = {},
  ): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/entities/${id}/similar`, {
      limit: options.limit,
      min_score: options.minScore,
    });
  }

  async events(id: number): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/entities/${id}/events`);
  }

  async periods(id: number, options: { region?: string } = {}): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/entities/${id}/periods`, options.region ? { region: options.region } : {});
  }

  async successors(id: number): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/entities/${id}/successors`);
  }

  async predecessors(id: number): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/entities/${id}/predecessors`);
  }

  async timeline(id: number): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/entities/${id}/timeline`);
  }

  async nearby(opts: { lat: number; lon: number; year: number; radiusKm?: number }): Promise<Record<string, unknown>> {
    return this.client._get("/v1/nearby", {
      lat: opts.lat, lon: opts.lon, year: opts.year, radius_km: opts.radiusKm,
    });
  }
}

class EventsNamespace {
  constructor(private readonly client: AtlasPI) {}

  async list(params: Record<string, unknown> = {}): Promise<Record<string, unknown>> {
    return this.client._get("/v1/events", params);
  }

  async get(id: number): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/events/${id}`);
  }

  async onThisDay(mmDd: string): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/events/on-this-day/${mmDd}`);
  }

  async atDate(isoDate: string): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/events/at-date/${isoDate}`);
  }

  async dateCoverage(): Promise<Record<string, unknown>> {
    return this.client._get("/v1/events/date-coverage");
  }

  async periods(id: number, options: { region?: string } = {}): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/events/${id}/periods`, options.region ? { region: options.region } : {});
  }
}

class PeriodsNamespace {
  constructor(private readonly client: AtlasPI) {}

  async list(params: Record<string, unknown> = {}): Promise<Record<string, unknown>> {
    return this.client._get("/v1/periods", params);
  }

  async get(id: number): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/periods/${id}`);
  }

  async bySlug(slug: string): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/periods/by-slug/${slug}`);
  }

  async atYear(year: number, options: { region?: string } = {}): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/periods/at-year/${year}`, options.region ? { region: options.region } : {});
  }
}

class ChainsNamespace {
  constructor(private readonly client: AtlasPI) {}
  async list(params: Record<string, unknown> = {}): Promise<Record<string, unknown>> {
    return this.client._get("/v1/chains", params);
  }
  async get(id: number): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/chains/${id}`);
  }
}

class CitiesNamespace {
  constructor(private readonly client: AtlasPI) {}
  async list(params: Record<string, unknown> = {}): Promise<Record<string, unknown>> {
    return this.client._get("/v1/cities", params);
  }
  async get(id: number): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/cities/${id}`);
  }
}

class RoutesNamespace {
  constructor(private readonly client: AtlasPI) {}
  async list(params: Record<string, unknown> = {}): Promise<Record<string, unknown>> {
    return this.client._get("/v1/routes", params);
  }
  async get(id: number): Promise<Record<string, unknown>> {
    return this.client._get(`/v1/routes/${id}`);
  }
}

class SearchNamespace {
  constructor(private readonly client: AtlasPI) {}
  async fuzzy(q: string, options: { limit?: number } = {}): Promise<Record<string, unknown>> {
    return this.client._get("/v1/search/fuzzy", { q, limit: options.limit });
  }
  async advanced(q: string, params: Record<string, unknown> = {}): Promise<Record<string, unknown>> {
    return this.client._get("/v1/search/advanced", { q, ...params });
  }
  async autocomplete(q: string, options: { limit?: number } = {}): Promise<Record<string, unknown>> {
    return this.client._get("/v1/search", { q, limit: options.limit });
  }
}
