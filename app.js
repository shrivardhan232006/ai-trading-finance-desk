const $ = id => document.getElementById(id);
const money = n => new Intl.NumberFormat('en-IN',{maximumFractionDigits:2}).format(n);
function render(d){
  const r=d.research,s=d.signal,k=d.risk,p=d.portfolio;
  $('signal').textContent=`${s.action} ${s.quantity}`;$('signalMeta').textContent=`entry ₹${money(s.entry)}`;
  $('confidence').textContent=`${Math.round(r.confidence*100)}%`;$('risk').textContent=k.approved?'APPROVED':'REJECTED';$('risk').style.color=k.approved?'var(--green)':'var(--red)';$('riskMeta').textContent=k.reasons.join(' · ');
  $('equity').textContent=`₹${money(p.equity)}`;$('pnl').textContent=`P&L ₹${money(p.pnl)}`;$('trend').textContent=r.trend.toUpperCase();$('narrative').textContent=r.narrative;$('price').textContent=`₹${money(r.price)}`;$('volatility').textContent=`${(r.volatility*100).toFixed(1)}%`;$('sources').textContent=r.sources.length;
  $('entry').textContent=`₹${money(s.entry)}`;$('stop').textContent=`₹${money(s.stop)}`;$('target').textContent=`₹${money(s.target)}`;$('rr').textContent=`${s.rr}:1`;$('reasoning').textContent=s.reasoning.join(' · ');$('fill').textContent=d.fill?d.fill.status:'NO FILL';$('fill').style.color=d.fill?'var(--green)':'var(--muted)';
  $('auditCount').textContent=`${d.audit_events.length} events`;$('auditRows').innerHTML=d.audit_events.map(e=>`<div class="audit-row"><span>${new Date(e.time).toLocaleTimeString()}</span><b>${e.agent}</b><code>${e.event}</code></div>`).join('');
}
async function run(){ $('run').disabled=true;$('status').textContent='Running research → signal → risk → execution → review…';try{const q=new URLSearchParams({symbol:$('symbol').value,capital:$('capital').value});const res=await fetch('/api/run?'+q);if(!res.ok)throw new Error('API error');render(await res.json());$('status').textContent='Cycle complete. Paper execution only.'}catch(e){$('status').textContent='Start the Python server with: python trading-bot.py --serve'}finally{$('run').disabled=false}}
$('run').addEventListener('click',run);run();
