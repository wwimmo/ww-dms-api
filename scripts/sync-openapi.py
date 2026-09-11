#!/usr/bin/env python3
"""Holt die generierte OpenAPI-Spec, normalisiert sie deterministisch und schreibt YAML.

Quelle ist das Export-JSON aus dem Polaris-main-Build (`openapi/dms-api.v1.json`, von der
Azure-Pipeline auf den Branch `sync/openapi` gepusht) oder – für lokale Versuche – eine URL. Die Transformation ist bewusst deterministisch, damit `git diff` nur bei
echten Inhaltsänderungen anschlägt:

  * CRLF -> LF normalisieren,
  * doppelte Operation-`tags` deduplizieren (der Generator gibt "DMS" doppelt aus),
  * `info.x-generated-at` entfernen (sha + build-nummer identifizieren den Build; der Zeitstempel
    würde jeden Sync zu einem Diff machen – das Roh-JSON behält ihn),
  * festen `servers`-Block (nur Test) injizieren – wird NICHT aus der Quelle übernommen; Prod wird
    bewusst nicht publiziert, die URL erhalten Partner beim Onboarding (#21140),
  * als YAML mit Block-Skalaren ausgeben.

Aufruf:  python scripts/sync-openapi.py <quelle-url-oder-datei> <ausgabe.yaml>
"""

import json
import sys
import urllib.request

import yaml

# Fester servers-Block. Der Generator liefert keine servers; Prod wird nicht publiziert (#21140), die
# URL erhalten Partner beim Onboarding. Zwei Einträge: die Test-Sandbox und ein Template mit der
# Variable {host} OHNE enum – Swagger UI rendert daraus ein Dropdown plus ein freies Textfeld, in das
# ein Partner seinen Host (Prod-URL, eigener Proxy) einträgt. «Try it out» funktioniert nur gegen Hosts,
# die den Pages-Origin per CORS erlauben (heute: Test). Muss zu docs/3-referenz/1-authentifizierung.md passen.
SERVERS = [
    {"url": "https://erp-test.wwimmo.net", "description": "Test – Sandbox für Partner"},
    {
        "url": "https://{host}",
        "description": "Eigener Host, z. B. die beim Onboarding erhaltene Produktions-URL",
        "variables": {
            "host": {
                "default": "erp-test.wwimmo.net",
                "description": "Hostname ohne Schema und Pfad; der Pfadpräfix /api/v1/dms steht in den Operationen.",
            }
        },
    },
]


def normalize(value):
    """CRLF -> LF in allen Strings, rekursiv."""
    if isinstance(value, str):
        return value.replace("\r\n", "\n").replace("\r", "\n")
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize(val) for key, val in value.items()}
    return value


def load_source(source):
    if source.startswith("http://") or source.startswith("https://"):
        with urllib.request.urlopen(source, timeout=30) as response:  # noqa: S310 (vertrauenswürdige interne URL)
            return json.loads(response.read().decode("utf-8"))
    with open(source, encoding="utf-8") as handle:
        return json.load(handle)


def dedupe_operation_tags(spec):
    for operations in spec.get("paths", {}).values():
        for operation in operations.values():
            if isinstance(operation, dict) and isinstance(operation.get("tags"), list):
                seen = []
                for tag in operation["tags"]:
                    if tag not in seen:
                        seen.append(tag)
                operation["tags"] = seen


def inject_servers(spec):
    """servers direkt nach info einsetzen (Reihenfolge erhalten)."""
    rebuilt = {}
    for key, value in spec.items():
        if key == "servers":
            continue  # vorhandene servers verwerfen, eigene setzen
        rebuilt[key] = value
        if key == "info":
            rebuilt["servers"] = SERVERS
    if "servers" not in rebuilt:  # falls info fehlt (sollte nicht vorkommen)
        rebuilt["servers"] = SERVERS
    return rebuilt


def _str_representer(dumper, data):
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    source, output = sys.argv[1], sys.argv[2]

    spec = normalize(load_source(source))
    dedupe_operation_tags(spec)
    spec.get("info", {}).pop("x-generated-at", None)
    spec = inject_servers(spec)

    yaml.add_representer(str, _str_representer)
    with open(output, "w", encoding="utf-8", newline="\n") as handle:
        yaml.dump(
            spec,
            handle,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=100,
        )
    print(f"OpenAPI geschrieben: {output} ({len(spec.get('paths', {}))} Pfade)")


if __name__ == "__main__":
    main()
