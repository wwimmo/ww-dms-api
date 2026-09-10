#!/usr/bin/env python3
"""Prüft die handgeschriebene Doku und die Bruno-Collection gegen die OpenAPI-Spezifikation.

Die Spezifikation wird aus dem Code generiert und per Sync-PR aktualisiert; die Prosa in `docs/`,
das `README.md` und die `.bru`-Requests nicht. Dieses Skript macht Drift sichtbar, statt ihn
stillschweigend liegen zu lassen – es läuft in jedem PR und im Sync-Workflow.

Geprüft wird:
  1. Jeder in Doku oder Bruno referenzierte Endpunkt (`GET /pfad`, `{{baseUrl}}/pfad`,
     `/api/v1/dms/pfad`) existiert in der Spezifikation, samt HTTP-Methode.
  2. Jeder Spezifikations-Pfad kommt im README (Abschnitt «Was die Spezifikation abdeckt») vor.
  3. Verbotene Begriffe (veraltete Hosts, widerlegte Aussagen, Platzhalter-Markierungen).
  4. JSON-Bodies der Bruno-Requests passen zum Request-Schema: keine unbekannten Eigenschaften,
     keine fehlenden Pflichtfelder (rekursiv; Typen werden nicht geprüft, `{{platzhalter}}` gelten
     als gesetzt).

Aufruf:  python scripts/check-docs-against-spec.py [openapi/dms-api.v1.yaml]
Exit 0 ohne Befund, 1 mit Befunden (je Zeile `datei:zeile: meldung`).
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
PREFIX = "/api/v1/dms"
DOC_FILES = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md")), ROOT / "bruno" / "README.md"]
BRU_FILES = sorted((ROOT / "bruno").rglob("*.bru"))
METHODS = ("get", "post", "put", "patch", "delete")

# (Regex, Begründung). CHANGELOG.md ist ausgenommen: dort dürfen alte Namen historisch vorkommen.
FORBIDDEN = [
    (r"wwimmo\.ch\b", "veralteter Host – die Partner-Hosts enden auf wwimmo.net (#21140)"),
    (r"wwportal-dev\.ch", "die Dev-Instanz gehört nicht in die Partner-Doku"),
    (r"\berp\.wwimmo\.net", "die Prod-URL wird beim Onboarding mitgeteilt, nicht publiziert"),
    (r"octet-stream", "der Content-Download liefert den gespeicherten MIME-Typ, kein octet-stream"),
    (r"Soft-Delete", "DELETE löscht physisch, kein Soft-Delete"),
    (r"X-RateLimit-Limit", "diesen Header sendet die API nicht"),
    (r"\(in Arbeit\)", "Platzhalter-Markierung – fertigstellen oder als Follow-up benennen"),
    (r"InvoiceUploadRequest", "so heisst das Schema nicht mehr; über den Endpunkt referenzieren"),
    (r"beide erforderlich", "changed_since und changed_until sind optional"),
    (r"curl -sL\b", "kein Redirect beim Download, -L ist irreführend"),
]

ENDPOINT_RE = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE)\s+`?(?:\{[^}]*\})?((?:/api/v1/dms)?/[A-Za-z0-9_\-{}<>:./]*)"
)
BRU_METHOD_RE = re.compile(r"^(get|post|put|patch|delete)\s*\{", re.MULTILINE)
BRU_URL_RE = re.compile(r"^\s*url:\s*(\S+)", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")


def normalize(path: str) -> str:
    """Pfad vergleichbar machen: Prefix und Query weg, Parameter auf `{}` vereinheitlichen."""
    path = path.split("?", 1)[0].split("#", 1)[0].rstrip("`.,;:)")
    if path.startswith(PREFIX):
        path = path[len(PREFIX):]
    # Bruno-Variablen ({{id}}) zuerst, sonst bleibt von der äusseren Klammer ein `}` stehen.
    path = re.sub(r"\{\{[^}]*\}\}", "{}", path)
    path = re.sub(r"\{[^}]*\}|<[^>]*>", "{}", path)
    return path.rstrip("/") or "/"


def load_spec(spec_path: pathlib.Path) -> dict:
    with open(spec_path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def spec_operations(spec: dict) -> dict[str, set[str]]:
    operations: dict[str, set[str]] = {}
    for path, item in spec.get("paths", {}).items():
        operations.setdefault(normalize(path), set()).update(m for m in item if m in METHODS)
    return operations


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check_doc_endpoints(operations: dict[str, set[str]], errors: list[str]) -> None:
    for file in DOC_FILES:
        if not file.exists():
            continue
        text = file.read_text(encoding="utf-8")
        for match in ENDPOINT_RE.finditer(text):
            method, raw = match.group(1).lower(), match.group(2)
            if raw in ("/", "") or raw.startswith("/api/") and not raw.startswith(PREFIX):
                continue
            path = normalize(raw)
            where = f"{file.relative_to(ROOT)}:{line_of(text, match.start())}"
            if path not in operations:
                errors.append(f"{where}: Endpunkt `{method.upper()} {raw}` existiert nicht in der Spezifikation")
            elif method not in operations[path]:
                errors.append(f"{where}: `{method.upper()} {raw}` – Methode nicht in der Spezifikation "
                              f"(erlaubt: {', '.join(sorted(m.upper() for m in operations[path]))})")


def check_readme_coverage(operations: dict[str, set[str]], errors: list[str]) -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for path in sorted(operations):
        segment = "/" + path.split("/")[1]
        if not re.search(re.escape(segment) + r"(?![A-Za-z0-9_-])", readme):
            errors.append(f"README.md: Spezifikations-Pfad `{segment}` fehlt im Abschnitt «Was die Spezifikation abdeckt»")


def check_forbidden_terms(errors: list[str]) -> None:
    for file in DOC_FILES + BRU_FILES:
        if not file.exists():
            continue
        text = file.read_text(encoding="utf-8")
        for pattern, reason in FORBIDDEN:
            for match in re.finditer(pattern, text):
                errors.append(f"{file.relative_to(ROOT)}:{line_of(text, match.start())}: `{match.group(0)}` – {reason}")


def resolve(schema: dict, spec: dict) -> dict:
    while isinstance(schema, dict) and "$ref" in schema:
        node: object = spec
        for part in schema["$ref"].lstrip("#/").split("/"):
            node = node[part.replace("~1", "/").replace("~0", "~")]
        schema = node  # type: ignore[assignment]
    if isinstance(schema, dict) and "allOf" in schema:
        merged: dict = {"properties": {}, "required": []}
        for part in schema["allOf"]:
            part = resolve(part, spec)
            merged["properties"].update(part.get("properties", {}))
            merged["required"].extend(part.get("required", []))
        return merged
    return schema


def check_body(schema: dict, value: object, spec: dict, where: str, errors: list[str]) -> None:
    schema = resolve(schema, spec)
    if isinstance(value, dict):
        properties = schema.get("properties")
        if properties is None:
            return
        for key in value:
            if key not in properties:
                errors.append(f"{where}: Eigenschaft `{key}` kennt das Request-Schema nicht")
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{where}: Pflichtfeld `{key}` fehlt im Body")
        for key, child in value.items():
            if key in properties:
                check_body(properties[key], child, spec, f"{where}.{key}", errors)
    elif isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            check_body(schema["items"], item, spec, f"{where}[{index}]", errors)


def extract_bru_body(text: str) -> str | None:
    start = text.find("body:json {")
    if start < 0:
        return None
    lines = text[start:].split("\n")[1:]
    body: list[str] = []
    for line in lines:
        if line.rstrip() == "}":
            break
        body.append(line)
    raw = "\n".join(body)
    # Platzhalter: in Anführungszeichen bleiben sie Strings, nackte werden zu 0.
    raw = re.sub(r'"\{\{[^}]+\}\}"', '"platzhalter"', raw)
    raw = PLACEHOLDER_RE.sub("0", raw)
    return raw


def check_bruno(spec: dict, operations: dict[str, set[str]], errors: list[str]) -> None:
    for file in BRU_FILES:
        text = file.read_text(encoding="utf-8")
        where = str(file.relative_to(ROOT))
        method_match, url_match = BRU_METHOD_RE.search(text), BRU_URL_RE.search(text)
        if not method_match or not url_match:
            continue
        method, url = method_match.group(1), url_match.group(1)
        path = normalize(re.sub(r"^\{\{baseUrl\}\}", "", url))
        if path not in operations:
            errors.append(f"{where}: Request-URL `{url}` zeigt auf keinen Pfad der Spezifikation")
            continue
        if method not in operations[path]:
            errors.append(f"{where}: Methode {method.upper()} gibt es für `{path}` nicht in der Spezifikation")
            continue
        body = extract_bru_body(text)
        if body is None:
            continue
        spec_path = next(p for p in spec["paths"] if normalize(p) == path)
        schema = (spec["paths"][spec_path][method].get("requestBody", {})
                  .get("content", {}).get("application/json", {}).get("schema"))
        if schema is None:
            errors.append(f"{where}: Request hat einen JSON-Body, die Spezifikation für {method.upper()} {path} aber keinen")
            continue
        try:
            value = json.loads(body)
        except json.JSONDecodeError as error:
            errors.append(f"{where}: Body ist kein gültiges JSON ({error.msg})")
            continue
        check_body(schema, value, spec, f"{where} body", errors)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows-Konsolen sind sonst cp1252
    spec_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "openapi" / "dms-api.v1.yaml"
    spec = load_spec(spec_path)
    operations = spec_operations(spec)
    errors: list[str] = []
    check_doc_endpoints(operations, errors)
    check_readme_coverage(operations, errors)
    check_forbidden_terms(errors)
    check_bruno(spec, operations, errors)
    for error in errors:
        print(error)
    print(f"{len(errors)} Befund(e); {len(operations)} Pfade in {spec_path.relative_to(ROOT) if spec_path.is_relative_to(ROOT) else spec_path}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
