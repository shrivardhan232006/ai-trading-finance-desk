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
function browserDemo(symbol, capital){
  const price = symbol.length * 97.13 + 500, stop = price * .975, target = price * 1.05, qty = Math.max(1, Math.floor(capital * .01 / (price-stop)));
  const t = new Date().toISOString();
  return {mode:'PAPER_ONLY_BROWSER_DEMO',research:{symbol,price,trend:'bullish',volatility:.18,narrative:`${symbol} demo feed shows a constructive trend with a 10-day average above the 30-day average. This browser-only result is illustrative.`,confidence:.68,sources:['browser demo feed','moving averages','realized volatility']},signal:{symbol,action:'BUY',entry:price,stop,target,quantity:qty,rr:2,reasoning:['fast average above slow average','confidence clears threshold'],confidence:.68},risk:{approved:true,quantity:qty,risk_amount:qty*(price-stop),reasons:['within 1% portfolio risk budget']},fill:{order_id:'DEMO-001',symbol,side:'BUY',quantity:qty,price,status:'PAPER_FILLED',time:t},portfolio:{cash:capital-qty*price,position:qty,equity:capital+qty*(price-price),pnl:0},compliance:{status:'PASS',paper_only:true,reasoning_logged:true},audit_events:[['research','brief'],['quant','signal'],['risk','decision'],['execution','paper_fill'],['compliance','review']].map(([agent,event])=>({time:t,agent,event,payload:{browser_demo:true}}))};
}
async function run(){ $('run').disabled=true;$('status').textContent='Running research → signal → risk → execution → review…';try{const q=new URLSearchParams({symbol:$('symbol').value,capital:$('capital').value});const res=await fetch('/api/run?'+q);if(!res.ok)throw new Error('API error');render(await res.json());$('status').textContent='Cycle complete. Paper execution only.'}catch(e){render(browserDemo($('symbol').value.toUpperCase(),Number($('capital').value)));$('status').textContent='Browser demo cycle complete. Start the Python server for the full local API.'}finally{$('run').disabled=false}}
$('run').addEventListener('click',run);run();
