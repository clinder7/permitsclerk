#!/usr/bin/env python3
"""Generate the 50 state SEO pages + /states/ index + sitemap.xml.
Data compiled July 2026 — VERIFY fees with each state agency before relying on them.
Run from repo root: python3 scripts/generate-state-pages.py
"""
import os, html

# name, permit (local term), agency, short, fee, quirk sentence, portal
# no_tax=True → alternate page explaining no statewide sales tax
STATES = [
 ("Alabama","Sales Tax License","Alabama Department of Revenue","ALDOR","$0","Registration is free through the My Alabama Taxes (MAT) portal.","My Alabama Taxes"),
 ("Alaska","Business License","Alaska Department of Commerce","DCCED","—","Alaska has no statewide sales tax, but many boroughs and cities levy local sales taxes with their own registration, and the state requires a general business license.","myAlaska", True),
 ("Arizona","Transaction Privilege Tax (TPT) License","Arizona Department of Revenue","ADOR","$12","Arizona charges $12 per business location, and many cities add their own license fees on top.","AZTaxes"),
 ("Arkansas","Sales Tax Permit","Arkansas Department of Finance and Administration","DFA","$50","Arkansas charges a $50 permit fee — one of the few states with a meaningful charge.","Arkansas Taxpayer Access Point"),
 ("California","Seller's Permit","California Department of Tax and Fee Administration","CDTFA","$0","California charges no fee, though the CDTFA may request a security deposit in limited cases. Temporary 90-day permits are available for pop-ups and events.","CDTFA Online Services"),
 ("Colorado","Sales Tax License","Colorado Department of Revenue","CDOR","$16","Colorado's license fee is $16 for a two-year period, plus a refundable $50 deposit for some businesses. Home-rule cities may require separate local licenses.","MyBizColorado"),
 ("Connecticut","Sales and Use Tax Permit","Connecticut Department of Revenue Services","DRS","$100","Connecticut charges $100 — the highest seller's permit fee in the country.","myconneCT"),
 ("Delaware","Business License","Delaware Division of Revenue","DOR","—","Delaware has no sales tax and no seller's permit, but businesses pay a gross receipts tax and need a state business license.","Delaware One Stop", True),
 ("Florida","Sales Tax Registration","Florida Department of Revenue","FDOR","$0","Registering online is free (a $5 fee applies only to paper applications). Florida issues an Annual Resale Certificate with your registration.","Florida Business Tax Application"),
 ("Georgia","Sales and Use Tax Registration","Georgia Department of Revenue","GADOR","$0","Registration is free through the Georgia Tax Center.","Georgia Tax Center"),
 ("Hawaii","General Excise Tax (GET) License","Hawaii Department of Taxation","DOTAX","$20","Hawaii uses a General Excise Tax instead of a sales tax — the GET license is a one-time $20 fee.","Hawaii Tax Online"),
 ("Idaho","Seller's Permit","Idaho State Tax Commission","ISTC","$0","Registration is free through the Idaho Business Registration System.","Idaho Business Registration"),
 ("Illinois","Certificate of Registration","Illinois Department of Revenue","IDOR","$0","Illinois retailers register for the Retailers' Occupation Tax at no charge.","MyTax Illinois"),
 ("Indiana","Registered Retail Merchant Certificate","Indiana Department of Revenue","INDOR","$25","Indiana charges $25 for the RRMC, which renews free every two years.","INBiz"),
 ("Iowa","Sales Tax Permit","Iowa Department of Revenue","IDR","$0","Registration is free through GovConnectIowa.","GovConnectIowa"),
 ("Kansas","Sales Tax Registration","Kansas Department of Revenue","KDOR","$0","Registration is free through the Kansas Customer Service Center.","Kansas Customer Service Center"),
 ("Kentucky","Sales and Use Tax Permit","Kentucky Department of Revenue","KYDOR","$0","Registration is free through the Kentucky One Stop Business Portal.","Kentucky One Stop"),
 ("Louisiana","Sales Tax Certificate","Louisiana Department of Revenue","LDR","$0","State registration is free; parish (local) sales taxes have separate registrations.","geauxBIZ"),
 ("Maine","Retailer Certificate","Maine Revenue Services","MRS","$0","Registration is free through the Maine Tax Portal.","Maine Tax Portal"),
 ("Maryland","Sales and Use Tax License","Comptroller of Maryland","—","$0","Registration is free through Maryland Tax Connect.","Maryland Tax Connect"),
 ("Massachusetts","Sales and Use Tax Registration","Massachusetts Department of Revenue","MassDOR","$0","Registration is free through MassTaxConnect; you'll display Form ST-1.","MassTaxConnect"),
 ("Michigan","Sales Tax License","Michigan Department of Treasury","—","$0","Registration is free through Michigan Treasury Online and the license renews automatically each year.","Michigan Treasury Online"),
 ("Minnesota","Sales Tax ID","Minnesota Department of Revenue","MNDOR","$0","Registration is free through e-Services.","Minnesota e-Services"),
 ("Mississippi","Sales Tax Permit","Mississippi Department of Revenue","MSDOR","$0","Registration is free through the Taxpayer Access Point (TAP).","Mississippi TAP"),
 ("Missouri","Sales Tax License","Missouri Department of Revenue","MODOR","$0","The license itself is free, but Missouri requires a sales tax bond (roughly two to three times your estimated monthly tax) that is refunded after a good payment history.","MyTax Missouri"),
 ("Montana","—","Montana Department of Revenue","MTDOR","—","Montana has no general statewide sales tax, so no seller's permit is required (a few resort areas levy local taxes).","Montana TAP", True),
 ("Nebraska","Sales Tax Permit","Nebraska Department of Revenue","NEDOR","$0","Registration is free through NebFile / the Nebraska One-Stop portal.","Nebraska One-Stop"),
 ("Nevada","Sales Tax Permit","Nevada Department of Taxation","NVDOT","$15","Nevada charges $15 per business location and may require a security deposit based on expected sales.","SilverFlume"),
 ("New Hampshire","—","New Hampshire Department of Revenue Administration","NHDRA","—","New Hampshire has no statewide sales tax, so no seller's permit is required for in-state sales.","NH DRA", True),
 ("New Jersey","Certificate of Authority","New Jersey Division of Taxation","—","$0","Register free via NJ-REG at least 15 business days before opening; the state issues a Certificate of Authority you must display.","NJ Business Portal"),
 ("New Mexico","Gross Receipts Tax Registration","New Mexico Taxation and Revenue Department","TRD","$0","New Mexico uses a Gross Receipts Tax instead of a sales tax — registration is free through the Taxpayer Access Point.","New Mexico TAP"),
 ("New York","Certificate of Authority","New York State Department of Taxation and Finance","NYSDTF","$0","Free, but you must apply at least 20 days before you begin business — operating without a Certificate of Authority carries penalties.","New York Business Express"),
 ("North Carolina","Certificate of Registration","North Carolina Department of Revenue","NCDOR","$0","Registration is free online.","NCDOR Online Registration"),
 ("North Dakota","Sales Tax Permit","North Dakota Office of State Tax Commissioner","—","$0","Registration is free through ND TAP.","North Dakota TAP"),
 ("Ohio","Vendor's License","Ohio Department of Taxation","ODT","$25","Ohio charges $25 per location for a vendor's license, obtained through the state or your county auditor.","Ohio Business Gateway"),
 ("Oklahoma","Sales Tax Permit","Oklahoma Tax Commission","OTC","$20","Oklahoma charges $20 (plus $10 per additional location); permits renew every three years.","OkTAP"),
 ("Oregon","—","Oregon Department of Revenue","ORDOR","—","Oregon has no statewide sales tax, so no seller's permit is required for in-state sales.","Revenue Online", True),
 ("Pennsylvania","Sales Tax License","Pennsylvania Department of Revenue","PADOR","$0","Registration is free through myPATH.","myPATH"),
 ("Rhode Island","Sales Tax Permit","Rhode Island Division of Taxation","RIDOT","$10","Rhode Island charges a small annual permit fee.","RI Taxpayer Portal"),
 ("South Carolina","Retail License","South Carolina Department of Revenue","SCDOR","$50","South Carolina charges $50 per business location for a retail license.","MyDORWAY"),
 ("South Dakota","Sales Tax License","South Dakota Department of Revenue","SDDOR","$0","Registration is free online.","SD Tax Application"),
 ("Tennessee","Sales and Use Tax Registration","Tennessee Department of Revenue","TNDOR","$0","Registration is free through TNTAP.","TNTAP"),
 ("Texas","Sales and Use Tax Permit","Texas Comptroller of Public Accounts","—","$0","Registration is free; Texas may require a security bond in limited cases.","Texas Online Tax Registration"),
 ("Utah","Sales Tax License","Utah State Tax Commission","USTC","$0","Registration is free through Utah's OneStop Business Registration.","Utah OneStop"),
 ("Vermont","Sales and Use Tax License","Vermont Department of Taxes","VTDOT","$0","Registration is free through myVTax.","myVTax"),
 ("Virginia","Certificate of Registration","Virginia Department of Taxation","VATAX","$0","Registration is free online.","Virginia Tax Online"),
 ("Washington","Business License with Tax Registration","Washington Department of Revenue","WADOR","$50","Washington bundles tax registration into its Business License Application (about $50, plus any city endorsements).","My DOR"),
 ("West Virginia","Business Registration Certificate","West Virginia Tax Division","—","$30","West Virginia charges a one-time $30 business registration fee that covers sales tax collection.","MyTaxes WV"),
 ("Wisconsin","Seller's Permit","Wisconsin Department of Revenue","WIDOR","$20","Wisconsin's Business Tax Registration is $20, renewed at $10 every two years.","WI Business Tax Registration"),
 ("Wyoming","Sales/Use Tax License","Wyoming Department of Revenue","WYDOR","$60","Wyoming charges a one-time $60 licensing fee.","WYIFS"),
]

