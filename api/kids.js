// /kids – parents' inquiry form. Each lead = private blob kids/leads/<id>.json
// POST (public): new lead. GET / status updates: אודי only (cookie pb=1717, same as other admin pages).
import { put, get, list } from '@vercel/blob';

const PASS = '1717';
const PRE = 'kids/leads/';
const isUdi = (req) => /(?:^|;\s*)pb=1717(?:;|$)/.test(req.headers.cookie || '');
const clip = (v, n) => String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, n);
const arr = (v, n) => (Array.isArray(v) ? v : []).map((x) => clip(x, 40)).filter(Boolean).slice(0, n);

async function readOne(pathname) {
  const r = await get(pathname, { access: 'private', useCache: false });
  if (!r || r.statusCode !== 200) return null;
  return JSON.parse(await new Response(r.stream).text());
}
const save = (x) => put(PRE + x.id + '.json', JSON.stringify(x), { access: 'private', addRandomSuffix: false, allowOverwrite: true, contentType: 'application/json' });

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  try {
    if (req.method === 'GET') {
      if (!isUdi(req)) return res.status(401).json({ error: 'unauthorized' });
      const out = []; let cursor;
      do {
        const l = await list({ prefix: PRE, cursor, limit: 1000 });
        for (const b of l.blobs) { try { const x = await readOne(b.pathname); if (x) out.push(x); } catch {} }
        cursor = l.hasMore ? l.cursor : undefined;
      } while (cursor);
      out.sort((a, b) => b.created - a.created);
      return res.status(200).json({ items: out });
    }
    if (req.method !== 'POST') return res.status(405).json({ error: 'method' });
    const b = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});

    if (b.action === 'login') {
      if (String(b.code || '').trim() !== PASS) return res.status(403).json({ error: 'קוד שגוי' });
      res.setHeader('Set-Cookie', 'pb=' + PASS + '; Path=/; Max-Age=31536000; HttpOnly; Secure; SameSite=Lax');
      return res.status(200).json({ ok: true });
    }
    if (b.action === 'status') {
      if (!isUdi(req)) return res.status(401).json({ error: 'unauthorized' });
      const id = String(b.id || '').replace(/[^a-z0-9]/gi, '');
      const x = await readOne(PRE + id + '.json'); if (!x) return res.status(404).json({ error: 'not found' });
      x.status = ['new', 'handled'].includes(b.status) ? b.status : x.status;
      x.note = b.note != null ? clip(b.note, 1000) : x.note;
      await save(x); return res.status(200).json({ ok: true, item: x });
    }

    // new lead (public)
    if (b.website) return res.status(200).json({ ok: true }); // honeypot
    const parent = clip(b.parent, 80), phone = clip(b.phone, 30);
    if (phone.replace(/\D/g, '').length < 9) return res.status(400).json({ error: 'חסר טלפון תקין' });
    const x = {
      id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
      created: Date.now(), status: 'new',
      parent, phone, email: clip(b.email, 100), city: clip(b.city, 60),
      kids: clip(b.kids, 10), child: clip(b.child, 120), ages: arr(b.ages, 8),
      interest: arr(b.interest, 8), days: arr(b.days, 6), hours: arr(b.hours, 6), exp: clip(b.exp, 30),
      source: clip(b.source, 60), notes: clip(b.notes, 1500), note: '',
    };
    await save(x);
    return res.status(200).json({ ok: true, id: x.id });
  } catch (e) {
    return res.status(500).json({ error: 'server', detail: String(e && e.message || e).slice(0, 200) });
  }
}
