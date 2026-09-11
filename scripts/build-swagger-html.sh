#!/usr/bin/env bash
# Baut eine eigenständige Swagger-UI-Seite: Spezifikation, swagger-ui.css und swagger-ui-bundle.js
# sind inline eingebettet. Die Datei läuft per Doppelklick aus dem Dateisystem, offline und ohne
# Webserver – als Download auf Pages, als PR-Artefakt, als E-Mail-Anhang. «Try it out» geht aus
# file:// nicht (die API erlaubt keinen file-Origin per CORS); dafür gibt es die Bruno-Collection.
#
# Aufruf:  scripts/build-swagger-html.sh <spec.yaml|spec.json> <ausgabe.html>
# Braucht: node/npm (js-yaml und swagger-ui-dist werden per npm geholt) und python3.
set -euo pipefail

SPEC="${1:?Pfad zur Spezifikation fehlt}"
OUT="${2:?Pfad der Ausgabedatei fehlt}"
# Bewusst gepinnt: ein Update ist eine Entscheidung, kein Nebeneffekt eines Builds.
SWAGGER_UI_VERSION="5.32.15"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

case "$SPEC" in
  *.json) cp "$SPEC" "$work/spec.json" ;;
  *)      npx --yes js-yaml@4 "$SPEC" > "$work/spec.json" ;;
esac

npm install --silent --no-save --no-audit --no-fund --prefix "$work" "swagger-ui-dist@$SWAGGER_UI_VERSION" > /dev/null

python3 - "$work/spec.json" "$work/node_modules/swagger-ui-dist" "$OUT" "$SWAGGER_UI_VERSION" <<'PY'
import json
import pathlib
import sys

spec_path, dist, out, version = sys.argv[1:5]
dist = pathlib.Path(dist)

# `</` würde ein <script>-Element vorzeitig schliessen; im JSON ist `<\/` dieselbe Zeichenkette.
spec = json.dumps(json.load(open(spec_path, encoding="utf-8")), ensure_ascii=False, separators=(",", ":"))
spec = spec.replace("</", "<\\/")
css = (dist / "swagger-ui.css").read_text(encoding="utf-8")
js = (dist / "swagger-ui-bundle.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
title = json.load(open(spec_path, encoding="utf-8")).get("info", {}).get("title", "API")

html = """<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>W&amp;W Immo __TITLE__ – Referenz (offline)</title>
    <style>__CSS__
      body { margin: 0; }</style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script>__JS__</script>
    <script>
      window.onload = () => {
        window.ui = SwaggerUIBundle({
          spec: __SPEC__,
          dom_id: '#swagger-ui',
          deepLinking: true,
          persistAuthorization: true,
        });
      };
    </script>
  </body>
</html>
"""
html = html.replace("__TITLE__", title).replace("__CSS__", css).replace("__JS__", js).replace("__SPEC__", spec)
pathlib.Path(out).write_text(html, encoding="utf-8", newline="\n")
print(f"Swagger-UI geschrieben: {out} ({pathlib.Path(out).stat().st_size // 1024} KB, swagger-ui-dist {version})")
PY
