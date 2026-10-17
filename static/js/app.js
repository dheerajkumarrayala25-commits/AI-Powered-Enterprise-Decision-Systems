/**
 * AI-POWERED ENTERPRISE DECISION SYSTEM — CLIENT CONTROLLER
 * Full-stack single-page application logic and REST API bindings.
 */

// Global Chart Instances
let salesChart = null;
let categoryChart = null;
let churnDonut = null;
let inventoryBarChart = null;
let riskHistChart = null;

// Notification Toast Engine
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    if (type === 'danger') toast.style.borderLeftColor = 'var(--accent-rose)';
    if (type === 'warning') toast.style.borderLeftColor = 'var(--accent-amber)';
    toast.innerHTML = `<strong>${type.toUpperCase()}:</strong> ${message}`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ----------------- TAB ROUTING -----------------
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadOverviewData();
});

function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('data-target');
            
            // Update active states
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            link.parentElement.classList.add('active');
            
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add('active');
            
            // Update Header Title
            const titleText = link.querySelector('span').innerText;
            document.getElementById('current-page-title').innerText = titleText;
            
            // Lazy load corresponding data
            switch (targetId) {
                case 'overview-tab': loadOverviewData(); break;
                case 'sales-tab': loadSalesForecast(); break;
                case 'churn-tab': loadChurnAccounts(); break;
                case 'inventory-tab': loadInventoryData(); break;
                case 'risk-tab': loadRiskTransactions(); break;
                case 'governance-tab': loadAuditTrail(); break;
                case 'real-world-tab': loadRealWorldVerticals('fintech'); break;
                case 'benchmarks-tab': loadBenchmarks(); break;
                case 'database-tab': loadDatabaseStudio(); break;
            }
        });
    });
}

// =====================================================================
// 1. EXECUTIVE COMMAND CENTER
// =====================================================================
async function loadOverviewData() {
    try {
        const res = await fetch('/api/overview');
        const data = await res.json();
        
        // Render KPIs
        const kpis = data.kpis;
        document.getElementById('kpi-revenue').innerText = `₹${(kpis.projected_revenue_30d / 10000000).toFixed(2)} Cr`;
        document.getElementById('kpi-churn').innerText = `₹${(kpis.at_risk_churn_revenue / 100000).toFixed(1)} Lakhs`;
        document.getElementById('kpi-capex').innerText = `₹${(kpis.reorder_capex_required / 100000).toFixed(1)} Lakhs`;
        document.getElementById('kpi-reviews').innerText = `${kpis.mandatory_audit_reviews} Events`;
        
        // Render Recommendations Cards
        const recsContainer = document.getElementById('overview-recs-container');
        recsContainer.innerHTML = '';
        data.recommendations.forEach(r => {
            const cardClass = r.priority.toLowerCase() === 'critical' ? 'critical' : (r.priority.toLowerCase() === 'high' ? 'high' : 'success');
            const card = document.createElement('div');
            card.className = `rec-card ${cardClass}`;
            card.innerHTML = `
                <div class="rec-header">
                    <span class="rec-badge">${r.priority} • ${r.domain}</span>
                    <span style="font-weight: 700; color: var(--accent-emerald); font-size: 11px;">${r.impact}</span>
                </div>
                <div class="rec-title">${r.title}</div>
                <div class="rec-desc">${r.reason}</div>
                <div class="rec-footer">
                    <span><b>Governance:</b> ${r.governance}</span>
                    <button class="action-btn" style="padding: 4px 10px; font-size: 10px;" onclick="openReviewModal('${r.id}', '${r.title}')">Adjudicate</button>
                </div>
            `;
            recsContainer.appendChild(card);
        });
        
        // Render Churn Donut
        renderChurnDonut(data.churn_tiers);
        
    } catch (err) {
        console.error("Failed to load overview data:", err);
    }
}

function renderChurnDonut(tiers) {
    const ctx = document.getElementById('churnDonutChart').getContext('2d');
    if (churnDonut) churnDonut.destroy();
    
    churnDonut = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(tiers),
            datasets: [{
                data: Object.values(tiers),
                backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11 } } }
            },
            cutout: '70%'
        }
    });
}

