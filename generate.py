import csv, os, math, datetime, urllib.parse
from jinja2 import Environment, FileSystemLoader, select_autoescape

# ----------------------------
# CONFIG — adjust these first
# ----------------------------
SITE_NAME = "PartLookup"
# Use your real Pages URL once you know it, e.g. https://<username>.github.io/<repo>
BASE_URL = "https://tydeck1016.github.io/ai-seo-project"

# IMPORTANT: GitHub Pages set to /docs, so publish there
OUTPUT_DIR = "docs"

DATA_CSV = "data/products.csv"
# optional multi-merchant offer file (can omit)
AFFILIATE_OFFERS_CSV = "data/offers.csv"

TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "page_template.html"
PRICE_CURRENCY = "USD"

# Your Amazon Associates tracking ID
AFFILIATE_AMAZON_TAG = "easyproduc07b-20"

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
    """Section page with top bar, gradient hero, live product search, theme toggle."""
    items = PAGES_BY_SECTION.get(section, [])
    cards_html = "\n".join(
        f"""
        <a class='card' data-title='{title.lower()}' href='{BASE_URL}/{section}/{slug}/'>
          <h3>{title}</h3>
          <p>Details →</p>
        </a>"""
        for slug, title in sorted(items, key=lambda x: x[1].lower())
    )

    html = f"""<!doctype html>
<html lang="en" data-theme="auto">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{section.capitalize()} – {SITE_NAME}</title>
  <link rel="canonical" href="{BASE_URL}/{section}/" />
  <style>
    :root{{
      --bg:#0b1020; --surface:#0f1428; --card:#ffffff; --ink:#0b1220; --muted:#687089;
      --b:#e7e8ef; --accent:#3b82f6; --accent-2:#1d4ed8; --chip:#f2f5ff;
      --max:1200px; --pad:18px; --radius:16px; --shadow:0 8px 30px rgba(10,20,30,.08);
    }}
    html[data-theme="dark"] :root, :root[data-theme="dark"]{{ 
      --card:#0f172a; --ink:#e5e7ef; --b:#1f2937; --chip:#111827;
    }}
    @media (prefers-color-scheme: dark) {{
      html[data-theme="auto"] :root{{ --card:#0f172a; --ink:#e5e7ef; --b:#1f2937; --chip:#111827; }}
      html[data-theme="auto"] body{{ background:#0b1020; }}
    }}
    *{{box-sizing:border-box}} html,body{{margin:0}}
    body{{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,"Helvetica Neue",Arial;
         line-height:1.6; background:var(--bg); color:var(--ink)}}

    .topbar{{background:linear-gradient(180deg, var(--surface), rgba(15,23,42,.6)); color:#fff}}
    .topbar .wrap{{max-width:var(--max); margin:0 auto; padding:14px var(--pad);
                   display:flex; align-items:center; gap:14px; justify-content:space-between}}
    .brand{{display:flex; align-items:center; gap:10px; text-decoration:none; color:#fff; font-weight:800}}
    .logo{{width:28px;height:28px;border-radius:10px;background:linear-gradient(135deg,#60a5fa,#a78bfa);
           box-shadow:inset 0 0 0 2px rgba(255,255,255,.2)}}
    .nav a{{color:#cbd5e1;text-decoration:none;font-weight:600;margin-left:14px}}
    .nav a:hover{{color:#fff}}
    .theme-btn{{appearance:none;border:1px solid rgba(255,255,255,.25);background:transparent;color:#fff;
                padding:8px 10px;border-radius:10px;cursor:pointer;font-weight:700}}

    .hero{{background:
      radial-gradient(1200px 400px at 20% -10%, rgba(59,130,246,.35), transparent 60%),
      radial-gradient(900px 300px at 90% -20%, rgba(167,139,250,.28), transparent 60%),
      linear-gradient(180deg, rgba(15,23,42,.9), rgba(15,23,42,.66)); color:#fff; border-bottom:1px solid rgba(255,255,255,.06)}}
    .hero .wrap{{max-width:var(--max); margin:0 auto; padding:28px var(--pad) 34px}}
    .breadcrumbs{{font-size:13px; color:#94a3b8; margin-bottom:8px}}
    .breadcrumbs a{{color:inherit; text-decoration:none}}
    h1{{font-size:clamp(24px,5vw,36px); margin:8px 0 0}}

    .wrap{{max-width:var(--max); margin:0 auto; padding:32px 20px}}
    .search{{max-width:520px; margin:18px 0 28px; display:flex}}
    .search input{{flex:1;padding:12px 14px;border:1px solid var(--b);border-radius:12px;font-size:16px;background:var(--card);color:var(--ink)}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:24px}}
    .card{{border:1px solid var(--b);border-radius:16px;padding:22px 18px;text-decoration:none;color:var(--ink);
           background:var(--card);transition:all .15s; box-shadow:var(--shadow)}}
    .card:hover{{transform:translateY(-2px); box-shadow:0 10px 28px rgba(0,0,0,.10)}}
    .card h3{{margin:0 0 6px;font-size:18px}}
    .card p{{margin:0;color:var(--muted);font-size:14px}}
    footer{{margin-top:24px;text-align:center;color:#94a3b8;font-size:13px}}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="wrap">
      <a class="brand" href="{BASE_URL}/"><div class="logo"></div><span>{SITE_NAME}</span></a>
      <div class="nav">
        <a href="{BASE_URL}/{section}/">{section.capitalize()}</a>
        <button id="themeToggle" class="theme-btn" type="button">Toggle theme</button>
      </div>
    </div>
  </div>

  <div class="hero">
    <div class="wrap">
      <div class="breadcrumbs"><a href="{BASE_URL}/">Home</a> › <a href="{BASE_URL}/{section}/">{section.capitalize()}</a></div>
      <h1>{section.capitalize()}</h1>
    </div>
  </div>

  <div class="wrap">
    <div class="search"><input id="itemSearch" type="search" placeholder="Search {section}…" aria-label="Search {section}"></div>
    <section id="itemGrid" class="grid">{cards_html}</section>
    <footer>{len(items)} items · Last updated {today_iso()}</footer>
  </div>

  <script>
    // Live filter
    const search = document.getElementById('itemSearch');
    const cards  = Array.from(document.querySelectorAll('#itemGrid .card'));
    search?.addEventListener('input', e => {{
      const v = e.target.value.trim().toLowerCase();
      cards.forEach(c => {{
        const title = c.dataset.title || '';
        c.style.display = title.includes(v) ? '' : 'none';
      }});
    }});

    // Theme toggle (persists)
    const root = document.documentElement;
    const key = 'theme-pref';
    function applyTheme(t) {{ root.setAttribute('data-theme', t); }}
    const saved = localStorage.getItem(key);
    if (saved) applyTheme(saved);
    document.getElementById('themeToggle').addEventListener('click', () => {{
      const cur = root.getAttribute('data-theme') || 'auto';
      const next = cur === 'dark' ? 'light' : (cur === 'light' ? 'auto' : 'dark');
      localStorage.setItem(key, next); applyTheme(next);
    }});
  </script>
</body></html>"""
    write_text(os.path.join(OUTPUT_DIR, section, "index.html"), html)


