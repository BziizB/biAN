const paths = {
  state: 'paper_trading/state.json',
  trades: 'paper_trading/paper_trades.csv',
  signals: 'paper_trading/paper_signals.csv',
  report: 'paper_trading/paper_daily_report.md'
};

const fmt = (v, digits = 4) => {
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(digits) : (v ?? '');
};

async function text(path) {
  const res = await fetch(`${path}?t=${Date.now()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`${path} ${res.status}`);
  return res.text();
}

function parseCsv(src) {
  const rows = src.trim() ? src.trim().split(/\r?\n/) : [];
  if (!rows.length) return [];
  const parseLine = line => {
    const out = [];
    let cur = '';
    let q = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; }
      else if (ch === '"') q = !q;
      else if (ch === ',' && !q) { out.push(cur); cur = ''; }
      else cur += ch;
    }
    out.push(cur);
    return out;
  };
  const headers = parseLine(rows[0].replace(/^\uFEFF/, ''));
  return rows.slice(1).map(line => Object.fromEntries(parseLine(line).map((v, i) => [headers[i], v])));
}

function table(el, rows, cols) {
  el.innerHTML = `<thead><tr>${cols.map(c => `<th>${c.label}</th>`).join('')}</tr></thead><tbody>${rows.length ? rows.map(row => `<tr>${cols.map(c => `<td>${c.format ? c.format(row[c.key], row) : (row[c.key] ?? '')}</td>`).join('')}</tr>`).join('') : `<tr><td colspan="${cols.length}">No rows</td></tr>`}</tbody>`;
}

function card(label, value, cls = '') {
  return `<article class="card"><span>${label}</span><strong class="${cls}">${value}</strong></article>`;
}

async function load() {
  const [stateRaw, tradesRaw, signalsRaw, report] = await Promise.all([
    text(paths.state).catch(() => '{}'),
    text(paths.trades).catch(() => ''),
    text(paths.signals).catch(() => ''),
    text(paths.report).catch(err => String(err))
  ]);
  const state = JSON.parse(stateRaw || '{}');
  const trades = parseCsv(tradesRaw).filter(r => r.status === 'CLOSED');
  const signals = parseCsv(signalsRaw);
  const open = Object.values(state.markets || {}).filter(m => m.position_status === 'OPEN');
  const net = trades.reduce((s, r) => s + (Number(r.net_R) || 0), 0);
  const warnings = state.warnings || [];
  document.getElementById('cards').innerHTML = [
    card('Status', warnings.length ? 'WARNING' : 'Observing', warnings.length ? 'warn' : 'good'),
    card('Open Positions', open.length),
    card('Closed Trades', trades.length),
    card('Cumulative net_R', fmt(net), net >= 0 ? 'good' : 'bad'),
    card('Mismatch Rate', fmt((state.consistency?.mismatch_rate || 0) * 100, 2) + '%'),
    card('Data End', state.last_data_time || 'NA')
  ].join('');
  table(document.getElementById('positionsTable'), open, [
    {key:'market', label:'Market'}, {key:'entry_time', label:'Entry Time'}, {key:'entry_price', label:'Entry', format:fmt},
    {key:'stop_loss', label:'SL', format:fmt}, {key:'take_profit', label:'TP', format:fmt},
    {key:'bars_held', label:'Bars'}, {key:'unrealized_R', label:'Unrealized R', format:fmt}
  ]);
  table(document.getElementById('signalsTable'), signals.slice(-20).reverse(), [
    {key:'signal_time', label:'Time'}, {key:'market', label:'Market'}, {key:'signal_valid', label:'Valid'},
    {key:'skip_reason', label:'Skip'}, {key:'adx', label:'ADX', format:fmt}, {key:'close', label:'Close', format:fmt}
  ]);
  table(document.getElementById('tradesTable'), trades.slice(-20).reverse(), [
    {key:'exit_time', label:'Exit Time'}, {key:'market', label:'Market'}, {key:'exit_reason', label:'Reason'},
    {key:'net_R', label:'net_R', format:fmt}, {key:'mfe_R', label:'MFE', format:fmt}, {key:'mae_R', label:'MAE', format:fmt}
  ]);
  document.getElementById('dailyReport').textContent = report;
}

document.getElementById('refreshBtn').addEventListener('click', load);
load().catch(err => { document.getElementById('dailyReport').textContent = err.stack || String(err); });
setInterval(load, 60000);
