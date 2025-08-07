import csv, os, math, datetime, urllib.parse
from jinja2 import Environment, FileSystemLoader, select_autoescape

# ----------------------------
# CONFIG — adjust these first
# ----------------------------
SITE_NAME = "Your Site Name"
# Use your real Pages URL once you know it, e.g. https://<username>.github.io/<repo>
BASE_URL = "https://example.com"
OUTPUT_DIR = "site"  # GH Actions will deploy this folder
DATA_CSV = "data/products.csv"
TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "page_template.html"
PRICE_CURRENCY = "USD"

# URL structure for part pages (toner/ink are "cartridges")
SECTION = "cartridges"  # change later per-vertical if needed

# Optional limit while testing (None = all)
ROW_LIMIT = None

# ----------------------------
# Utilities
# ----------------------------

# ----------  SECTION + HOME INDEX HELPERS  ----------

PAGES_BY_SECTION = {}              # { "cartridges": [ (slug, title) , … ] }

def build_section_index(section: str) -> None:
    """Generate site/<section>/index.html with a live-filter search box."""
    items = PAGES_BY_SECTION.get(section, [])

    # 🔗 product cards --------------------------------------------------------
    cards_html = "\n".join(
        f"""
        <a class='card' data-title='{title.lower()}' href='{BASE_URL}/{section}/{slug}/'>
          <h3>{title}</h3>
          <p>Details →</p>
        </a>"""
        for slug, title in sorted(items, key=lambda x: x[1].lower())
    )

    # full HTML --------------------------------------------------------------
    html = f"""<!doctype html>
<html lang="en"><head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{section.capitalize()} – {SITE_NAME}</title>
  <link rel="canonical" href="{BASE_URL}/{section}/" />
  <style>
    :root{{--max:1100px;--muted:#6b7280;--b:#e5e7eb;--accent:#111827;--accent2:#0f172a}}
    *{{box-sizing:border-box}}
    body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,'Helvetica Neue',Arial;
         line-height:1.55;color:#111827;background:#fff}}
    .wrap{{max-width:var(--max);margin:0 auto;padding:32px 20px}}
    h1{{margin:0 0 24px;font-size:clamp(24px,5vw,34px)}}
    nav a{{font-size:14px;color:var(--accent);text-decoration:none}}
    nav a:hover{{text-decoration:underline}}

    .search{{max-width:500px;margin:10px 0 28px;display:flex}}
    .search input{{flex:1;padding:12px 14px;border:1px solid var(--b);border-radius:10px;font-size:16px}}

    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:24px}}
    .card{{border:1px solid var(--b);border-radius:16px;padding:22px 18px;text-decoration:none;
           color:var(--accent);background:#fff;transition:all .15s}}
    .card:hover{{box-shadow:0 6px 18px rgba(0,0,0,.06);transform:translateY(-2px)}}
    .card h3{{margin:0 0 6px;font-size:18px}}
    .card p{{margin:0;color:var(--muted);font-size:14px}}

    footer{{margin-top:48px;font-size:14px;color:var(--muted);text-align:center}}
  </style>
</head><body>
  <div class="wrap">
    <nav><a href="{BASE_URL}/">← Home</a></nav>
    <h1>{section.capitalize()}</h1>

    <!-- 🔍 Search bar -->
    <div class="search">
      <input id="itemSearch" type="search" placeholder="Search {section}…" aria-label="Search {section}">
    </div>

    <!-- product grid -->
    <section id="itemGrid" class="grid">
      {cards_html}
    </section>

    <footer>{len(items)} items · Last updated {today_iso()}</footer>
  </div>

  <!-- vanilla-JS live filter -->
  <script>
    const search = document.getElementById('itemSearch');
    const cards  = Array.from(document.querySelectorAll('#itemGrid .card'));
    search.addEventListener('input', e => {{
      const v = e.target.value.trim().toLowerCase();
      cards.forEach(c => {{
        const title = c.dataset.title;
        c.style.display = title.includes(v) ? '' : 'none';
      }});
    }});
  </script>
</body></html>"""
    write_text(os.path.join(OUTPUT_DIR, section, "index.html"), html)



