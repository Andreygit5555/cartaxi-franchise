#!/usr/bin/env python3
"""Собирает index.html из landing.src.html и assets/.

    python3 build.py

Страницы:
  landing.src.html → index.html      (франшиза)
  fix.src.html     → fix/index.html  (фрахт)

Плейсхолдеры:
  __LOGO_SVG__  → инлайновый фирменный логотип (assets/logo.svg), ids разводятся
  __SWOOSH__    → assets/swoosh.svg как data-URI
  __TRUCK__     → assets/truck.png как data-URI

Правки вносите в *.src.html — собранные страницы пересобираются.
"""
import base64, pathlib, re, sys

here = pathlib.Path(__file__).parent

PAGES = [("landing.src.html", "index.html"),
         ("fix.src.html",     "fix/index.html")]


def data_uri(name, mime):
    return "data:%s;base64,%s" % (
        mime, base64.b64encode((here / "assets" / name).read_bytes()).decode("ascii"))


ASSETS = {"__SWOOSH__": ("swoosh.svg", "image/svg+xml"),
          "__TRUCK__":  ("truck.png",  "image/png")}

# логотип: инлайн-SVG, чтобы перекрашивать его на тёмных блоках
logo = (here / "assets" / "logo.svg").read_text(encoding="utf-8").strip()
logo = re.sub(r"<\?xml[^>]*\?>\s*", "", logo)
logo = logo.replace("<svg ", '<svg class="logo" role="img" aria-label="CarTaxi" ', 1)

for src_name, out_name in PAGES:
    src_path = here / src_name
    if not src_path.exists():
        sys.exit("нет исходника %s" % src_name)
    html = src_path.read_text(encoding="utf-8")

    seq = [0]
    def one_logo(_m):
        seq[0] += 1
        # разводим id, чтобы два инстанса на странице не делили clip-path
        return re.sub(r'(id="|url\(#)([A-Za-z0-9_]+)',
                      lambda m: m.group(1) + m.group(2) + "_%d" % seq[0], logo)

    html = re.sub(r"__LOGO_SVG__", one_logo, html)
    if seq[0] == 0:
        sys.exit("%s: плейсхолдер __LOGO_SVG__ не найден" % src_name)

    for token, (name, mime) in ASSETS.items():
        if token not in html:
            sys.exit("%s: плейсхолдер %s не найден" % (src_name, token))
        html = html.replace(token, data_uri(name, mime))

    left = re.findall(r"__[A-Z][A-Z_]*__", html)
    if left:
        sys.exit("%s: остались плейсхолдеры %s" % (src_name, sorted(set(left))))

    out = here / out_name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("%-14s → %.1f KB, логотипов: %d" % (out_name, out.stat().st_size / 1024, seq[0]))
