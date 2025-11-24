// assets/js/state.js
import { api } from './api_client.js';
import { sendEvent } from './telemetry.js';

const mountMain = async (htmlPath) => {
  const res = await fetch(htmlPath);
  const html = await res.text();
  document.querySelector('main .content').innerHTML = html;
  initComponents();
};

export async function loadPage(name, params={}){
  const map = {
    'agent_opena5': '/pages/agent_opena5.html',
    'agent_opena5_logs': '/pages/agent_opena5_logs.html',
    'agent_opena5_config': '/pages/agent_opena5_config.html'
  };
  await mountMain(map[name]);
  sendEvent('nav.route_change', {route: location.hash.replace('#','')});
}

async function loadComponent(name, mountId){
  const res = await fetch(`/components/${name}.html`);
  const html = await res.text();
  const mount = document.getElementById(mountId);
  if(mount){ mount.innerHTML = html; }
}

function bindControlBar(){
  const toggle = document.getElementById('agent_toggle');
  const preset = document.getElementById('model_preset');
  const apiForm = document.getElementById('apikey_form');
  const apiClear = document.getElementById('api_clear');
  const inputForm = document.getElementById('agent_input_form');
  const agentId = 'opena5';

  // Load config
  api.get(`/api/agents/${agentId}/config`).then(cfg => {
    if(toggle) toggle.checked = !!cfg.enabled;
    if(preset && cfg.model_preset) preset.value = cfg.model_preset;
  }).catch(()=>{});

  if(toggle){
    toggle.addEventListener('change', async (e)=>{
      const enabled = e.target.checked;
      try{
        await api.post(`/api/agents/${agentId}/config`, { enabled });
        sendEvent('agent.toggle', {agentId, enabled});
      }catch(_){ e.target.checked = !enabled; }
    });
  }

  if(preset){
    preset.addEventListener('change', async (e)=>{
      const model_preset = e.target.value;
      try{
        await api.post(`/api/agents/${agentId}/config`, { model_preset });
        sendEvent('agent.model_preset.change', {agentId, preset:model_preset});
      }catch(_){ /* revert not implemented */ }
    });
  }

  if(apiForm){
    apiForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const api_key = document.getElementById('api_key').value;
      await api.post(`/api/agents/${agentId}/config`, { api_key });
      sendEvent('agent.apikey.save', {agentId, hasKey:true});
    });
  }

  if(apiClear){
    apiClear.addEventListener('click', async ()=>{
      await api.post(`/api/agents/${agentId}/config`, { api_key: '' });
      sendEvent('agent.apikey.save', {agentId, hasKey:false});
    });
  }

  if(inputForm){
    inputForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const text = document.getElementById('agent_input').value.trim();
      if(!text) return;
      const res = await api.post(`/api/agents/${agentId}/input`, { text });
      sendEvent('agent.input.submit', {agentId, text_len:text.length});
      document.getElementById('agent_input').value = '';
    });
  }
}

function bindJobsTable(){
  const tbl = document.getElementById('jobs_table');
  if(!tbl) return;
  tbl.addEventListener('click', async (e)=>{
    const btn = e.target.closest('button[data-action]');
    if(!btn) return;
    const action = btn.getAttribute('data-action');
    const jobId = btn.getAttribute('data-id');
    const agentId = 'opena5';
    if(action==='retry'){
      await api.post(`/api/agents/${agentId}/jobs/${jobId}/retry`,{});
      sendEvent('jobs.retry', {agentId, jobId});
    }
    if(action==='cancel'){
      await api.post(`/api/agents/${agentId}/jobs/${jobId}/cancel`,{});
      sendEvent('jobs.cancel', {agentId, jobId});
    }
  });
}

function initLogs(){
  const mount = document.getElementById('log_console_mount');
  if(!mount) return;
  const ws = new WebSocket((location.protocol==='https:'?'wss':'ws') + '://' + location.host + '/api/agents/opena5/logs');
  ws.onmessage = (evt)=>{
    const msg = JSON.parse(evt.data);
    const line = document.createElement('div');
    line.textContent = `[${msg.ts}] ${msg.level.toUpperCase()} — ${msg.msg}`;
    mount.appendChild(line);
    mount.scrollTop = mount.scrollHeight;
  };
}

export function initComponents(){
  // Mount Control Bar if requested
  document.querySelectorAll('[data-component="control_bar"]').forEach(async (el)=>{
    await loadComponent('control_bar', 'control_bar_mount');
    bindControlBar();
  });

  // Mount stat cards container
  if(document.getElementById('statcards_mount')){
    // simple placeholders; real data via API
    const sc = document.getElementById('statcards_mount');
    sc.innerHTML = `
      <div class="kpi-grid grid">
        <section class="stat_card"><h3 class="stat_title">Uptime</h3><p class="stat_value" data-testid="uptime">--</p></section>
        <section class="stat_card"><h3 class="stat_title">Total Jobs</h3><p class="stat_value" data-testid="total_jobs">--</p></section>
        <section class="stat_card"><h3 class="stat_title">Success Rate</h3><p class="stat_value" data-testid="success_rate">--</p></section>
      </div>`;
    api.get('/api/agents/opena5/metrics').then(m=>{
      const fmt = (v)=> (typeof v==='number'? v : (v??'--'));
      document.querySelector('[data-testid="uptime"]').textContent = fmt(m.uptime);
      document.querySelector('[data-testid="total_jobs"]').textContent = fmt(m.total_jobs);
      document.querySelector('[data-testid="success_rate"]').textContent = fmt(m.success_rate);
    }).catch(()=>{});
  }

  // Mount jobs table
  if(document.getElementById('jobs_table_mount')){
    await loadComponent('jobs_table', 'jobs_table_mount');
    bindJobsTable();
    // Populate
    api.get('/api/agents/opena5/jobs?limit=50').then(rows=>{
      const tbody = document.querySelector('#jobs_table tbody');
      tbody.innerHTML = rows.map(r=>`
        <tr>
          <td>${r.id}</td>
          <td>${r.model_preset}</td>
          <td>${r.status}</td>
          <td>${r.started_at||''}</td>
          <td>${r.duration_ms||''}</td>
          <td>
            <button data-action="retry" data-id="${r.id}">Retry</button>
            <button data-action="cancel" data-id="${r.id}">Cancel</button>
          </td>
        </tr>`).join('');
    }).catch(()=>{});
  }

  // Mount last result
  if(document.getElementById('last_result_mount')){
    await loadComponent('json_viewer', 'last_result_mount');
  }

  // Logs page
  initLogs();
}
