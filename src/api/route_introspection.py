"""Introspezione version-proof delle route FastAPI (audit sicurezza /admin/*).

FastAPI >= 0.139 (con Starlette >= 1.0) ha reso *lazy* l'inclusione dei router:
``app.include_router(...)`` non appiattisce piu' le route in ``app.routes`` ma
registra un nodo interno ``_IncludedRouter`` con ``original_router`` (le route
figlie) e ``include_context`` (prefix + dependencies aggiunte alla include).
Iterare ``app.routes`` cercando path/dependant — come facevano lo startup-audit
di Wave 1.1 e tests/test_admin_auth.py — trova quindi 0 route /admin/* e rende
CIECO l'audit di sicurezza (regressione silenziosa: la protezione verify_admin
resta attiva, ma il guard che la verifica non vede piu' nulla).

# ETHICS/SECURITY: questo modulo esiste per mantenere VERIFICABILE la promessa
# "ogni /admin/* e' protetto da verify_admin" su qualsiasi versione di FastAPI.

``iter_effective_api_routes`` appiattisce ricorsivamente l'albero delle route e
restituisce, per ogni route HTTP, il path completo, i metodi e la catena
EFFETTIVA delle dependency callables (route-level dependant + dependencies
ereditate dagli include_context annidati). Funziona sia su FastAPI < 0.139
(lista gia' piatta, deps nel dependant) sia su >= 0.139 (albero lazy).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Any

RouteInfo = tuple[str, set[str], list[Callable[..., Any]]]


def iter_effective_api_routes(
    routes: Iterable[Any],
    prefix: str = "",
    inherited_deps: Sequence[Callable[..., Any]] = (),
) -> Iterator[RouteInfo]:
    """Yield ``(full_path, methods, effective_dependency_callables)``.

    - FastAPI >= 0.139: i nodi ``_IncludedRouter`` (riconosciuti via duck-typing
      su ``original_router``/``include_context``) vengono attraversati
      ricorsivamente, accumulando prefix e dependencies del contesto.
    - FastAPI < 0.139: le route sono gia' piatte e le dependencies della
      include sono gia' nel ``dependant`` della route — il ramo ricorsivo
      semplicemente non scatta.
    - Mount/static (senza ``methods``) vengono saltati: non sono route API.
    """
    for route in routes:
        original_router = getattr(route, "original_router", None)
        include_context = getattr(route, "include_context", None)
        if original_router is not None and include_context is not None:
            child_prefix = prefix + (getattr(include_context, "prefix", "") or "")
            ctx_deps = [
                dep.dependency
                for dep in (getattr(include_context, "dependencies", None) or [])
                if getattr(dep, "dependency", None) is not None
            ]
            yield from iter_effective_api_routes(
                original_router.routes,
                prefix=child_prefix,
                inherited_deps=[*inherited_deps, *ctx_deps],
            )
            continue

        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if not methods or path is None:
            continue

        deps: list[Callable[..., Any]] = list(inherited_deps)
        dependant = getattr(route, "dependant", None)
        if dependant is not None:
            deps.extend(
                dep.call
                for dep in (getattr(dependant, "dependencies", None) or [])
                if getattr(dep, "call", None) is not None
            )
        # route.dependencies copre le Depends dichiarate a livello route che
        # su alcune versioni non compaiono (ancora) risolte nel dependant.
        deps.extend(
            dep.dependency
            for dep in (getattr(route, "dependencies", None) or [])
            if getattr(dep, "dependency", None) is not None
        )
        yield prefix + path, set(methods), deps
