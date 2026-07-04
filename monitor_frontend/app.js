const paths = {
  state: 'paper_trading/state.json',
  trades: 'paper_trading/paper_trades.csv',
  signals: 'paper_trading/paper_signals.csv'
};

const markets = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'LINK', 'AVAX', 'LTC'];
const BEIJING_OFFSET_MS = 8 * 60 * 60 * 1000;
const BAR_MINUTES = 15;
const HISTORICAL_MAX_DD_R = 39.87957723494097;

const pad = value => String(value).padStart(2, '0');
const finite = value => Number.isFinite(Number(value));
const asNumber = value => finite(value) ? Number(value) : null;
const isTrue = value => value === true || String(value).toLowerCase() === 'true' || String(value) === '1';
const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;'}[char]));

const fmt = (value, digits = 4) => {
  const n = asNumber(value);
  return n === null ? '--' : n.toFixed(digits);
};

const fmtR = value => {
  const n = asNumber(value);
  if (n === null) return '--';
  const text = n.toFixed(4);
  return n > 0 ? `+${text}` : text;
};

const fmtPct = value => {
  const n = asNumber(value);
  return n === null ? 'NA' : `${(n * 100).toFixed(2)}%`;
};

function parseUtc(value) {
  if (!value) return null;
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value;
  const text = String(value).trim();
  if (!text) return null;
  const match = text.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?/);
  if (match && !/[zZ]|[+-]\d{2}:?\d{2}$/.test(text)) {
    const [, y, mo, d, h, mi, s = '0'] = match;
    return new Date(Date.UTC(Number(y), Number(mo) - 1, Number(d), Number(h), Number(mi), Number(s)));
  }
  const parsed = new Date(text);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function toBeijingDate(value) {
  const utc = parseUtc(value);
  return utc ? new Date(utc.getTime() + BEIJING_OFFSET_MS) : null;
}

function formatBeijingDate(date, withSeconds = false) {
  if (!date) return '--';
  const base = `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())} ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`;
  return withSeconds ? `${base}:${pad(date.getUTCSeconds())}` : base;
}

function formatBeijing(value, withSeconds = false) {
  return formatBeijingDate(toBeijingDate(value), withSeconds);
}

function formatBeijingClock(date) {
  if (!date) return '--';
  return `${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`;
}

function formatBarWindow(value) {
  const start = toBeijingDate(value);
  if (!start) return '--';
  const end = new Date(start.getTime() + BAR_MINUTES * 60 * 1000);
  return `${formatBeijingDate(start)} - ${formatBeijingClock(end)}`;
}

function beijingDayKey(value) {
  const date = toBeijingDate(value);
  if (!date) return '';
  return `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}`;
}

