/* B9 Site-Health collector — runs IN the page (bot-challenge blocks plain HTTP, so this
   must run inside the real/authenticated browser, same as the AAIR/GSC scans).
   Returns {page, checked, broken:[{url,status,type}], good_imgs:[...]}.
   Inject per seed page (Hermes CDP or claude-in-chrome), aggregate the results, hand to classify.py. */
(() => {
  const B = location.origin;
  function head(u){ try{ var x=new XMLHttpRequest(); x.open('HEAD', u, false); x.send(); return x.status; }catch(e){ return null; } }
  function kind(u){ if(/\.(png|jpe?g|gif|webp|svg|avif)(\?|$)/i.test(u)) return 'image';
                    if(/\.css(\?|$)/i.test(u)) return 'css'; if(/\.js(\?|$)/i.test(u)) return 'js'; return 'other'; }
  const urls = new Set();
  document.querySelectorAll('img[src]').forEach(i=>{ const s=i.getAttribute('src'); if(s && !s.startsWith('data:')) urls.add(new URL(s, location.href).href); });
  document.querySelectorAll('link[rel="stylesheet"][href]').forEach(l=>urls.add(new URL(l.getAttribute('href'), location.href).href));
  document.querySelectorAll('script[src]').forEach(s=>urls.add(new URL(s.getAttribute('src'), location.href).href));
  const list = [...urls].filter(u => u.startsWith(B)).slice(0, 300);
  const recs = list.map(u => ({url: u.replace(B,''), status: head(u), type: kind(u)}));
  const broken = recs.filter(r => r.status===404 || r.status===410 || (r.status>=500));
  const good_imgs = recs.filter(r => r.type==='image' && r.status===200).map(r=>r.url);
  return JSON.stringify({page: location.pathname, checked: recs.length, broken, good_imgs});
})()
