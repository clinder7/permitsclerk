// Permits Clerk payment API — creates embedded Checkout Sessions.
// Env vars (set in the Render dashboard, never committed):
//   STRIPE_SECRET_KEY  sk_live_... from the same account as the publishable key
//   STRIPE_PRICE_ID    optional override; otherwise the product's default price is used
//   ALLOWED_ORIGINS    comma-separated, e.g. https://permitsclerk.com,https://www.permitsclerk.com
const express = require('express');
const Stripe = require('stripe');

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
const PRODUCT_ID = 'prod_UtTz3Qehuonkiu'; // Seller's Permit Application Filing ($204)
let PRICE_ID = process.env.STRIPE_PRICE_ID || null;
async function getPriceId() {
  if (PRICE_ID) return PRICE_ID;
  const product = await stripe.products.retrieve(PRODUCT_ID);
  if (!product.default_price) throw new Error('product has no default price');
  PRICE_ID = typeof product.default_price === 'string' ? product.default_price : product.default_price.id;
  console.log('resolved default price:', PRICE_ID);
  return PRICE_ID;
}
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
      ui_mode: 'embedded',
      mode: 'payment',
      payment_method_types: ['card'],
      submit_type: 'pay',
      custom_text: { submit: { message: 'Your filing begins the moment your payment completes.' } },
      customer_email: email || undefined,
      client_reference_id: app_id || undefined,
      metadata,
      return_url: 'https://www.permitsclerk.com/get-your-sales-permit?paid=1&session_id={CHECKOUT_SESSION_ID}',
    });
    let session;
    try {
      session = await stripe.checkout.sessions.create({ ...params(), line_items: [{ price: await getPriceId(), quantity: 1 }] });
    } catch (err) {
      // price changed in Stripe (old default archived) — drop cache, re-resolve, retry once
      if (/archived|inactive|no such price/i.test(err.message || '')) {
        PRICE_ID = null;
        session = await stripe.checkout.sessions.create({ ...params(), line_items: [{ price: await getPriceId(), quantity: 1 }] });
      } else throw err;
    }
    res.json({ clientSecret: session.client_secret });
  } catch (err) {
    console.error('checkout session error:', err.message);
    res.status(500).json({ error: 'could not start checkout' });
  }
});

const port = process.env.PORT || 8080;
app.listen(port, () => console.log('payments api on :' + port));