// =====================================================================
// 2. SALES FORECASTING & REVENUE INTELLIGENCE
// =====================================================================
async function loadSalesForecast() {
    const horizon = document.getElementById('sales-horizon')?.value || 30;
    const mktBoost = document.getElementById('sales-mkt-boost')?.value || 0;
    const promoDays = document.getElementById('sales-promo-days')?.value || 4;
    
    document.getElementById('mkt-boost-val').innerText = `${mktBoost > 0 ? '+' : ''}${mktBoost}%`;
    document.getElementById('promo-days-val').innerText = `${promoDays} Days`;
    
    try {
        const res = await fetch(`/api/sales/forecast?horizon=${horizon}&mkt_boost=${mktBoost}&promo_days=${promoDays}`);
        const data = await res.json();
        
        document.getElementById('sales-total-units').innerText = Math.round(data.total_projected_units).toLocaleString();
        document.getElementById('sales-total-rev').innerText = `₹${(data.total_projected_revenue / 10000000).toFixed(2)} Cr`;
        document.getElementById('sales-mae').innerText = `${data.metrics.mae} units`;
        document.getElementById('sales-r2').innerText = data.metrics.r2.toFixed(3);
        
        // Plot Daily Forecast Area Chart
        renderSalesChart(data.daily);
        renderCategoryChart(data.categories);
        
    } catch (err) {
        console.error("Failed to load sales forecast:", err);
    }
}

function renderSalesChart(daily) {
    const ctx = document.getElementById('salesForecastChart').getContext('2d');
    if (salesChart) salesChart.destroy();
    
    const dates = daily.map(d => d.date);
    const expected = daily.map(d => d.forecast_units);
    const p90 = daily.map(d => d.upper_bound_p90);
    const p10 = daily.map(d => d.lower_bound_p10);
    
    salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'P90 Upper Bound',
                    data: p90,
                    borderColor: 'transparent',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    fill: '+1',
                    pointRadius: 0
                },
                {
                    label: 'P10 Lower Bound',
                    data: p10,
                    borderColor: 'transparent',
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: 'Expected AI Demand Forecast',
                    data: expected,
                    borderColor: '#38bdf8',
                    borderWidth: 2.5,
                    backgroundColor: 'rgba(56, 189, 248, 0.15)',
                    fill: false,
                    tension: 0.3,
                    pointBackgroundColor: '#38bdf8',
                    pointRadius: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b' } },
                y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b' } }
            },
            plugins: {
                legend: { labels: { color: '#94a3b8' } }
            }
        }
    });
}

