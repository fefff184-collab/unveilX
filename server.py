"""
unveilX - servidor unico
Sirve el sitio web Y conecta con deobfuscator.py

Estructura del repo en GitHub:
    /
    ├── server.py          <- este archivo
    ├── deobfuscator.py    <- tu archivo sin tocar
    ├── trace_to_lua.py    <- si lo tienes
    └── lua_bin/
        └── lua5.1.exe

Instalar dependencias:
    pip install flask flask-cors

Correr:
    python server.py
    Abrir: http://localhost:5000
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import importlib.util
import tempfile
import glob
import os

app = Flask(__name__)
CORS(app)

# ── Cargar deobfuscator.py sin ejecutar main() ────────────────────────────────
def _load_deobfuscator():
    path = os.path.join(os.path.dirname(__file__), "deobfuscator.py")
    spec = importlib.util.spec_from_file_location("deobfuscator", path)
    mod  = importlib.util.module_from_spec(spec)
    mod.__name__ = "_deobfuscator_imported"
    spec.loader.exec_module(mod)
    return mod

try:
    deob = _load_deobfuscator()
    print("[OK] deobfuscator.py cargado")
except Exception as e:
    deob = None
    print(f"[ERROR] No se pudo cargar deobfuscator.py: {e}")

# ── HTML inline ───────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>unveilX</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap" rel="stylesheet">
<style>
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  :root{
    --ac:#5865F2;--ag:rgba(88,101,242,.35);--gn:#00e87a;--rd:#ff4545;
    --bg:#000;--s1:#0a0a0a;--s2:#111;--b1:#1c1c1c;--b2:#2a2a2a;--mt:#555;--tx:#e8e8e8;
  }
  html{scroll-behavior:smooth}
  body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--tx);overflow-x:hidden;min-height:100vh}
  body::before{
    content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
    background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),
      linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);
    background-size:60px 60px;
    mask-image:radial-gradient(ellipse 80% 60% at 50% 0%,black 40%,transparent 100%);
  }
  .orb{
    position:fixed;width:800px;height:500px;border-radius:50%;pointer-events:none;z-index:0;
    background:radial-gradient(ellipse,rgba(88,101,242,.12) 0%,transparent 65%);
    top:-150px;left:50%;transform:translateX(-50%);
    animation:orbP 6s ease-in-out infinite;
  }
  @keyframes orbP{0%,100%{opacity:.8;transform:translateX(-50%) scale(1)}50%{opacity:1;transform:translateX(-50%) scale(1.05)}}

  nav{
    position:fixed;top:0;left:0;right:0;height:64px;
    display:flex;align-items:center;justify-content:space-between;padding:0 48px;
    background:rgba(0,0,0,.7);backdrop-filter:blur(20px) saturate(1.4);
    border-bottom:1px solid var(--b1);z-index:100;
    opacity:0;animation:dn .5s .1s cubic-bezier(.16,1,.3,1) forwards;
  }
  @keyframes dn{from{opacity:0;transform:translateY(-16px)}to{opacity:1;transform:translateY(0)}}
  .logo{font-size:1rem;font-weight:800;letter-spacing:-.5px;color:#fff}
  .logo span{color:var(--ac)}
  .nav-r{display:flex;align-items:center;gap:8px}

  .badge{
    display:flex;align-items:center;gap:6px;font-size:.75rem;font-weight:500;
    color:var(--mt);padding:5px 12px;border:1px solid var(--b1);border-radius:999px;background:var(--s1);transition:all .3s;
  }
  .badge.on{color:var(--gn);border-color:rgba(0,232,122,.2)}
  .badge.off{color:var(--rd);border-color:rgba(255,69,69,.2)}
  .dsm{width:5px;height:5px;border-radius:50%;background:currentColor;flex-shrink:0}
  .badge.on .dsm{box-shadow:0 0 6px var(--gn);animation:pu 2s infinite}

  .pill{
    display:none;align-items:center;gap:10px;background:var(--s1);
    border:1px solid var(--b2);border-radius:999px;padding:5px 16px 5px 5px;
  }
  .pill img{width:28px;height:28px;border-radius:50%;border:1.5px solid var(--ac)}
  .pill span{font-size:.82rem;font-weight:500;color:#bbb}

  .btn{
    display:inline-flex;align-items:center;gap:9px;padding:13px 24px;border:none;border-radius:10px;
    font-family:inherit;font-size:.9rem;font-weight:600;cursor:pointer;
    transition:all .2s cubic-bezier(.16,1,.3,1);text-decoration:none;line-height:1;
  }
  .bp{background:var(--ac);color:#fff}
  .bp:hover{background:#6673f5;transform:translateY(-2px);box-shadow:0 12px 32px var(--ag)}
  .bp:disabled{opacity:.5;cursor:not-allowed;transform:none;box-shadow:none}
  .bo{background:transparent;color:var(--mt);border:1px solid var(--b2)}
  .bo:hover{background:var(--s2);border-color:#3a3a3a;color:#ccc;transform:translateY(-2px)}
  .bsm{padding:8px 16px;font-size:.8rem;border-radius:8px}

  .hero{
    position:relative;z-index:1;min-height:100vh;
    display:flex;flex-direction:column;justify-content:center;align-items:center;
    text-align:center;padding:120px 24px 100px;
  }
  .eyebrow{
    display:inline-flex;align-items:center;gap:8px;font-size:.72rem;font-weight:600;
    letter-spacing:2px;text-transform:uppercase;color:var(--ac);
    border:1px solid rgba(88,101,242,.25);background:rgba(88,101,242,.06);
    padding:6px 16px;border-radius:999px;margin-bottom:32px;
    opacity:0;animation:rs .7s .3s cubic-bezier(.16,1,.3,1) forwards;
  }
  .edot{width:5px;height:5px;border-radius:50%;background:var(--ac);box-shadow:0 0 8px var(--ac)}
  h1{
    font-size:clamp(2.8rem,7vw,5.5rem);font-weight:900;line-height:1;
    letter-spacing:-3px;color:#fff;max-width:820px;
    opacity:0;animation:rs .7s .45s cubic-bezier(.16,1,.3,1) forwards;
  }
  h1 em{
    font-style:normal;
    background:linear-gradient(135deg,#7b89ff,#5865F2 50%,#3d4fc2);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  }
  @keyframes rs{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:translateY(0)}}
  .sub{
    margin:24px 0 44px;color:var(--mt);font-size:1rem;line-height:1.7;max-width:440px;
    opacity:0;animation:rs .7s .6s cubic-bezier(.16,1,.3,1) forwards;
  }
  .cta{
    display:flex;gap:12px;flex-wrap:wrap;justify-content:center;
    opacity:0;animation:rs .7s .75s cubic-bezier(.16,1,.3,1) forwards;
  }

  .stats{
    position:relative;z-index:1;display:flex;justify-content:center;
    max-width:700px;margin:-20px auto 0;padding:0 24px;
    opacity:0;animation:rs .7s .9s cubic-bezier(.16,1,.3,1) forwards;
  }
  .stat{flex:1;text-align:center;padding:28px 20px;border:1px solid var(--b1);background:var(--s1)}
  .stat:first-child{border-radius:12px 0 0 12px}
  .stat:last-child{border-radius:0 12px 12px 0;border-left:none}
  .stat:not(:first-child):not(:last-child){border-left:none}
  .sv{font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-1px;display:block}
  .sl{font-size:.75rem;color:var(--mt);font-weight:500;margin-top:4px;display:block;text-transform:uppercase;letter-spacing:.5px}

  .feats{
    position:relative;z-index:1;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
    gap:1px;max-width:900px;margin:100px auto 120px;padding:0 24px;
    background:var(--b1);border:1px solid var(--b1);border-radius:16px;overflow:hidden;
  }
  .fc{background:var(--s1);padding:36px 32px;transition:background .2s}
  .fc:hover{background:#0f0f0f}
  .fi{
    width:38px;height:38px;border-radius:9px;background:rgba(88,101,242,.15);
    border:1px solid rgba(88,101,242,.2);display:flex;align-items:center;
    justify-content:center;margin-bottom:20px;color:#a0a8ff;
  }
  .fc h3{font-size:.95rem;font-weight:600;color:#fff;margin-bottom:10px}
  .fc p{font-size:.85rem;color:var(--mt);line-height:1.7}

  .app{
    display:none;position:relative;z-index:1;max-width:860px;margin:0 auto;
    padding:80px 24px;opacity:0;animation:rs .5s ease forwards;
  }
  .sh{margin-bottom:32px}
  .sh h2{font-size:1.4rem;font-weight:700;color:#fff;letter-spacing:-.5px}
  .sh p{color:var(--mt);font-size:.87rem;margin-top:6px}

  .editor{background:var(--s1);border:1px solid var(--b1);border-radius:14px;overflow:hidden}
  .ebar{
    display:flex;align-items:center;justify-content:space-between;
    padding:12px 16px;border-bottom:1px solid var(--b1);background:var(--s2);
  }
  .dots{display:flex;gap:6px;align-items:center}
  .dots span{width:11px;height:11px;border-radius:50%}
  .d1{background:#ff5f57}.d2{background:#febc2e}.d3{background:#28c840}
  .fn{font-size:.75rem;color:var(--mt);font-family:'Consolas',monospace}

  textarea{
    width:100%;background:transparent;color:#d4d4d4;border:none;outline:none;
    padding:20px 22px;font-family:'Consolas','Fira Code','Monaco',monospace;
    font-size:.87rem;line-height:1.75;resize:vertical;min-height:200px;
  }
  textarea::placeholder{color:#333}
  textarea[readonly]{color:#b0d090;cursor:default}

  .efoot{
    display:flex;align-items:center;gap:10px;flex-wrap:wrap;
    padding:14px 16px;border-top:1px solid var(--b1);background:var(--s2);
  }

  .outsec{display:none;margin-top:16px}
  .ostatus{
    display:flex;align-items:center;gap:8px;font-size:.78rem;font-weight:600;
    color:var(--gn);text-transform:uppercase;letter-spacing:1px;
  }
  .sdot{width:6px;height:6px;border-radius:50%;background:currentColor;box-shadow:0 0 10px currentColor}
  @keyframes pu{0%,100%{opacity:1}50%{opacity:.4}}
  .ostatus .sdot{animation:pu 2s infinite}

  .errbox{
    display:none;background:rgba(255,69,69,.06);border:1px solid rgba(255,69,69,.2);
    border-radius:10px;padding:16px 20px;margin-top:16px;font-size:.85rem;
    color:#ff8080;font-family:'Consolas',monospace;line-height:1.6;white-space:pre-wrap;word-break:break-word;
  }

  .spin{
    width:15px;height:15px;border:2px solid rgba(255,255,255,.15);
    border-top-color:#fff;border-radius:50%;animation:sp .65s linear infinite;display:none;
  }
  @keyframes sp{to{transform:rotate(360deg)}}

  .toast{
    position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(10px);
    background:var(--s2);border:1px solid var(--b2);border-radius:9px;
    padding:10px 22px;font-size:.83rem;font-weight:500;color:var(--tx);
    opacity:0;transition:opacity .25s,transform .25s;pointer-events:none;z-index:999;white-space:nowrap;
  }
  .toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
  .toast.ok{border-color:rgba(0,232,122,.3);color:var(--gn)}
  .toast.ko{border-color:rgba(255,69,69,.3);color:var(--rd)}

  footer{
    position:relative;z-index:1;text-align:center;padding:40px 24px;
    border-top:1px solid var(--b1);color:var(--mt);font-size:.8rem;
  }
  footer a{color:var(--ac);text-decoration:none}
  footer a:hover{text-decoration:underline}
</style>
</head>
<body>
<div class="orb"></div>
<div class="toast" id="T"></div>

<nav>
  <div class="logo">unveil<span>X</span></div>
  <div class="nav-r">
    <div class="badge" id="B"><span class="dsm"></span><span id="BT">checking...</span></div>
    <div class="pill" id="pill"><img id="av" src="" alt=""><span id="un"></span></div>
    <button class="btn bo bsm" id="lbtn" onclick="login()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057c.002.022.015.043.033.055a19.9 19.9 0 0 0 5.993 3.03.077.077 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03z"/></svg>
      Login
    </button>
  </div>
</nav>

<section class="hero" id="HS">
  <div class="eyebrow"><span class="edot"></span>New Generation</div>
  <h1>The <em>fastest</em> dumper<br>ever built</h1>
  <p class="sub">Powerful deobfuscation engine, free 24/7 API access, and instant Discord support.</p>
  <div class="cta">
    <button class="btn bp" onclick="login()">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057c.002.022.015.043.033.055a19.9 19.9 0 0 0 5.993 3.03.077.077 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03z"/></svg>
      Login with Discord
    </button>
    <button class="btn bo" onclick="document.getElementById('FS').scrollIntoView({behavior:'smooth'})">View features</button>
  </div>
</section>

<div class="stats" id="FS">
  <div class="stat"><span class="sv">10K+</span><span class="sl">Dumps processed</span></div>
  <div class="stat"><span class="sv">99.9%</span><span class="sl">Uptime</span></div>
  <div class="stat"><span class="sv">Free</span><span class="sl">API access</span></div>
</div>

<div class="feats">
  <div class="fc">
    <div class="fi"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>
    <h3>Instant Dump</h3><p>Lightning-fast deobfuscation engine. Paste your code and get clean output in milliseconds.</p>
  </div>
  <div class="fc">
    <div class="fi"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>
    <h3>Free API Key</h3><p>Every member gets a free 24/7 API key with no rate limiting and zero hidden fees.</p>
  </div>
  <div class="fc">
    <div class="fi"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></div>
    <h3>24/7 Support</h3><p>Our team is always online in Discord to help you with your API key or any issues.</p>
  </div>
</div>

<div class="app" id="AS">
  <div class="sh"><h2>Dumper</h2><p>Paste obfuscated Lua code below and dump it instantly.</p></div>

  <div class="editor">
    <div class="ebar">
      <div class="dots"><span class="d1"></span><span class="d2"></span><span class="d3"></span></div>
      <span class="fn">input.lua</span><div></div>
    </div>
    <textarea id="inp" placeholder="-- Paste obfuscated Lua code here..."></textarea>
    <div class="efoot">
      <button class="btn bp" onclick="runDump()" id="DB">
        <div class="spin" id="SP"></div>
        <span id="DL">Dump</span>
      </button>
      <button class="btn bo bsm" onclick="clearAll()">Clear</button>
    </div>
  </div>

  <div class="errbox" id="EB"></div>

  <div class="outsec" id="OS">
    <div class="editor">
      <div class="ebar">
        <div class="ostatus"><span class="sdot"></span>Deobfuscated</div>
        <div style="display:flex;gap:8px">
          <button class="btn bo bsm" onclick="copyOut()">Copy</button>
          <button class="btn bo bsm" onclick="dlOut()">Download</button>
        </div>
      </div>
      <textarea id="out" readonly></textarea>
    </div>
  </div>
</div>

<footer>&copy; 2025 unveilX &mdash; <a href="https://discord.gg/z3B6qWybM">Join Discord</a></footer>

<script>
  const CID = '1497317363526139994';
  const RDR = window.location.origin + window.location.pathname;

  let _tt=null;
  function toast(m,c='',ms=2600){
    const e=document.getElementById('T');
    e.textContent=m;e.className='toast show '+c;
    clearTimeout(_tt);_tt=setTimeout(()=>e.className='toast',ms);
  }

  async function checkHealth(){
    const b=document.getElementById('B'),t=document.getElementById('BT');
    try{
      const r=await fetch('/api/health',{signal:AbortSignal.timeout(3000)});
      const d=await r.json();
      b.className=d.ok?'badge on':'badge off';
      t.textContent=d.ok?'server online':'server error';
    }catch{b.className='badge off';t.textContent='server offline';}
  }

  function login(){
    const s=crypto.randomUUID();sessionStorage.setItem('os',s);
    const u=new URL('https://discord.com/api/oauth2/authorize');
    u.searchParams.set('client_id',CID);u.searchParams.set('redirect_uri',RDR);
    u.searchParams.set('response_type','token');u.searchParams.set('scope','identify');
    u.searchParams.set('state',s);window.location.href=u.toString();
  }

  function parseCallback(){
    const p=new URLSearchParams(window.location.hash.slice(1));
    const token=p.get('access_token'),state=p.get('state');
    if(!token)return null;
    if(state!==sessionStorage.getItem('os')){toast('Auth error.','ko');return null;}
    sessionStorage.removeItem('os');
    history.replaceState(null,'',window.location.pathname);
    const exp=Date.now()+parseInt(p.get('expires_in')||'604800',10)*1000;
    localStorage.setItem('dx_t',token);localStorage.setItem('dx_e',String(exp));
    return token;
  }

  async function fetchUser(token){
    const r=await fetch('https://discord.com/api/users/@me',{headers:{Authorization:'Bearer '+token}});
    if(!r.ok)throw new Error('bad token');return r.json();
  }

  function showApp(user){
    const av=user.avatar
      ?`https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=64`
      :`https://cdn.discordapp.com/embed/avatars/${(parseInt(user.discriminator)||0)%5}.png`;
    document.getElementById('av').src=av;
    document.getElementById('un').textContent=user.global_name||user.username;
    document.getElementById('pill').style.display='flex';
    document.getElementById('lbtn').style.display='none';
    document.getElementById('HS').style.display='none';
    document.getElementById('AS').style.display='block';
    toast('Welcome, '+(user.global_name||user.username));
  }

  window.addEventListener('load',async()=>{
    checkHealth();setInterval(checkHealth,30000);
    let token=parseCallback()||localStorage.getItem('dx_t');
    if(!token)return;
    if(Date.now()>parseInt(localStorage.getItem('dx_e')||'0',10)){
      localStorage.removeItem('dx_t');localStorage.removeItem('dx_e');return;
    }
    try{showApp(await fetchUser(token));}
    catch{localStorage.removeItem('dx_t');localStorage.removeItem('dx_e');}
  });

  async function runDump(){
    const code=document.getElementById('inp').value.trim();
    if(!code){toast('Paste code first.','ko');return;}
    document.getElementById('SP').style.display='block';
    document.getElementById('DL').textContent='Dumping...';
    document.getElementById('DB').disabled=true;
    document.getElementById('EB').style.display='none';
    document.getElementById('OS').style.display='none';
    try{
      const res=await fetch('/api/dump',{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({code})
      });
      const d=await res.json();
      if(d.ok){
        document.getElementById('out').value=d.output;
        document.getElementById('OS').style.display='block';
        document.getElementById('OS').scrollIntoView({behavior:'smooth',block:'nearest'});
        toast('Done.','ok');
      }else{
        document.getElementById('EB').textContent=d.error||'Unknown error.';
        document.getElementById('EB').style.display='block';
        toast('Dump failed.','ko');
      }
    }catch(e){
      document.getElementById('EB').textContent='Server unreachable.\nRun: python server.py\n\n'+e.message;
      document.getElementById('EB').style.display='block';
      toast('Server offline.','ko');
    }
    document.getElementById('SP').style.display='none';
    document.getElementById('DL').textContent='Dump';
    document.getElementById('DB').disabled=false;
  }

  function clearAll(){
    document.getElementById('inp').value='';
    document.getElementById('OS').style.display='none';
    document.getElementById('EB').style.display='none';
  }
  function copyOut(){
    navigator.clipboard.writeText(document.getElementById('out').value)
      .then(()=>toast('Copied.','ok'));
  }
  function dlOut(){
    const b=new Blob([document.getElementById('out').value],{type:'text/plain'});
    const a=document.createElement('a');a.href=URL.createObjectURL(b);
    a.download='dumped.lua';a.click();
  }
</script>
</body>
</html>"""