def build_homepage_full() -> None:
    """Home page with live category search."""
    # ---------- category cards ---------- #
    cards_html = "\n".join(
        f"""
        <a class="card" data-name="{sec.lower()}" href="{BASE_URL}/{sec}/">
          <h3>{sec.capitalize()}</h3>
          <p>{len(items)} items →</p>
        </a>
        """
        for sec, items in sorted(PAGES_BY_SECTION.items())
    )

    # ---------- full HTML ---------- #
    html = f"""<!doctype html>
<html lang="en"><head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{SITE_NAME}</title>
  <link rel="canonical" href="{BASE_URL}/">
  <style>
    :root{{--max:1100px;--muted:#6b7280;--b:#e5e7eb;--accent:#111827;--accent2:#0f172a}}
    *{{box-sizing:border-box}}
    body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,'Helvetica Neue',Arial;
         line-height:1.55;color:#111827;background:#fff}}
    .wrap{{max-width:var(--max);margin:0 auto;padding:32px 20px}}
    header.hero{{text-align:center;margin-bottom:40px}}
    header.hero h1{{font-size:clamp(28px,6vw,40px);margin:0 0 10px}}
    header.hero p{{color:var(--muted);font-size:18px;margin:0 0 22px}}
    .search{{max-width:400px;margin:0 auto 34px;display:flex;}}
    .search input{{flex:1;padding:12px 14px;border:1px solid var(--b);border-radius:10px;font-size:16px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:24px}}
    .card{{border:1px solid var(--b);border-radius:16px;padding:22px 18px;text-decoration:none;
           color:var(--accent);background:#fff;transition:all .15s}}
    .card:hover{{box-shadow:0 6px 18px rgba(0,0,0,.06);transform:translateY(-2px)}}
    .card h3{{margin:0 0 6px;font-size:20px}}
    .card p{{margin:0;color:var(--muted)}}
    footer{{margin-top:48px;font-size:14px;color:var(--muted);text-align:center}}
  </style>
</head><body>
  <div class="wrap">
    <header class="hero">
      <h1>{SITE_NAME}</h1>
      <p>Your quick-lookup index for replacement parts & specs.</p>
    </header>

    <!-- 🔍 Search -->
    <div class="search">
      <input id="catSearch" type="search" placeholder="Search categories…" aria-label="Search categories">
    </div>

    <!-- category grid -->
    <section id="catGrid" class="grid">
      {cards_html}
    </section>

    <footer>
      Last updated {today_iso()} · <a href="{BASE_URL}/sitemap.xml">Sitemap</a>
    </footer>
  </div>

  <!-- Tiny vanilla-JS live filter -->
  <script>
    const q = document.getElementById('catSearch');
    const cards = Array.from(document.querySelectorAll('#catGrid .card'));
    q.addEventListener('input', e => {{
      const v = e.target.value.trim().toLowerCase();
      cards.forEach(c => {{
        const name = c.dataset.name;
        c.style.display = name.includes(v) ? '' : 'none';
      }});
    }});
  </script>
</body></html>"""
    write_text(os.path.join(OUTPUT_DIR, "index.html"), html)




def today_iso():
    return datetime.date.today().isoformat()

def cents_str(value):
    # e.g., 0.023 -> "2.3¢"; 0.1 -> "10.0¢"
    return f"{round(value*100, 2)}¢"

def safe_float(x, default=None):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except:
        return default

def safe_int(x, default=None):
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except:
        return default

def slugify(text):
    # Simple, dependency-free slugify
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-"
    text = (text or "").strip().lower()
    # replace separators with dash
    for ch in [" ", "_", "/", ".", ",", "|", "—", "–", "(", ")", "[", "]", "&", "+", "#", "'", '"', ":"]:
        text = text.replace(ch, "-")
    # collapse multiple dashes
    while "--" in text:
        text = text.replace("--", "-")
    # keep only allowed
    text = "".join(ch for ch in text if ch in allowed)
    return text.strip("-") or "item"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_text(path, content):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# ----------------------------
# Core generation
# ----------------------------

def load_rows(csv_path, row_limit=None):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            rows.append(row)
            if row_limit and i + 1 >= row_limit:
                break
    return rows

def compute_cpp(price, yield_pages):
    if price is None or yield_pages in (None, 0):
        return None, None
    cpp = price / yield_pages
    return cpp, cents_str(cpp)  # raw float, display string

def parse_compatible_models(raw):
    if not raw:
        return []
    # split on semicolon or comma
    parts = [p.strip() for p in raw.replace(",", ";").split(";")]
    return [p for p in parts if p]

def build_breadcrumbs(section, slug_path):
    # e.g., /cartridges/tn760/
    crumbs = [
        {"name": "Home", "url": BASE_URL + "/"},
        {"name": section.capitalize(), "url": f"{BASE_URL}/{section}/"},
    ]
    # optional: add more levels from slug path segments
    return crumbs

def page_output_path(section, slug):
    # /site/cartridges/<slug>/index.html
    return os.path.join(OUTPUT_DIR, section, slug, "index.html")

def page_url(section, slug):
    return f"{BASE_URL}/{section}/{slug}/"

