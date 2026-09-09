#!/usr/bin/env python3
"""Собирает index.html из landing.src.html и assets/.

    python3 build.py

Плейсхолдеры:
  __LOGO_SVG__  → инлайновый фирменный логотип (assets/logo.svg), ids разводятся
  __SWOOSH__    → assets/swoosh.svg как data-URI
  __TRUCK__     → assets/truck.png как data-URI

Правки вносите в landing.src.html — index.html пересобирается.
"""
import base64, pathlib, re, sys

here = pathlib.Path(__file__).parent
src  = (here / "landing.src.html").read_text(encoding="utf-8")


def data_uri(name, mime):
    return "data:%s;base64,%s" % (
        mime, base64.b64encode((here / "assets" / name).read_bytes()).decode("ascii"))


# ── логотип: инлайн-SVG, чтобы перекрашивать его на тёмных блоках ──
logo = (here / "assets" / "logo.svg").read_text(encoding="utf-8").strip()
logo = re.sub(r"<\?xml[^>]*\?>\s*", "", logo)
logo = logo.replace("<svg ", '<svg class="logo" role="img" aria-label="CarTaxi" ', 1)

seq = [0]
def one_logo(_m):
    seq[0] += 1
    # разводим id, чтобы два инстанса на странице не делили clip-path
    return re.sub(r'(id="|url\(#)([A-Za-z0-9_]+)', lambda m: m.group(1) + m.group(2) + "_%d" % seq[0], logo)

out_html = re.sub(r"__LOGO_SVG__", one_logo, src)
if seq[0] == 0:
    sys.exit("плейсхолдер __LOGO_SVG__ не найден")

for token, name, mime in (("__SWOOSH__", "swoosh.svg", "image/svg+xml"),
                          ("__TRUCK__",  "truck.png",  "image/png")):
    if token not in out_html:
        sys.exit("плейсхолдер %s не найден" % token)
    out_html = out_html.replace(token, data_uri(name, mime))

out = here / "index.html"
out.write_text(out_html, encoding="utf-8")
print("index.html — %.1f KB, логотипов: %d" % (out.stat().st_size / 1024, seq[0]))