def build_homepage_full() -> None:
    """Home page with top bar, gradient hero, live category search, theme toggle."""
    # category cards
    cards_html = "\n".join(
        f"""
        <a class="card" data-name="{sec.lower()}" href="{BASE_URL}/{sec}/">
          <h3>{sec.capitalize()}</h3>
          <p>{len(items)} items →</p>
        </a>
        """
        for sec, items in sorted(PAGES_BY_SECTION.items())
    )

    html = f"""<!doctype html>
<html lang="en" data-theme="auto">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{SITE_NAME}</title>
  <link rel="canonical" href="{BASE_URL}/">
  <style>
    :root{{
      --bg:#0b1020; --surface:#0f1428; --card:#ffffff; --ink:#0b1220; --muted:#687089;
      --b:#e7e8ef; --accent:#3b82f6; --accent-2:#1d4ed8; --chip:#f2f5ff;
      --max:1200px; --pad:18px; --radius:16px; --shadow:0 8px 30px rgba(10,20,30,.08);
    }}
    /* Dark theme vars (preferred if data-theme=dark) */
    html[data-theme="dark"] :root, :root[data-theme="dark"]{{ 
      --card:#0f172a; --ink:#e5e7ef; --b:#1f2937; --chip:#111827;
    }}
    /* Fallback to OS preference if user hasn't chosen */
    @media (prefers-color-scheme: dark) {{
      html[data-theme="auto"] :root{{ --card:#0f172a; --ink:#e5e7ef; --b:#1f2937; --chip:#111827; }}
      html[data-theme="auto"] body{{ background:#0b1020; }}
    }}
    *{{box-sizing:border-box}} html,body{{margin:0}}
    body{{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,"Helvetica Neue",Arial;
         line-height:1.6; background:var(--bg); color:var(--ink)}}

    /* Topbar */
    .topbar{{background:linear-gradient(180deg, var(--surface), rgba(15,23,42,.6)); color:#fff}}
    .topbar .wrap{{max-width:var(--max); margin:0 auto; padding:14px var(--pad);
                   display:flex; align-items:center; gap:14px; justify-content:space-between}}
    .brand{{display:flex; align-items:center; gap:10px; text-decoration:none; color:#fff; font-weight:800}}
    .logo{{width:28px;height:28px;border-radius:10px;background:linear-gradient(135deg,#60a5fa,#a78bfa);
           box-shadow:inset 0 0 0 2px rgba(255,255,255,.2)}}
    .nav a{{color:#cbd5e1;text-decoration:none;font-weight:600;margin-left:14px}}
    .nav a:hover{{color:#fff}}
    .theme-btn{{appearance:none;border:1px solid rgba(255,255,255,.25);background:transparent;color:#fff;
                padding:8px 10px;border-radius:10px;cursor:pointer;font-weight:700}}

    /* Hero */
    .hero{{background:
      radial-gradient(1200px 400px at 20% -10%, rgba(59,130,246,.35), transparent 60%),
      radial-gradient(900px 300px at 90% -20%, rgba(167,139,250,.28), transparent 60%),
      linear-gradient(180deg, rgba(15,23,42,.9), rgba(15,23,42,.66)); color:#fff; border-bottom:1px solid rgba(255,255,255,.06)}}
    .hero .wrap{{max-width:var(--max); margin:0 auto; padding:28px var(--pad) 34px; text-align:center}}
    .hero h1{{font-size:clamp(28px,6vw,44px); margin:0 0 8px}}
    .hero p{{color:#cbd5e1; margin:0}}

    /* Search + grid */
    .wrap{{max-width:var(--max); margin:0 auto; padding:32px 20px}}
    .search{{max-width:460px; margin:22px auto 28px; display:flex}}
    .search input{{flex:1;padding:12px 14px;border:1px solid var(--b);border-radius:12px;font-size:16px;background:var(--card);color:var(--ink)}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:24px}}
    .card{{border:1px solid var(--b);border-radius:16px;padding:22px 18px;text-decoration:none;color:var(--ink);
           background:var(--card);transition:all .15s; box-shadow:var(--shadow)}}
    .card:hover{{transform:translateY(-2px); box-shadow:0 10px 28px rgba(0,0,0,.10)}}
    .card h3{{margin:0 0 6px;font-size:20px}}
    .card p{{margin:0;color:var(--muted)}}
    footer{{margin-top:24px;text-align:center;color:#94a3b8;font-size:13px}}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="wrap">
      <a class="brand" href="{BASE_URL}/"><div class="logo"></div><span>{SITE_NAME}</span></a>
      <div class="nav">
        <a href="{BASE_URL}/cartridges/">Cartridges</a>
        <button id="themeToggle" class="theme-btn" type="button">Toggle theme</button>
      </div>
    </div>
  </div>

  <div class="hero">
    <div class="wrap">
      <h1>{SITE_NAME}</h1>
      <p>Your quick-lookup index for replacement parts & specs.</p>
    </div>
  </div>

  <div class="wrap">
    <div class="search"><input id="catSearch" type="search" placeholder="Search categories…" aria-label="Search categories"></div>
    <section id="catGrid" class="grid">{cards_html}</section>
    <footer>Last updated {today_iso()} · <a href="{BASE_URL}/sitemap.xml" style="color:inherit">Sitemap</a></footer>
  </div>

  <script>
    // Live filter
    const q = document.getElementById('catSearch');
    const cards = Array.from(document.querySelectorAll('#catGrid .card'));
    q?.addEventListener('input', e => {{
      const v = e.target.value.trim().toLowerCase();
      cards.forEach(c => c.style.display = c.dataset.name.includes(v) ? '' : 'none');
    }});

    // Theme toggle (persists)
    const root = document.documentElement;
    const key = 'theme-pref';
    function applyTheme(t) {{
      root.setAttribute('data-theme', t);
    }}
    const saved = localStorage.getItem(key);
    if (saved) applyTheme(saved);
    document.getElementById('themeToggle').addEventListener('click', () => {{
      const cur = root.getAttribute('data-theme') || 'auto';
      const next = cur === 'dark' ? 'light' : (cur === 'light' ? 'auto' : 'dark');
      localStorage.setItem(key, next); applyTheme(next);
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
        reader = csv.DictReader(f, skipinitialspace=True)
        for i, row in enumerate(reader):
            rows.append(row)
            if row_limit and i + 1 >= row_limit:
                break
    return rows

def load_offers(csv_path):
    """Load optional offers.csv -> dict[SKU] = [offers]."""
    if not os.path.exists(csv_path):
        return {}
    offers_by_sku = {}
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;")
        except csv.Error:
            dialect = csv.excel
            dialect.delimiter = ","
        reader = csv.DictReader(f, dialect=dialect)
        for row in reader:
            sku = (row.get("sku") or "").strip().upper()
            if not sku:
                continue
            offer = {
                "merchant": (row.get("merchant") or "Online").strip(),
                "url": (row.get("url") or "").strip(),
                "price": safe_float(row.get("price")),
                "currency": (row.get("currency") or "USD").strip(),
                "in_stock": str(row.get("in_stock") or "1").strip() not in ("0", "false", "False", ""),
            }
            if not offer["url"]:
                continue
            offers_by_sku.setdefault(sku, []).append(offer)
    return offers_by_sku

def amazon_search_link(query, tag):
    q = urllib.parse.quote_plus(query)
    return f"https://www.amazon.com/s?k={q}&tag={tag}"

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
    return crumbs

def page_output_path(section, slug):
    # /docs/cartridges/<slug>/index.html
    return os.path.join(OUTPUT_DIR, section, slug, "index.html")

def page_url(section, slug):
    return f"{BASE_URL}/{section}/{slug}/"

# -------- Affiliate offer building (Amazon tag + offers.csv + per-row URL) --------
OFFERS_BY_SKU = {}

def build_page_context(row):
    product_name = (row.get("product_name") or "").strip()
    model_number = (row.get("model_number") or "").strip()
    price = safe_float(row.get("price"))
    page_yield = safe_int(row.get("page_yield"))
    affiliate_url = (row.get("affiliate_url") or "").strip()

    cpp_raw, cpp_display = compute_cpp(price, page_yield)
    compatible_models = parse_compatible_models(row.get("compatible_models"))

    # Basic brand inference (optional; improve later)
    brand = product_name.split()[0] if product_name else None

    # Build affiliate offers: offers.csv > per-row url (normalize tag) > Amazon search fallback
    affiliate_offers = []
    sku_key = model_number.strip().upper()

    # 1) offers.csv rows
    if sku_key and OFFERS_BY_SKU.get(sku_key):
        affiliate_offers = OFFERS_BY_SKU[sku_key]

    # 2) per-row affiliate_url
    elif affiliate_url:
        url = affiliate_url.strip()
        if "amazon." in url and "tag=" not in url and AFFILIATE_AMAZON_TAG:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}tag={AFFILIATE_AMAZON_TAG}"
        affiliate_offers = [{
            "merchant": "Amazon" if "amazon." in url else "Online",
            "url": url,
            "price": price,  # keep None for Amazon to avoid compliance issues
            "currency": PRICE_CURRENCY,
            "in_stock": True,
        }]

    # 3) fallback to Amazon search by SKU
    elif AFFILIATE_AMAZON_TAG and model_number:
        affiliate_offers = [{
            "merchant": "Amazon",
            "url": amazon_search_link(model_number, AFFILIATE_AMAZON_TAG),
            "price": None,
            "currency": PRICE_CURRENCY,
            "in_stock": True,
        }]

    # FAQs (basic defaults)
    faqs = []
    if page_yield:
        faqs.append({"q": f"How long does {product_name} last?",
                     "a": f"About {page_yield} standard pages under ISO/IEC test conditions. Real-world results vary by coverage and settings."})
    if compatible_models:
        faqs.append({"q": f"Which printers are compatible with {product_name}?",
                     "a": "Compatible printers include: " + ", ".join(compatible_models) + "."})

    # Key points
    key_points = []
    if page_yield: key_points.append(f"Approx. yield: {page_yield} pages")
    if cpp_display: key_points.append(f"Cost per page: {cpp_display}")
    if compatible_models: key_points.append(f"{len(compatible_models)} compatible printers")

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
        "base_url": BASE_URL,
        "section": SECTION
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
        if ctx.get("affiliate_offers"):
            for off in ctx["affiliate_offers"]:
                print(f"[aff] {ctx['model_number']} -> {off['merchant']}: {off['url']}")

        html = tpl.render(**ctx)
        out_path = page_output_path(SECTION, slug)
        write_text(out_path, html)
        urls.append(ctx["canonical_url"])

        # remember this page for section index
        PAGES_BY_SECTION.setdefault(SECTION, []).append((slug, ctx["product_name"]))

    return urls

def build_homepage(urls):
    # Simple homepage that links to first N pages (kept for reference; not used)
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

    # Load data
    rows = load_rows(DATA_CSV, row_limit=ROW_LIMIT)

    # Load optional offers mapping once
    global OFFERS_BY_SKU
    OFFERS_BY_SKU = load_offers(AFFILIATE_OFFERS_CSV)

    print(f"[debug] loaded {len(rows)} data rows from {DATA_CSV}")
    print(f"[debug] loaded {sum(len(v) for v in OFFERS_BY_SKU.values())} offers from {AFFILIATE_OFFERS_CSV}" if OFFERS_BY_SKU else "[debug] no offers.csv found")

    # Render pages
    urls = render_pages(rows)

    # Build indexes + static files
    build_section_index(SECTION)
    build_homepage_full()
    build_sitemap(urls)
    build_robots()
    print(f"Generated {len(urls)} pages into ./{OUTPUT_DIR}")

if __name__ == "__main__":
    main()
