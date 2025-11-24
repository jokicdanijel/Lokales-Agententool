// assets/js/api_client.js
export const api = {
  async get(url){
    const r = await fetch(url, { headers: { 'Accept':'application/json' } });
    if(!r.ok) throw new Error('GET '+url+' failed');
    return r.json();
  },
  async post(url, body){
    const r = await fetch(url, {
      method:'POST',
      headers:{ 'Content-Type':'application/json', 'Accept':'application/json' },
      body: JSON.stringify(body||{})
    });
    if(!r.ok) throw new Error('POST '+url+' failed');
    try{ return await r.json(); } catch(_){ return {}; }
  }
};