# ── Rutas ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return Response(HTML, mimetype="text/html")

@app.route("/api/health")
def health():
    return jsonify({
        "ok": True,
        "lua":          os.path.exists(os.path.join("lua_bin", "lua5.1.exe")),
        "deobfuscator": deob is not None
    })

@app.route("/api/dump", methods=["POST"])
def api_dump():
    data = request.get_json(silent=True)
    if not data or not data.get("code", "").strip():
        return jsonify({"ok": False, "error": "No code provided"}), 400

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8",
        suffix=".lua", delete=False, prefix="ux_"
    ) as f:
        tmp = f.name
        f.write(data["code"])

    report = tmp + ".report.txt"
    deobf  = tmp + ".deobf.lua"

    try:
        deob.deobfuscate_file(tmp)
    except Exception as e:
        _cleanup(tmp, report, deobf)
        return jsonify({"ok": False, "error": str(e)}), 500

    output = _read_del(deobf) or _read_del(report)
    _cleanup(tmp)

    if output:
        return jsonify({"ok": True, "output": output})
    return jsonify({
        "ok": False,
        "error": "Deobfuscator ran but produced no output.\n"
                 "Check that lua_bin/lua5.1.exe exists and the code is compatible."
    }), 500


def _read_del(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            c = f.read()
        os.remove(path)
        return c or None
    except Exception:
        return None

def _cleanup(*paths):
    for p in paths:
        if p and os.path.exists(p):
            try: os.remove(p)
            except Exception: pass
    for f in glob.glob("ux_*.lua*"):
        try: os.remove(f)
        except Exception: pass


if __name__ == "__main__":
    print("unveilX corriendo en http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