def norm(row):
    r = list(row) + [False] * (8 - len(row))
    return dict(zip(["name","permit","agency","short","fee","quirk","portal","no_tax"], r))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = html.escape

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{meta}">
<link rel="canonical" href="https://www.permitsclerk.com/{slug}/">
{jsonld}
<style>
:root{{--ink:#17221f;--muted:#62706b;--green:#176b52;--green-dark:#0f503e;--mint:#eaf7f1;--cream:#fbfaf6;--line:#dce6e1;--gold:#f4b740;--shadow:0 24px 70px rgba(23,34,31,.12)}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}
body{{margin:0;font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:var(--cream);line-height:1.55;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}.wrap{{width:min(1060px,calc(100% - 40px));margin:auto}}
.announcement{{background:var(--ink);color:#fff;text-align:center;padding:9px 16px;font-size:14px;font-weight:750}}
.header{{position:sticky;top:0;z-index:30;background:rgba(251,250,246,.94);backdrop-filter:blur(14px);border-bottom:1px solid rgba(23,34,31,.08)}}
.nav{{height:72px;display:flex;align-items:center;justify-content:space-between}}.brand-logo{{height:40px;width:auto;display:block}}
.btn{{display:inline-block;border:0;border-radius:13px;background:var(--green);color:#fff;padding:15px 24px;font-weight:850;cursor:pointer;box-shadow:0 8px 20px rgba(23,107,82,.2);transition:.2s;font-size:16px}}
.btn:hover{{transform:translateY(-1px);background:var(--green-dark)}}
.hero{{padding:56px 0 40px}}.hero h1{{font-size:clamp(34px,4.8vw,54px);line-height:1.05;letter-spacing:-.05em;margin:0 0 16px;max-width:860px}}
.hero .lead{{font-size:19px;color:var(--muted);max-width:720px;margin:0 0 26px}}
.trust-line{{margin-top:16px;font-size:14px;color:var(--muted);font-weight:700}}.stars{{color:var(--gold);letter-spacing:1px}}
.facts{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:38px 0 8px}}
.fact{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px;text-align:center}}
.fact strong{{display:block;font-size:22px;letter-spacing:-.03em}}.fact small{{color:var(--muted);font-weight:750;font-size:11px;text-transform:uppercase;letter-spacing:.05em}}
.section{{padding:44px 0}}.section h2{{font-size:clamp(26px,3.2vw,36px);letter-spacing:-.04em;margin:0 0 14px}}
.section p{{color:var(--muted);max-width:760px}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:22px}}
.card{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:24px}}
.card h3{{margin:0 0 10px;font-size:19px}}.card ul{{margin:0;padding-left:20px;color:var(--muted)}}.card li{{margin:7px 0}}
.steps{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:22px}}
.step{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px}}
.num{{width:38px;height:38px;border-radius:11px;background:var(--mint);color:var(--green);display:grid;place-items:center;font-weight:900}}
.step h3{{font-size:17px;margin:14px 0 6px}}.step p{{font-size:14px;margin:0}}
.callout{{background:var(--mint);border:1px solid #d8ecdf;border-radius:18px;padding:22px 24px;margin-top:22px}}
.callout strong{{color:var(--green)}}
.faq{{max-width:820px}}.faq details{{border-top:1px solid var(--line);padding:16px 0}}.faq details:last-child{{border-bottom:1px solid var(--line)}}
.faq summary{{font-weight:800;cursor:pointer;font-size:16px}}.faq p{{margin:10px 0 0}}
.cta-band{{background:var(--green);color:#fff;border-radius:24px;padding:38px 40px;display:flex;align-items:center;justify-content:space-between;gap:24px;margin:30px 0 10px}}
.cta-band h2{{margin:0 0 6px;font-size:28px;letter-spacing:-.03em}}.cta-band p{{margin:0;color:#d5eee5}}
.btn.light{{background:#fff;color:var(--green);white-space:nowrap}}
.states-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:20px}}
.states-grid a{{padding:10px 12px;background:#fff;border:1px solid var(--line);border-radius:10px;font-weight:700;font-size:14px}}
.states-grid a:hover{{background:var(--mint)}}
.footer{{background:#0b1916;color:#adc0ba;padding:40px 0 26px;margin-top:50px;font-size:14px}}
.footer .disclaimer{{font-size:12px;color:#7d938c;max-width:820px;line-height:1.6;border-top:1px solid rgba(255,255,255,.1);margin-top:20px;padding-top:18px}}
@media(max-width:800px){{.facts{{grid-template-columns:1fr 1fr}}.cols,.steps{{grid-template-columns:1fr}}.cta-band{{flex-direction:column;align-items:flex-start}}.cta-band .btn{{width:100%;text-align:center}}.states-grid{{grid-template-columns:1fr 1fr}}}}
</style>
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-18326874625"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}
if(location.hostname!=='localhost'&&location.hostname!=='127.0.0.1'&&location.protocol!=='file:'){{gtag('js',new Date());gtag('config','AW-18326874625');}}
</script>
</head>
<body>
<div class="announcement">Seller’s permit filings available nationwide · Most applications take under 5 minutes</div>
<header class="header"><div class="wrap nav"><a href="../"><img class="brand-logo" src="../assets/permits-clerk-logo.png" alt="Permits Clerk"></a><a class="btn" style="padding:11px 18px;font-size:14px" href="../get-your-sales-permit/?state={q}">Start my application</a></div></header>
<main class="wrap">
"""

FOOT = """</main>
<footer class="footer"><div class="wrap">
<img class="brand-logo" src="../assets/permits-clerk-logo-light.png" alt="Permits Clerk" style="height:34px">
<p style="max-width:520px">Fast, guided seller’s permit filings for small businesses — prepared, error-checked, and filed correctly.</p>
<p style="font-size:13px"><a href="../states/" style="text-decoration:underline">All states</a> · <a href="../" style="text-decoration:underline">Home</a></p>
<div class="disclaimer">Permits Clerk is a private filing assistance service and is not affiliated with any government agency, including the {agency}. You may file directly with the {short} without using this service. State fee information compiled July 2026 — verify current fees with the {short}.</div>
<div style="font-size:12px;color:#7d938c;margin-top:10px">© 2026 Permits Clerk. All rights reserved.</div>
</div></footer>
<script>
if(location.protocol==='file:'){{document.querySelectorAll('a').forEach(a=>{{const h=a.getAttribute('href');if(h==='../')a.setAttribute('href','../index.html');else if(h&&h.startsWith('../get-your-sales-permit/'))a.setAttribute('href','../get-your-sales-permit/index.html'+(h.includes('?')?h.slice(h.indexOf('?')):''));else if(h==='../states/')a.setAttribute('href','../states/index.html')}})}}
</script>
</body>
</html>
"""

def faq_jsonld(qas):
    items = ",".join(
        '{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
        % (q.replace('"','\\"'), a.replace('"','\\"')) for q, a in qas)
    return items

def page_taxed(s):
    slug = s["name"].lower().replace(" ", "-") + "-sellers-permit"
    q = s["name"].replace(" ", "%20")
    permit_label = "Seller’s Permit"
    official = s["permit"] if "Seller" not in s["permit"] else "seller’s permit"
    fee_line = ("free — the state charges nothing" if s["fee"] == "$0"
                else f'{s["fee"]} (paid to the state, separate from our fee)')
    qas = [
        (f'How much does a {s["name"]} {s["permit"].lower()} cost?',
         f'The state charge is {"nothing — registration with the " + s["short"] + " is free" if s["fee"]=="$0" else s["fee"]}. Permits Clerk charges a $75 flat service fee to prepare your application, check it for errors, and file it correctly. {s["quirk"]}'),
        (f'Who needs a seller’s permit in {s["name"]}?',
         f'Anyone selling taxable goods in {s["name"]} — including online stores, Amazon and Etsy sellers, retail shops, wholesalers, and pop-up or event vendors — generally must register with the {s["agency"]} before making sales.'),
        (f'How long does it take?',
         'Our guided application takes most customers under 5 minutes. State processing typically runs from same-day to a few business days.'),
        (f'Do I need a permit to sell online from home in {s["name"]}?',
         f'Yes — if you sell taxable goods to customers, {s["name"]} requires registration even for home-based, online-only businesses.'),
        ('Is Permits Clerk a government agency?',
         f'No. Permits Clerk is a private filing assistance service and is not affiliated with any government agency. You may file directly with the {s["short"]} without using our service.'),
    ]
    jsonld = ('<script type="application/ld+json">{"@context":"https://schema.org","@graph":['
      '{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://www.permitsclerk.com/"},{"@type":"ListItem","position":2,"name":"%s Seller\'s Permit","item":"https://www.permitsclerk.com/%s/"}]},'
      '{"@type":"Service","name":"%s Seller\'s Permit Filing Service","provider":{"@type":"Organization","name":"Permits Clerk","url":"https://www.permitsclerk.com/"},"areaServed":{"@type":"State","name":"%s"},"offers":{"@type":"Offer","price":"75.00","priceCurrency":"USD"}},'
      '{"@type":"FAQPage","mainEntity":[%s]}]}</script>'
      % (s["name"], slug, s["name"], s["name"], faq_jsonld(qas)))

    body = HEAD.format(
        title=f'{s["name"]} Seller’s Permit — File Online in Minutes ({("$0 State Fee" if s["fee"]=="$0" else s["fee"] + " State Fee")}) | Permits Clerk',
        meta=f'Get your {s["name"]} {s["permit"].lower()} fast. {("The state charges no fee" if s["fee"]=="$0" else "State fee: " + s["fee"])} — we prepare and file your {s["short"]} application for $75 flat with expert error checking.',
        slug=slug, jsonld=jsonld, q=q)
    body += f"""
<section class="hero">
<h1>Get Your {e(s["name"])} {e(permit_label)} — Filed Fast, Done Right</h1>
<p class="lead">Businesses selling taxable goods in {e(s["name"])} must register for a {e(official)} with the {e(s["agency"])}. Answer a few simple questions — we prepare your application, check it for errors, and file it correctly. <strong>$75 flat, no hidden service fees.</strong></p>
<a class="btn" href="../get-your-sales-permit/?state={q}">Start my {e(s["name"])} application →</a>
<div class="trust-line"><span class="stars">★★★★★</span> 4.8/5 from 1,376 reviews · Trusted by 10,000+ founders</div>
<div class="facts">
<div class="fact"><strong>{e(s["fee"])}</strong><small>{e(s["name"])} state fee</small></div>
<div class="fact"><strong>$75</strong><small>Our flat service fee</small></div>
<div class="fact"><strong>~5 min</strong><small>Application time</small></div>
<div class="fact"><strong>{e(s["short"] if s["short"] != "—" else s["agency"].split()[0])}</strong><small>Issuing agency</small></div>
</div>
</section>
<section class="section">
<h2>Who needs a seller’s permit in {e(s["name"])}?</h2>
<p>{e(s["name"])} requires registration for any individual or business selling taxable goods — even part-time or online-only sellers operating from home. The registration is issued by the {e(s["agency"])} (via {e(s["portal"])}).</p>
<div class="cols">
<div class="card"><h3>You need one if you…</h3><ul>
<li>Sell online to {e(s["name"])} customers (Shopify, Amazon, Etsy, your own store)</li>
<li>Run a retail shop, boutique, or showroom</li>
<li>Sell wholesale to other businesses</li>
<li>Sell at pop-ups, fairs, or markets</li>
<li>Lease taxable equipment or goods</li>
</ul></div>
<div class="card"><h3>What you’ll need to apply</h3><ul>
<li>Legal business name and entity type</li>
<li>EIN (or SSN for sole proprietors)</li>
<li>Business address and contact details</li>
<li>What you plan to sell</li>
<li>About 5 minutes</li>
</ul></div>
</div>
<div class="callout"><strong>Good to know:</strong> The {e(s["name"])} state charge is {e(fee_line)}. {e(s["quirk"])} Our $75 covers guided preparation, an expert error check (mistakes are the #1 cause of delays), filing support, and digital delivery of your documents.</div>
</section>
<section class="section">
<h2>How it works</h2>
<div class="steps">
<div class="step"><div class="num">1</div><h3>Answer simple questions</h3><p>Our guided application takes about 5 minutes — no confusing government forms.</p></div>
<div class="step"><div class="num">2</div><h3>We review &amp; file</h3><p>A specialist checks your application for errors, then files it with the {e(s["short"] if s["short"] != "—" else s["agency"])}. We rush all orders.</p></div>
<div class="step"><div class="num">3</div><h3>Receive your permit</h3><p>Your {e(s["name"])} permit documents arrive by email — often within days.</p></div>
</div>
</section>
<section class="section">
<h2>{e(s["name"])} seller’s permit FAQ</h2>
<div class="faq">
""" + "".join(f'<details{" open" if i==0 else ""}><summary>{e(qa[0])}</summary><p>{e(qa[1])}</p></details>\n' for i, qa in enumerate(qas)) + f"""</div>
</section>
<div class="cta-band">
<div><h2>Start your {e(s["name"])} application now.</h2><p>5 minutes of questions · $75 flat · expert error check included</p></div>
<a class="btn light" href="../get-your-sales-permit/?state={q}">Start my application →</a>
</div>
"""
    body += FOOT.format(agency=e(s["agency"]), short=e(s["short"] if s["short"] != "—" else s["agency"]))
    return slug, body

def page_no_tax(s):
    slug = s["name"].lower().replace(" ", "-") + "-sellers-permit"
    q = s["name"].replace(" ", "%20")
    qas = [
        (f'Do I need a seller’s permit in {s["name"]}?',
         f'Generally no — {s["name"]} has no statewide sales tax, so there is no statewide seller’s permit. {s["quirk"]}'),
        (f'What if I sell to customers in other states?',
         'If you sell online into states that do have sales tax, you may need seller’s permits there once you cross their economic nexus thresholds. We can file those applications for you.'),
        ('Is Permits Clerk a government agency?',
         'No. Permits Clerk is a private filing assistance service and is not affiliated with any government agency.'),
    ]
    jsonld = ('<script type="application/ld+json">{"@context":"https://schema.org","@graph":['
      '{"@type":"FAQPage","mainEntity":[%s]}]}</script>' % faq_jsonld(qas))
    body = HEAD.format(
        title=f'{s["name"]} Seller’s Permit — Do You Need One? (No State Sales Tax) | Permits Clerk',
        meta=f'{s["name"]} has no statewide sales tax, so most businesses don’t need a seller’s permit. Here’s what applies instead — and what you need if you sell into other states.',
        slug=slug, jsonld=jsonld, q=q)
    body += f"""
<section class="hero">
<h1>Does {e(s["name"])} Require a Seller’s Permit? Short Answer: No.</h1>
<p class="lead">{e(s["name"])} has <strong>no statewide sales tax</strong>, so there is no statewide seller’s permit to get. {e(s["quirk"])}</p>
<div class="callout" style="max-width:760px"><strong>Selling into other states?</strong> If your online store ships to customers in states that do charge sales tax, you may need seller’s permits there once you pass their thresholds. We file those applications — $75 flat per state.</div>
<p style="margin-top:24px"><a class="btn" href="../get-your-sales-permit/">Start an application for another state →</a></p>
<div class="trust-line"><span class="stars">★★★★★</span> 4.8/5 from 1,376 reviews · Trusted by 10,000+ founders</div>
</section>
<section class="section">
<h2>{e(s["name"])} FAQ</h2>
<div class="faq">
""" + "".join(f'<details{" open" if i==0 else ""}><summary>{e(qa[0])}</summary><p>{e(qa[1])}</p></details>\n' for i, qa in enumerate(qas)) + """</div>
</section>
"""
    body += FOOT.format(agency=e(s["agency"]), short=e(s["agency"]))
    return slug, body

# ---------- generate ----------
slugs = []
for row in STATES:
    s = norm(row)
    slug, out = (page_no_tax(s) if s["no_tax"] else page_taxed(s))
    d = os.path.join(ROOT, slug)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(out)
    slugs.append((s["name"], slug))
print(f"wrote {len(slugs)} state pages")

# ---------- states index ----------
links = "".join(f'<a href="../{slug}/">{e(name)}</a>' for name, slug in slugs)
idx = HEAD.format(title="Seller’s Permits by State — Requirements & Fees | Permits Clerk",
    meta="Seller’s permit requirements, state fees, and filing for all 50 states. $75 flat filing service.",
    slug="states", jsonld="", q="")
idx += f"""
<section class="hero"><h1>Seller’s Permits by State</h1>
<p class="lead">Requirements, state fees, and issuing agencies for all 50 states — plus guided filing for $75 flat.</p>
<div class="states-grid">{links}</div></section>
"""
idx += FOOT.format(agency="any state agency", short="relevant agency")
# fix relative shim for /states/ page links (they are ../slug/ which works)
os.makedirs(os.path.join(ROOT, "states"), exist_ok=True)
open(os.path.join(ROOT, "states", "index.html"), "w").write(idx)
print("wrote states index")

# ---------- sitemap + robots ----------
urls = ["", "get-your-sales-permit/", "states/"] + [slug + "/" for _, slug in slugs]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    sm += f'<url><loc>https://www.permitsclerk.com/{u}</loc></url>\n'
sm += "</urlset>\n"
open(os.path.join(ROOT, "sitemap.xml"), "w").write(sm)
open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: https://www.permitsclerk.com/sitemap.xml\n")
print("wrote sitemap.xml + robots.txt with", len(urls), "urls")
