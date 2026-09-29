/* Service worker: guarda o jogo no aparelho para funcionar offline.
   - Página e JSON: busca na rede primeiro (mudanças aparecem na hora); sem rede, usa o cache.
   - Imagens, ícones e fontes: respondem do cache e se atualizam em segundo plano.
   Troque VERSAO ao mudar a lista de arquivos básicos. */
const VERSAO = 'encefalo-v2';
const ESPERA_REDE = 3500;   // ms; rede mais lenta que isso cai para o cache
const BASICOS = [
  './',
  './index.html',
  './manifest.json',
  './dados/estruturas.json',
  './icones/icone-192.png',
  './icones/icone-512.png',
  './icones/apple-touch-icon.png',
];
const FONTES = ['https://fonts.googleapis.com', 'https://fonts.gstatic.com'];

self.addEventListener('install', ev => {
  ev.waitUntil((async () => {
    const cache = await caches.open(VERSAO);
    await cache.addAll(BASICOS);
    // As imagens vêm da lista do JSON, então novas estruturas entram sem mexer aqui.
    try {
      const dados = await (await cache.match('./dados/estruturas.json')).json();
      await cache.addAll(dados.estruturas.map(e => './' + e.imagem));
    } catch {}
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', ev => {
  ev.waitUntil((async () => {
    for (const chave of await caches.keys()) {
      if (chave.startsWith('encefalo-') && chave !== VERSAO) await caches.delete(chave);
    }
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', ev => {
  const req = ev.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin && !FONTES.includes(url.origin)) return;

  const redePrimeiro = req.mode === 'navigate' || /\.(html|json)$/.test(url.pathname);
  if (redePrimeiro) {
    ev.respondWith((async () => {
      const cache = await caches.open(VERSAO);
      try {
        const r = await Promise.race([
          fetch(req),
          new Promise((_, falha) => setTimeout(() => falha(new Error('rede lenta')), ESPERA_REDE)),
        ]);
        if (r.ok) cache.put(req, r.clone());
        return r;
      } catch {
        const salvo = await cache.match(req, { ignoreSearch: true })
          || (req.mode === 'navigate' && await cache.match('./index.html'));
        return salvo || Response.error();
      }
    })());
    return;
  }

  ev.respondWith((async () => {
    const cache = await caches.open(VERSAO);
    const salvo = await cache.match(req, { ignoreSearch: true });
    const daRede = fetch(req)
      .then(r => { if (r.ok || r.type === 'opaque') cache.put(req, r.clone()); return r; })
      .catch(() => null);
    if (salvo) { ev.waitUntil(daRede); return salvo; }
    const r = await daRede;
    if (r) return r;
    if (req.mode === 'navigate') return (await cache.match('./index.html')) || Response.error();
    return Response.error();
  })());
});