function runAge(value) {
  const utc = parseUtc(value);
  if (!utc) return '--';
  const minutes = Math.max(0, Math.round((Date.now() - utc.getTime()) / 60000));
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes} 分钟前`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `${hours} 小时 ${rest} 分钟前` : `${hours} 小时前`;
}

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
  return rows.slice(1).filter(Boolean).map(line => Object.fromEntries(parseLine(line).map((v, i) => [headers[i], v])));
}

function badge(label, type = '') {
  return `<span class="badge ${type}">${escapeHtml(label)}</span>`;
}

function table(el, rows, cols) {
  const header = `<thead><tr>${cols.map(c => `<th>${escapeHtml(c.label)}</th>`).join('')}</tr></thead>`;
  const body = rows.length
    ? rows.map(row => `<tr>${cols.map(c => `<td>${c.format ? c.format(row[c.key], row) : escapeHtml(row[c.key] ?? '')}</td>`).join('')}</tr>`).join('')
    : `<tr><td colspan="${cols.length}" class="muted">暂无数据</td></tr>`;
  el.innerHTML = `${header}<tbody>${body}</tbody>`;
}

function metric(label, value, sub = '', cls = '') {
  return `<article class="metric-card"><span>${escapeHtml(label)}</span><strong class="${cls}">${escapeHtml(value)}</strong>${sub ? `<small>${escapeHtml(sub)}</small>` : ''}</article>`;
}

function sum(values) { return values.reduce((acc, value) => acc + value, 0); }
function mean(values) { return values.length ? sum(values) / values.length : null; }

function profitFactor(values) {
  const wins = sum(values.filter(v => v > 0));
  const losses = -sum(values.filter(v => v < 0));
  return losses > 0 ? wins / losses : null;
}

function drawdown(values) {
  let equity = 0;
  let peak = 0;
  let maxDD = 0;
  let currentDD = 0;
  values.forEach(value => {
    equity += value;
    peak = Math.max(peak, equity);
    currentDD = peak - equity;
    maxDD = Math.max(maxDD, currentDD);
  });
  return { maxDD, currentDD };
}

function translateSkip(reason) {
  const map = {
    no_signal: '无有效信号',
    indicator_not_ready: '指标未就绪',
    adx_below_30: 'ADX低于30',
    position_exists: '已有持仓'
  };
  return map[reason] || reason || '--';
}

function translateExit(reason) {
  return { SL: '止损', TP: '止盈', TIME: '时间退出' }[reason] || reason || '--';
}

function buildStats(state, allTrades, signals) {
  const closedTrades = allTrades.filter(row => row.status === 'CLOSED' && asNumber(row.net_R) !== null);
  const netValues = closedTrades.map(row => Number(row.net_R));
  const cumulativeNet = sum(netValues);
  const dd = drawdown(netValues);
  const reportDay = beijingDayKey(state.last_run_at) || beijingDayKey(state.last_data_time) || beijingDayKey(new Date().toISOString());
  const dailyClosed = closedTrades.filter(row => beijingDayKey(row.exit_time) === reportDay);
  const dailyEntries = allTrades.filter(row => beijingDayKey(row.entry_time) === reportDay);
  const dailySignals = signals.filter(row => isTrue(row.signal_valid) && beijingDayKey(row.signal_time) === reportDay);
  const dailyNet = sum(dailyClosed.map(row => Number(row.net_R)));
  const byMarket = markets.map(market => {
    const values = closedTrades.filter(row => row.market === market).map(row => Number(row.net_R));
    return { market, trades: values.length, net_R: sum(values), avg_R: mean(values) };
  }).sort((a, b) => (b.net_R - a.net_R) || (b.trades - a.trades));
  const positiveMarkets = byMarket.filter(row => row.net_R > 0).length;
  const last60 = netValues.slice(-60);
  return {
    reportDay,
    closedTrades,
    netValues,
    cumulativeNet,
    avgR: mean(netValues),
    winRate: netValues.length ? netValues.filter(v => v > 0).length / netValues.length : null,
    pf: profitFactor(netValues),
    maxDD: dd.maxDD,
    currentDD: dd.currentDD,
    dailyClosed,
    dailyEntries,
    dailySignals,
    dailyNet,
    byMarket,
    positiveMarkets,
    last60Avg: mean(last60),
    last60Pf: profitFactor(last60)
  };
}

function riskRows(stats) {
  return [0.001, 0.0025, 0.005, 0.01].map(risk => ({
    risk_per_trade: `${(risk * 100).toFixed(risk === 0.001 ? 1 : 2)}%`,
    estimated_return_pct: `${(stats.cumulativeNet * risk * 100).toFixed(2)}%`,
    current_drawdown_pct: `${(stats.currentDD * risk * 100).toFixed(2)}%`,
    historical_max_dd_pct_estimate: `${(HISTORICAL_MAX_DD_R * risk * 100).toFixed(2)}%`,
    suggestion: risk <= 0.0025 ? '观察可用' : (risk === 0.005 ? '不建议' : '禁止')
  }));
}

function renderReport(state, stats) {
  const warnings = state.warnings || [];
  const warningHtml = warnings.length
    ? `<ul class="warning-list">${warnings.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`
    : '<p class="note-line">暂无 WARNING。</p>';
  return `
    <div class="report-grid">
      <div class="report-item"><span>报告日期（北京）</span><strong>${escapeHtml(stats.reportDay || '--')}</strong></div>
      <div class="report-item"><span>今日信号 / 入场 / 平仓</span><strong>${stats.dailySignals.length} / ${stats.dailyEntries.length} / ${stats.dailyClosed.length}</strong></div>
      <div class="report-item"><span>今日 net_R</span><strong class="${stats.dailyNet >= 0 ? 'good' : 'bad'}">${fmtR(stats.dailyNet)}</strong></div>
      <div class="report-item"><span>累计 net_R</span><strong class="${stats.cumulativeNet >= 0 ? 'good' : 'bad'}">${fmtR(stats.cumulativeNet)}</strong></div>
      <div class="report-item"><span>胜率 / PF</span><strong>${fmtPct(stats.winRate)} / ${stats.pf === null ? 'NA' : fmt(stats.pf, 3)}</strong></div>
      <div class="report-item"><span>最大回撤 / 当前回撤</span><strong>${fmt(stats.maxDD, 4)}R / ${fmt(stats.currentDD, 4)}R</strong></div>
      <div class="report-item"><span>正收益市场</span><strong>${stats.positiveMarkets}/9</strong></div>
      <div class="report-item"><span>最近60笔 avg_R</span><strong>${stats.last60Avg === null ? 'NA' : fmtR(stats.last60Avg)}</strong></div>
      <div class="report-item"><span>最近60笔 PF</span><strong>${stats.last60Pf === null ? 'NA' : fmt(stats.last60Pf, 3)}</strong></div>
    </div>
    <h2>预警监控</h2>
    ${warningHtml}
    <p class="note-line">策略状态：Paper Trading Candidate。不是已验证实盘 Alpha，不是可重仓生产策略。</p>
    <p class="note-line">当前策略处于 paper trading 观察阶段。通过交易规则验证不等于通过 walk-forward；通过 walk-forward 不等于可实盘重仓；paper trading 有效不等于实盘 Alpha。</p>
  `;
}

async function load() {
  const [stateRaw, tradesRaw, signalsRaw] = await Promise.all([
    text(paths.state).catch(() => '{}'),
    text(paths.trades).catch(() => ''),
    text(paths.signals).catch(() => '')
  ]);
  const state = JSON.parse(stateRaw || '{}');
  const allTrades = parseCsv(tradesRaw);
  const signals = parseCsv(signalsRaw);
  const open = Object.values(state.markets || {}).filter(m => m.position_status === 'OPEN');
  const warnings = state.warnings || [];
  const stats = buildStats(state, allTrades, signals);

  document.getElementById('statusPill').className = `status-pill ${warnings.length ? 'warn' : 'good'}`;
  document.getElementById('statusPill').textContent = warnings.length ? 'WARNING' : '观察中';
  document.getElementById('lastRunTime').textContent = formatBeijing(state.last_run_at, true);
  document.getElementById('lastDataTime').textContent = formatBeijing(state.last_data_time);
  document.getElementById('barWindow').textContent = formatBarWindow(state.last_data_time);
  document.getElementById('runAge').textContent = runAge(state.last_run_at);

  document.getElementById('cards').innerHTML = [
    metric('当前状态', warnings.length ? 'WARNING' : '观察中', warnings.length ? `${warnings.length} 条预警` : '无预警', warnings.length ? 'warn' : 'good'),
    metric('当前持仓', String(open.length), '同市场最多一笔'),
    metric('累计 net_R', fmtR(stats.cumulativeNet), `${stats.closedTrades.length} 笔已平仓`, stats.cumulativeNet >= 0 ? 'good' : 'bad'),
    metric('今日 net_R', fmtR(stats.dailyNet), `${stats.reportDay} 北京时间`, stats.dailyNet >= 0 ? 'good' : 'bad'),
    metric('胜率', fmtPct(stats.winRate), `PF ${stats.pf === null ? 'NA' : fmt(stats.pf, 3)}`),
    metric('最大回撤', `${fmt(stats.maxDD, 4)}R`, `当前 ${fmt(stats.currentDD, 4)}R`, stats.maxDD >= 20 ? 'warn' : ''),
    metric('正收益市场', `${stats.positiveMarkets}/9`, '按已平仓交易统计'),
    metric('一致性检查', `${fmt((state.consistency?.mismatch_rate || 0) * 100, 2)}%`, `${state.consistency?.comparable_rows || 0} 条对比`)
  ].join('');

  table(document.getElementById('positionsTable'), open, [
    {key:'market', label:'市场'},
    {key:'position_status', label:'状态', format: value => badge(value === 'OPEN' ? '持仓中' : '空仓', value === 'OPEN' ? 'good' : '')},
    {key:'entry_time', label:'入场时间（北京）', format: value => escapeHtml(formatBeijing(value))},
    {key:'entry_price', label:'入场价', format: value => escapeHtml(fmt(value, 4))},
    {key:'stop_loss', label:'止损', format: value => escapeHtml(fmt(value, 4))},
    {key:'take_profit', label:'止盈', format: value => escapeHtml(fmt(value, 4))},
    {key:'bars_held', label:'持有K线'},
    {key:'unrealized_R', label:'浮动R', format: value => `<span class="${Number(value) >= 0 ? 'good' : 'bad'}">${escapeHtml(fmtR(value))}</span>`}
  ]);

  table(document.getElementById('signalsTable'), signals.slice(-20).reverse(), [
    {key:'signal_time', label:'时间（北京）', format: value => escapeHtml(formatBeijing(value))},
    {key:'market', label:'市场'},
    {key:'signal_valid', label:'有效', format: value => badge(isTrue(value) ? '有效' : '无效', isTrue(value) ? 'good' : '')},
    {key:'skip_reason', label:'跳过原因', format: value => escapeHtml(translateSkip(value))},
    {key:'adx', label:'ADX', format: value => escapeHtml(fmt(value, 2))},
    {key:'close', label:'收盘价', format: value => escapeHtml(fmt(value, 4))},
    {key:'swing_high_level', label:'BOS水平', format: value => escapeHtml(fmt(value, 4))}
  ]);

  table(document.getElementById('tradesTable'), stats.closedTrades.slice(-20).reverse(), [
    {key:'exit_time', label:'平仓时间（北京）', format: value => escapeHtml(formatBeijing(value))},
    {key:'market', label:'市场'},
    {key:'exit_reason', label:'退出', format: value => escapeHtml(translateExit(value))},
    {key:'net_R', label:'net_R', format: value => `<span class="${Number(value) >= 0 ? 'good' : 'bad'}">${escapeHtml(fmtR(value))}</span>`},
    {key:'mfe_R', label:'MFE', format: value => escapeHtml(fmt(value, 4))},
    {key:'mae_R', label:'MAE', format: value => escapeHtml(fmt(value, 4))},
    {key:'bars_held', label:'持有K线'}
  ]);

  table(document.getElementById('marketTable'), stats.byMarket, [
    {key:'market', label:'市场'},
    {key:'trades', label:'交易数'},
    {key:'net_R', label:'net_R', format: value => `<span class="${Number(value) >= 0 ? 'good' : 'bad'}">${escapeHtml(fmtR(value))}</span>`},
    {key:'avg_R', label:'avg_R', format: value => escapeHtml(value === null ? 'NA' : fmtR(value))},
    {key:'net_R', label:'状态', format: value => badge(Number(value) > 0 ? '正贡献' : (Number(value) < 0 ? '拖累' : '观察'), Number(value) > 0 ? 'good' : (Number(value) < 0 ? 'bad' : ''))}
  ]);

  table(document.getElementById('riskTable'), riskRows(stats), [
    {key:'risk_per_trade', label:'单笔风险'},
    {key:'estimated_return_pct', label:'预估收益'},
    {key:'current_drawdown_pct', label:'当前回撤'},
    {key:'historical_max_dd_pct_estimate', label:'历史最大回撤估计'},
    {key:'suggestion', label:'建议', format: value => badge(value, value === '观察可用' ? 'good' : (value === '禁止' ? 'bad' : 'warn'))}
  ]);

  document.getElementById('dailyReport').innerHTML = renderReport(state, stats);
}

document.getElementById('refreshBtn').addEventListener('click', load);
load().catch(err => {
  document.getElementById('statusPill').className = 'status-pill warn';
  document.getElementById('statusPill').textContent = '加载失败';
  document.getElementById('dailyReport').innerHTML = `<p class="note-line">加载失败：${escapeHtml(err.message || String(err))}</p>`;
});
setInterval(load, 60000);