function renderCategoryChart(cats) {
    const ctx = document.getElementById('salesCategoryChart').getContext('2d');
    if (categoryChart) categoryChart.destroy();
    
    categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: cats.map(c => c.product_category),
            datasets: [{
                label: 'Projected Revenue (₹)',
                data: cats.map(c => c.projected_revenue),
                backgroundColor: ['#38bdf8', '#818cf8', '#34d399', '#f59e0b'],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b' } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

async function saveCurrentScenario() {
    const mkt = document.getElementById('sales-mkt-boost').value;
    const promo = document.getElementById('sales-promo-days').value;
    const horizon = document.getElementById('sales-horizon').value;
    
    const payload = {
        name: `Strategy Run (Mkt: ${mkt}%, Promo: ${promo}D, ${horizon}D Horizon)`,
        params: { mkt_boost: mkt, promo_days: promo, horizon: horizon },
        results: { timestamp: new Date().toISOString() }
    };
    
    const res = await fetch('/api/sales/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    showToast(data.message);
}

// =====================================================================
// 3. CUSTOMER CHURN & RETENTION SCORING
// =====================================================================
async function loadChurnAccounts() {
    try {
        const res = await fetch('/api/churn/accounts');
        const data = await res.json();
        
        document.getElementById('churn-precision').innerText = `${(data.metrics.precision * 100).toFixed(1)}%`;
        document.getElementById('churn-recall').innerText = `${(data.metrics.recall * 100).toFixed(1)}%`;
        document.getElementById('churn-f1').innerText = data.metrics.f1.toFixed(3);
        document.getElementById('churn-at-risk-val').innerText = `₹${(data.total_at_risk_revenue / 100000).toFixed(1)} Lakhs`;
        
        const tbody = document.getElementById('churn-table-body');
        tbody.innerHTML = '';
        
        data.accounts.slice(0, 15).forEach(acc => {
            const isCrit = acc.risk_tier === 'Critical Risk';
            const chipClass = isCrit ? 'chip-danger' : (acc.risk_tier === 'Moderate Risk' ? 'chip-warning' : 'chip-success');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${acc.customer_id}</b></td>
                <td>${acc.company_name}</td>
                <td><span class="chip chip-info">${acc.segment}</span></td>
                <td>${acc.contract_type}</td>
                <td>₹${acc.monthly_spend.toLocaleString()}</td>
                <td>${acc.support_tickets_30d}</td>
                <td><span class="chip ${chipClass}">${(acc.churn_probability * 100).toFixed(1)}%</span></td>
                <td><small style="color: var(--accent-blue);">${acc.prescriptive_action}</small></td>
                <td><button class="action-btn" style="padding: 4px 8px; font-size: 10px;" onclick="openReviewModal('${acc.customer_id}', 'Customer Retention Outreach: ${acc.company_name}')">Action</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed to load churn data:", err);
    }
}

// =====================================================================
// 4. INVENTORY OPTIMIZATION & SUPPLY CHAIN
// =====================================================================
async function loadInventoryData() {
    try {
        const res = await fetch('/api/inventory/optimization?service_level=95');
        const data = await res.json();
        
        document.getElementById('inv-skus-count').innerText = data.skus.length;
        document.getElementById('inv-triggered-count').innerText = `${data.reorder_triggered_count} SKUs`;
        document.getElementById('inv-stockout-risk').innerText = `${data.stockout_risk_count} SKUs`;
        document.getElementById('inv-capex-required').innerText = `₹${(data.total_reorder_budget / 100000).toFixed(1)} Lakhs`;
        
        const tbody = document.getElementById('inventory-table-body');
        tbody.innerHTML = '';
        
        data.skus.forEach(item => {
            const isAlert = item.stock_status.includes('CRITICAL') || item.stock_status.includes('URGENT');
            const chipClass = isAlert ? 'chip-danger' : (item.recommended_order_units > 0 ? 'chip-warning' : 'chip-success');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${item.sku}</b></td>
                <td>${item.product_name}</td>
                <td>${item.stock_on_hand}</td>
                <td>${item.daily_sales_avg.toFixed(1)}</td>
                <td>${item.dynamic_safety_stock}</td>
                <td>${item.dynamic_reorder_point}</td>
                <td>${item.eoq_units}</td>
                <td><b>${item.recommended_order_units}</b></td>
                <td>₹${item.reorder_budget_required.toLocaleString()}</td>
                <td><span class="chip ${chipClass}">${item.stock_status}</span></td>
                <td><button class="action-btn" style="padding: 4px 8px; font-size: 10px;" onclick="openReviewModal('${item.sku}', 'PO Authorization for ${item.product_name}')">Approve PO</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed to load inventory data:", err);
    }
}

// =====================================================================
// 5. TRANSACTION RISK & FRAUD FLAGGING
// =====================================================================
async function loadRiskTransactions() {
    try {
        const res = await fetch('/api/risk/transactions?threshold=10000&risk_cutoff=0.6');
        const data = await res.json();
        
        document.getElementById('risk-precision').innerText = `${(data.metrics.precision * 100).toFixed(1)}%`;
        document.getElementById('risk-recall').innerText = `${(data.metrics.recall * 100).toFixed(1)}%`;
        document.getElementById('risk-f1').innerText = data.metrics.f1.toFixed(3);
        document.getElementById('risk-queue-count').innerText = `${data.mandatory_review_count} Txns`;
        
        const tbody = document.getElementById('risk-table-body');
        tbody.innerHTML = '';
        
        data.transactions.slice(0, 15).forEach(tx => {
            const isReview = tx.decision_status === 'MANDATORY HUMAN REVIEW';
            const chipClass = isReview ? 'chip-danger' : 'chip-success';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${tx.transaction_id}</b></td>
                <td>₹${tx.amount.toLocaleString()}</td>
                <td>${tx.hour_of_day}:00</td>
                <td>${tx.velocity_24h}</td>
                <td>${(tx.ml_risk_probability * 100).toFixed(1)}%</td>
                <td><b>${tx.hybrid_risk_score}</b>/100</td>
                <td><span class="chip ${chipClass}">${tx.decision_status}</span></td>
                <td><small style="color: #94a3b8;">${tx.explainability_rationale}</small></td>
                <td><button class="action-btn" style="padding: 4px 8px; font-size: 10px;" onclick="openReviewModal('${tx.transaction_id}', 'Adjudicate Wire: ₹${tx.amount.toLocaleString()}')">Review</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed to load risk transactions:", err);
    }
}

// =====================================================================
// 6. HUMAN-IN-THE-LOOP GOVERNANCE DESK
// =====================================================================
async function loadAuditTrail() {
    try {
        const res = await fetch('/api/governance/audit-trail');
        const data = await res.json();
        
        const tbody = document.getElementById('audit-table-body');
        tbody.innerHTML = '';
        
        data.audit_log.forEach(entry => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${entry.id}</td>
                <td><span class="chip chip-info">${entry.module}</span></td>
                <td><b>${entry.reference_id}</b></td>
                <td><span class="chip chip-success">${entry.decision_action}</span></td>
                <td>${entry.reviewer_name}</td>
                <td>${entry.rationale}</td>
                <td><small style="color: #64748b;">${entry.review_timestamp}</small></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed to load audit trail:", err);
    }
}

// Review Modal Controls
function openReviewModal(refId, title) {
    document.getElementById('modal-ref-id').innerText = refId;
    document.getElementById('modal-ref-title').innerText = title;
    document.getElementById('review-ref-input').value = refId;
    document.getElementById('review-notes-input').value = '';
    document.getElementById('review-modal').classList.add('active');
}

function closeReviewModal() {
    document.getElementById('review-modal').classList.remove('active');
}

async function submitReviewDecision(action) {
    const refId = document.getElementById('review-ref-input').value;
    const reviewer = document.getElementById('review-name-input').value;
    const rationale = document.getElementById('review-notes-input').value;
    
    if (!rationale.trim()) {
        alert("Compliance policy strictly requires a written audit rationale.");
        return;
    }
    
    try {
        const res = await fetch('/api/governance/adjudicate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                module: "Transaction Risk & Fraud",
                ref_id: refId,
                action: action,
                reviewer: reviewer,
                rationale: rationale
            })
        });
        const data = await res.json();
        closeReviewModal();
        showToast(data.message, 'success');
        loadAuditTrail();
        loadRiskTransactions();
    } catch (err) {
        showToast("Failed to commit review decision", 'danger');
    }
}

// =====================================================================
// 7. MODEL EVALUATION & LATENCY BENCHMARKS
// =====================================================================
async function loadBenchmarks() {
    try {
        const res = await fetch('/api/benchmarks');
        const data = await res.json();
        
        const tbody = document.getElementById('benchmarks-table-body');
        tbody.innerHTML = '';
        
        data.comparison_table.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${row['Architecture Layer']}</b></td>
                <td>${row['Accuracy']}</td>
                <td>${row['Precision']}</td>
                <td>${row['Recall']}</td>
                <td><b style="color: var(--accent-blue);">${row['F1-Score']}</b></td>
                <td><span class="chip chip-info">${row['Avg Decision Latency']}</span></td>
                <td><small>${row['Human Oversight']}</small></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed to load benchmarks:", err);
    }
}

// =====================================================================
// 8. RELATIONAL DATABASE STUDIO (15 Tables + SQL Console)
// =====================================================================
async function loadDatabaseStudio() {
    try {
        const res = await fetch('/api/database/tables');
        const data = await res.json();
        
        const selector = document.getElementById('db-table-selector');
        selector.innerHTML = '';
        
        data.tables.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.table_name;
            opt.innerText = `${t.table_name} (${t.record_count} records)`;
            selector.appendChild(opt);
        });
        
        document.getElementById('db-total-tables').innerText = data.tables.length;
        document.getElementById('db-total-records').innerText = data.total_records.toLocaleString();
        
        loadSelectedTableData(data.tables[0].table_name);
    } catch (err) {
        console.error("Failed to load DB studio:", err);
    }
}

async function loadSelectedTableData(tableName) {
    try {
        const res = await fetch(`/api/database/table/${tableName}`);
        const data = await res.json();
        
        const thead = document.getElementById('db-browser-head');
        thead.innerHTML = '';
        data.columns.forEach(c => {
            const th = document.createElement('th');
            th.innerText = c;
            thead.appendChild(th);
        });
        
        const tbody = document.getElementById('db-browser-body');
        tbody.innerHTML = '';
        data.data.slice(0, 50).forEach(row => {
            const tr = document.createElement('tr');
            data.columns.forEach(c => {
                const td = document.createElement('td');
                td.innerText = row[c] !== null ? row[c] : '';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed to load table content:", err);
    }
}

async function executeCustomQuery() {
    const sql = document.getElementById('sql-query-input').value;
    try {
        const res = await fetch('/api/database/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: sql })
        });
        const data = await res.json();
        if (!data.success) {
            alert(`Query Error: ${data.error}`);
            return;
        }
        
        document.getElementById('query-execution-stat').innerText = `Returned ${data.row_count} rows in ${data.execution_time_ms} ms`;
        
        const thead = document.getElementById('query-result-head');
        thead.innerHTML = '';
        data.columns.forEach(c => {
            const th = document.createElement('th');
            th.innerText = c;
            thead.appendChild(th);
        });
        
        const tbody = document.getElementById('query-result-body');
        tbody.innerHTML = '';
        data.data.forEach(row => {
            const tr = document.createElement('tr');
            data.columns.forEach(c => {
                const td = document.createElement('td');
                td.innerText = row[c];
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        showToast("SQL query executed successfully!");
    } catch (err) {
        console.error("Query failed:", err);
    }
}

// =====================================================================
// 9. REAL-WORLD GLOBAL ENTERPRISE INDUSTRY VERTICALS
// =====================================================================
let currentIndustryKey = 'fintech';
let cachedCatalog = [];

async function loadRealWorldVerticals(industryKey = 'fintech') {
    currentIndustryKey = industryKey;
    try {
        if (!cachedCatalog.length) {
            const catRes = await fetch('/api/real-world/catalog');
            const catData = await catRes.json();
            cachedCatalog = catData.catalog;
        }
        
        // Find selected item
        const indItem = cachedCatalog.find(c => c.industry_key === industryKey) || cachedCatalog[0];
        
        // Update dossier card
        document.getElementById('dossier-name').innerText = indItem.industry_name;
        document.getElementById('dossier-desc').innerText = indItem.description;
        document.getElementById('dossier-archetype').innerText = indItem.company_archetype;
        document.getElementById('dossier-usecase').innerText = indItem.key_use_case;
        document.getElementById('dossier-model').innerText = indItem.primary_model;
        document.getElementById('dossier-reg').innerText = indItem.regulatory_framework;
        document.getElementById('dossier-roi').innerText = indItem.quantified_roi;
        document.getElementById('dossier-badge').innerText = indItem.industry_name.toUpperCase();
        
        // Update stream title & subtitle
        const titles = {
            fintech: { t: "Real-Time Commercial Loan Applications & Underwriting Queue", s: "Credit underwriting models evaluated against score, DTI, revenue, and Basel III compliance gates." },
            retail: { t: "Regional Supply Chain SKU Replenishment & Dynamic Margin Optimizations", s: "Demand forecasts across regional fulfillment hubs (Mumbai, Delhi, Bangalore) to prevent stockouts." },
            saas: { t: "Enterprise B2B Client Health & Annual Contract Churn Risk Desk", s: "Monitors ARR, seat utilization, and ticket velocity to prescribe customer retention playbooks." },
            healthcare: { t: "Clinical Operations, ICU Bed Capacity & Emergency Triage Decisions", s: "Predicts admission velocity and clinical acuity to optimize medical staff and critical care capacity." },
            manufacturing: { t: "IoT Sensor Telemetry & Predictive Equipment Downtime Elimination", s: "Real-time vibration, thermal, and pressure signals to preempt assembly line failures." }
        };
        const curMeta = titles[industryKey] || titles.fintech;
        document.getElementById('industry-stream-title').innerText = curMeta.t;
        document.getElementById('industry-stream-subtitle').innerText = curMeta.s;
        
        // Fetch decision data
        const decRes = await fetch(`/api/real-world/decisions/${industryKey}`);
        const decData = await decRes.json();
        
        document.getElementById('industry-records-count').innerText = `${decData.total_records} Active Records`;
        renderRealWorldTable(industryKey, decData.data);
        
    } catch (err) {
        console.error("Failed to load real-world verticals:", err);
    }
}

function switchRealWorldIndustry(key) {
    document.querySelectorAll('.industry-btn').forEach(btn => {
        if (btn.getAttribute('data-ind') === key) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    loadRealWorldVerticals(key);
}

function renderRealWorldTable(key, data) {
    const thead = document.getElementById('real-world-table-head');
    const tbody = document.getElementById('real-world-table-body');
    thead.innerHTML = '';
    tbody.innerHTML = '';
    
    if (key === 'fintech') {
        thead.innerHTML = `
            <tr>
                <th>App ID</th>
                <th>Commercial Entity</th>
                <th>Loan Amount</th>
                <th>Credit Score</th>
                <th>DTI</th>
                <th>Annual Revenue</th>
                <th>Approval Prob</th>
                <th>Risk Tier</th>
                <th>Action</th>
                <th>Decision Gate</th>
            </tr>
        `;
        data.slice(0, 15).forEach(row => {
            const isApproved = row.decision_action.includes('Approved');
            const isReview = row.decision_action.includes('Mandatory');
            const chipClass = isApproved ? 'chip-success' : (isReview ? 'chip-warning' : 'chip-danger');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${row.application_id}</b></td>
                <td>${row.applicant_name}</td>
                <td>₹${row.loan_amount.toLocaleString()}</td>
                <td><b>${row.credit_score}</b></td>
                <td>${(row.debt_to_income * 100).toFixed(0)}%</td>
                <td>₹${row.annual_income.toLocaleString()}</td>
                <td>${(row.ml_approval_probability * 100).toFixed(1)}%</td>
                <td><span class="chip ${chipClass}">${row.risk_tier}</span></td>
                <td><small style="color: #94a3b8;">${row.decision_action}</small></td>
                <td><button class="action-btn" style="padding: 4px 8px; font-size: 10px;" onclick="openReviewModal('${row.application_id}', 'Loan Underwriting Sign-off: ₹${row.loan_amount.toLocaleString()}')">Sign-off</button></td>
            `;
            tbody.appendChild(tr);
        });
    } else if (key === 'retail') {
        thead.innerHTML = `
            <tr>
                <th>SKU</th>
                <th>Product Name</th>
                <th>Warehouse Hub</th>
                <th>Stock</th>
                <th>Daily Demand</th>
                <th>Dynamic Price</th>
                <th>Margin</th>
                <th>Stockout Risk</th>
                <th>Recommendation</th>
                <th>Action</th>
            </tr>
        `;
        data.forEach(row => {
            const isCrit = row.stockout_risk_score > 0.75;
            const chipClass = isCrit ? 'chip-danger' : (row.suggested_reorder_qty > 0 ? 'chip-warning' : 'chip-success');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${row.sku}</b></td>
                <td>${row.product_name}</td>
                <td><span class="chip chip-info">${row.regional_warehouse}</span></td>
                <td>${row.current_inventory}</td>
                <td>${row.daily_demand_forecast}</td>
                <td>₹${row.dynamic_price.toLocaleString()}</td>
                <td>${row.margin_pct}%</td>
                <td><span class="chip ${chipClass}">${(row.stockout_risk_score * 100).toFixed(0)}%</span></td>
                <td><small style="color: #94a3b8;">${row.action_recommendation}</small></td>
                <td><button class="action-btn" style="padding: 4px 8px; font-size: 10px;" onclick="openReviewModal('${row.sku}', 'Authorize Transfer / PO: ${row.product_name}')">Authorize</button></td>
            `;
            tbody.appendChild(tr);
        });
    } else if (key === 'saas') {
        thead.innerHTML = `
            <tr>
                <th>Account ID</th>
                <th>Enterprise Client</th>
                <th>Contract ARR</th>
                <th>Tier</th>
                <th>Seat Usage</th>
                <th>NPS</th>
                <th>Tickets</th>
                <th>Churn Risk</th>
                <th>Prescriptive Action</th>
                <th>Action</th>
            </tr>
        `;
        data.slice(0, 15).forEach(row => {
            const isCrit = row.churn_risk_score > 0.60;
            const chipClass = isCrit ? 'chip-danger' : (row.churn_risk_score > 0.35 ? 'chip-warning' : 'chip-success');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${row.account_id}</b></td>
                <td>${row.enterprise_client}</td>
                <td>₹${row.arr_revenue.toLocaleString()}</td>
                <td>${row.contract_tier}</td>
                <td>${(row.seat_utilization_pct * 100).toFixed(0)}%</td>
                <td><b>${row.nps_score}</b>/10</td>
                <td>${row.ticket_velocity}</td>
                <td><span class="chip ${chipClass}">${(row.churn_risk_score * 100).toFixed(1)}%</span></td>
                <td><small style="color: var(--accent-blue);">${row.prescriptive_action}</small></td>
                <td><button class="action-btn" style="padding: 4px 8px; font-size: 10px;" onclick="openReviewModal('${row.account_id}', 'Customer Intervention: ${row.enterprise_client}')">Escalate</button></td>
            `;
            tbody.appendChild(tr);
        });
    } else if (key === 'healthcare') {
        thead.innerHTML = `
            <tr>
                <th>Unit ID</th>
                <th>Department</th>
                <th>Occupancy</th>
                <th>Predicted Admissions (24h)</th>
                <th>Available ICU Beds</th>
                <th>Nurse-to-Patient</th>
                <th>Triage Urgency</th>
                <th>Prescribed Resource Action</th>
                <th>Sign-off Status</th>
            </tr>
        `;
        data.forEach(row => {
            const isUrgent = row.triage_urgency_index > 0.75;
            const chipClass = isUrgent ? 'chip-danger' : 'chip-success';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${row.unit_id}</b></td>
                <td><b>${row.hospital_department}</b></td>
                <td>${row.current_occupancy_pct}%</td>
                <td>+${row.predicted_admissions_24h} patients</td>
                <td><span class="chip ${row.available_icu_beds <= 2 ? 'chip-danger' : 'chip-info'}">${row.available_icu_beds} Beds</span></td>
                <td>${row.nurse_to_patient_ratio}</td>
                <td><span class="chip ${chipClass}">${(row.triage_urgency_index * 100).toFixed(0)}%</span></td>
                <td><small style="color: #94a3b8;">${row.resource_allocation_action}</small></td>
                <td><button class="action-btn" style="padding: 4px 8px; font-size: 10px;" onclick="openReviewModal('${row.unit_id}', 'Clinical Resource Sign-off: ${row.hospital_department}')">Clinical Auth</button></td>
            `;
            tbody.appendChild(tr);
        });
    } else if (key === 'manufacturing') {
        thead.innerHTML = `
            <tr>
                <th>Asset ID</th>
                <th>Machine Asset</th>
                <th>Line</th>
                <th>Vibration</th>
                <th>Temp (°C)</th>
                <th>Runtime</th>
                <th>Failure Risk</th>
                <th>Downtime Window</th>
                <th>Cost Avoidance</th>
                <th>Action</th>
            </tr>
        `;
        data.forEach(row => {
            const isCrit = row.failure_probability > 0.70;
            const chipClass = isCrit ? 'chip-danger' : (row.failure_probability > 0.30 ? 'chip-warning' : 'chip-success');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${row.asset_id}</b></td>
                <td>${row.machine_name}</td>
                <td><span class="chip chip-info">${row.assembly_line}</span></td>
                <td>${row.vibration_mm_s} mm/s</td>
                <td>${row.operating_temp_c}°C</td>
                <td>${row.runtime_hours} hrs</td>
                <td><span class="chip ${chipClass}">${(row.failure_probability * 100).toFixed(0)}%</span></td>
                <td><b>${row.maintenance_window}</b></td>
                <td style="color: var(--accent-emerald); font-weight: 700;">₹${row.cost_avoidance_value.toLocaleString()}</td>
                <td><button class="action-btn" style="padding: 4px 8px; font-size: 10px;" onclick="openReviewModal('${row.asset_id}', 'Maintenance Work Order: ${row.machine_name}')">Authorize</button></td>
            `;
            tbody.appendChild(tr);
        });
    }
}

