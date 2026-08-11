// Permits Clerk payment API — creates embedded Checkout Sessions.
// Env vars (set in the Render dashboard, never committed):
//   STRIPE_SECRET_KEY  sk_live_... from the same account as the publishable key
//   ALLOWED_ORIGINS    comma-separated, e.g. https://permitsclerk.com,https://www.permitsclerk.com
const express = require('express');
const Stripe = require('stripe');
const { randomBytes } = require('crypto');

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, { apiVersion: '2026-07-29.dahlia' });
const PRODUCT_ID = 'prod_UtTz3Qehuonkiu'; // Seller's Permit Full-Service Filing
const SERVICE_PRICE_CENTS = 12900;
const INTEGRATION_IDENTIFIER = 'permits_' + Array.from(
  randomBytes(8), byte => String.fromCharCode(97 + (byte % 26)),
).join('');
const ORIGINS = (process.env.ALLOWED_ORIGINS || 'https://permitsclerk.com,https://www.permitsclerk.com')
  .split(',').map(s => s.trim());

const app = express();
app.use(express.json({ limit: '32kb' }));

app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  }
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

app.get('/healthz', (req, res) => res.json({ ok: true }));

app.post('/create-checkout-session', async (req, res) => {
  try {
    const { email, app_id, application } = req.body || {};
    // application details ride along as metadata so every payment carries its application
    const metadata = { app_id: String(app_id || '').slice(0, 100) };
    if (application && typeof application === 'object') {
      for (const [k, v] of Object.entries(application)) {
        if (metadata[k] === undefined) metadata[k] = String(v ?? '').slice(0, 450);
      }
    }
    const params = () => ({
      // 'embedded' was renamed to 'embedded_page' in the dahlia API versions — the old value is rejected
      ui_mode: 'embedded_page',
      mode: 'payment',
      integration_identifier: INTEGRATION_IDENTIFIER,
      // copy application metadata onto the PaymentIntent so it shows on the payment in the Dashboard
      // statement_descriptor_suffix renders as "FILINGS HQ* PERMITS" on card statements;
      // account prefix "FILINGS HQ" is 10 chars, so the suffix is capped at 10 (22-char combined limit —
      // Stripe rejects session creation outright if exceeded)
      payment_intent_data: {
        metadata,
        description: 'Seller\'s Permit Filing — ' + (metadata.state || 'state n/a') + ' — ' + (metadata.app_id || ''),
        statement_descriptor_suffix: 'PERMITS',
      },
      // card only: Apple Pay / Google Pay still surface (they're card wallets), while
      // Cash App / Klarna / Amazon Pay stay hidden and the card form renders directly
      payment_method_types: ['card'],
      submit_type: 'pay',
      custom_text: { submit: { message: 'Your filing begins the moment your payment completes.' } },
      customer_email: email || undefined,
      client_reference_id: app_id || undefined,
      metadata,
      return_url: 'https://www.permitsclerk.com/get-your-sales-permit?paid=1&session_id={CHECKOUT_SESSION_ID}',
    });
    const session = await stripe.checkout.sessions.create({
      ...params(),
      line_items: [{
        price_data: {
          currency: 'usd',
          product: PRODUCT_ID,
          unit_amount: SERVICE_PRICE_CENTS,
        },
        quantity: 1,
      }],
    });
    res.json({ clientSecret: session.client_secret });
  } catch (err) {
    console.error('checkout session error:', err.message);
    res.status(500).json({ error: 'could not start checkout' });
  }
});

const port = process.env.PORT || 8080;
app.listen(port, () => console.log('payments api on :' + port));
