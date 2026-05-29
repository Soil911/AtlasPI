"""Wave 2.2 (audit security #3): la chiave del rate limiter è l'IP reale del client.

Dietro nginx, request.client.host è l'IP del proxy: senza X-Real-IP tutti i
client condividerebbero un unico bucket globale (un client aggressivo → 429
per tutti). Verifichiamo che _client_ip_key usi X-Real-IP (impostato da nginx,
non falsificabile) e che client diversi ottengano chiavi diverse.
"""
from types import SimpleNamespace

from src.middleware.rate_limit import _client_ip_key


def _req(headers, client_host="172.18.0.5"):
    # request.headers di Starlette è case-insensitive; qui usiamo chiavi
    # già lowercase per il SimpleNamespace di test (la key_func legge "x-real-ip").
    return SimpleNamespace(
        headers={k.lower(): v for k, v in headers.items()},
        client=SimpleNamespace(host=client_host),
    )


def test_uses_x_real_ip_when_present():
    assert _client_ip_key(_req({"X-Real-IP": "203.0.113.7"})) == "203.0.113.7"


def test_two_clients_behind_same_proxy_get_distinct_keys():
    # Stesso proxy host, X-Real-IP diversi → bucket distinti, non un unico globale.
    a = _client_ip_key(_req({"X-Real-IP": "203.0.113.1"}, client_host="172.18.0.5"))
    b = _client_ip_key(_req({"X-Real-IP": "203.0.113.2"}, client_host="172.18.0.5"))
    assert a != b


def test_fallback_to_remote_address_without_header():
    # Dev/locale senza proxy: nessun X-Real-IP → fallback a request.client.host.
    assert _client_ip_key(_req({}, client_host="127.0.0.1")) == "127.0.0.1"


def test_real_ip_is_trimmed():
    assert _client_ip_key(_req({"X-Real-IP": " 203.0.113.9 "})) == "203.0.113.9"