def build_page_context(row):
    product_name = (row.get("product_name") or "").strip()
    model_number = (row.get("model_number") or "").strip()
    price = safe_float(row.get("price"))
    page_yield = safe_int(row.get("page_yield"))
    affiliate_url = (row.get("affiliate_url") or "").strip()

    cpp_raw, cpp_display = compute_cpp(price, page_yield)

    compatible_models = parse_compatible_models(row.get("compatible_models"))

    # Basic brand inference (optional; improve later)
    brand = None
    if product_name:
        brand = product_name.split()[0]

    # Offers list for the buy box & JSON-LD
    affiliate_offers = []
    if affiliate_url:
        affiliate_offers.append({
            "merchant": "Amazon" if "amazon." in affiliate_url else "Online",
            "url": affiliate_url,
            "price": price if price is not None else "",
            "currency": PRICE_CURRENCY,
            "in_stock": True,
        })

    # FAQs (basic defaults; you can enrich later)
    faqs = []
    if page_yield:
        faqs.append({"q": f"How long does {product_name} last?",
                     "a": f"About {page_yield} standard pages under ISO/IEC test conditions. Real-world results vary by coverage and settings."})
    if compatible_models:
        faqs.append({"q": f"Which printers are compatible with {product_name}?",
                     "a": "Compatible printers include: " + ", ".join(compatible_models) + "."})

    # Key points (value props)
    key_points = []
    if page_yield:
        key_points.append(f"Approx. yield: {page_yield} pages")
    if cpp_display:
        key_points.append(f"Cost per page: {cpp_display}")
    if compatible_models:
        key_points.append(f"{len(compatible_models)} compatible printers")

    # Sources (optional, fill later)
    sources = []

    # Slug: prefer model_number if available; fallback to product name
    raw_slug = model_number if model_number else product_name
    slug = slugify(raw_slug)

    ctx = {
        "site_name": SITE_NAME,
        "product_name": product_name,
        "model_number": model_number,
        "brand": brand,
        "price": price,
        "price_currency": PRICE_CURRENCY,
        "page_yield": page_yield,
        "cpp_display": cpp_display or "—",
        "compatible_models": compatible_models,
        "affiliate_url": affiliate_url,
        "affiliate_offers": affiliate_offers,
        "faqs": faqs,
        "key_points": key_points,
        "related_parts": [],
        "related_printers": [],
        "sources": sources,
        "last_updated": today_iso(),
        "indexable": True,
        "canonical_url": page_url(SECTION, slug),
        "breadcrumbs": build_breadcrumbs(SECTION, slug),
    }
    return ctx, slug

def render_pages(rows):
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl = env.get_template(TEMPLATE_FILE)

    urls = []

    for row in rows:
        ctx, slug = build_page_context(row)
        html = tpl.render(**ctx)
        out_path = page_output_path(SECTION, slug)
        write_text(out_path, html)
        urls.append(ctx["canonical_url"])

        # ⭐ NEW: remember this page for section index
        PAGES_BY_SECTION.setdefault(SECTION, []).append((slug, ctx["product_name"]))

    return urls

def build_homepage(urls):
    # Simple homepage that links to first N pages
    N = min(100, len(urls))
    links = "\n".join(f'<li><a href="{u}">{u}</a></li>' for u in urls[:N])
    html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_NAME} – Compatibility & Replacements</title>
<meta name="description" content="{SITE_NAME}: find compatible parts and replacements.">
<link rel="canonical" href="{BASE_URL}/" />
</head><body>
<div style="max-width:1000px;margin:0 auto;padding:24px;font-family:system-ui;">
  <h1>{SITE_NAME}</h1>
  <p>Find compatible parts and replacements for printers, filters, and chargers.</p>
  <h2>Latest pages</h2>
  <ul>{links}</ul>
</div>
</body></html>"""
    write_text(os.path.join(OUTPUT_DIR, "index.html"), html)

def build_sitemap(urls):
    # Single-file sitemap for now
    lastmod = today_iso()
    items = "\n".join(
        f"<url><loc>{urllib.parse.quote(u, safe=':/?&=')}</loc><lastmod>{lastmod}</lastmod></url>"
        for u in urls
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>{BASE_URL}/</loc><lastmod>{lastmod}</lastmod></url>
{items}
</urlset>"""
    write_text(os.path.join(OUTPUT_DIR, "sitemap.xml"), xml)

def build_robots():
    txt = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    write_text(os.path.join(OUTPUT_DIR, "robots.txt"), txt)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows = load_rows(DATA_CSV, row_limit=ROW_LIMIT)
    urls = render_pages(rows)

    # NEW: build category index and new home page
    build_section_index(SECTION)
    build_homepage_full()

    build_sitemap(urls)
    build_robots()
    print(f"Generated {len(urls)} pages into ./{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
