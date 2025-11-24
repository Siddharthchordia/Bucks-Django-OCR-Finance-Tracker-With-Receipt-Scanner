
// ---------- helpers ----------
function formatNumber(n) {
    // Use user's locale for thousands separators
    try { return Number(n).toLocaleString(); } catch (e) { return n; }
}

function formatCurrency(n) {
    // No currency symbol assumed. If you want a symbol, prefix here.
    return formatNumber(n);
}

// create a purple gradient helper for fills
function createHorizontalGradient(ctx, area, stops) {
    const g = ctx.createLinearGradient(0, 0, area.width, 0);
    for (const s of stops) g.addColorStop(s.pos, s.color);
    return g;
}

// ---------- State management ----------
let weekOffset = 0;
let monthOffset = 0;

// ---------- Weekly (line + area) ----------
let weeklyChart = null;

function initWeeklyChart() {
    const canvas = document.getElementById('weeklyChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    weeklyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Income',
                    data: [],
                    borderColor: '#7CFFB2',
                    backgroundColor: function (context) {
                        const chart = context.chart;
                        const area = chart.chartArea;
                        if (!area) return 'rgba(124,255,178,0.12)';
                        return createHorizontalGradient(context.chart.ctx, area, [
                            { pos: 0, color: 'rgba(124,255,178,0.18)' },
                            { pos: 1, color: 'rgba(124,255,178,0.02)' }
                        ]);
                    },
                    borderWidth: 3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    tension: 0.36,
                    fill: true
                },
                {
                    label: 'Expense',
                    data: [],
                    borderColor: '#9D4EDD',
                    backgroundColor: function (context) {
                        const chart = context.chart;
                        const area = chart.chartArea;
                        if (!area) return 'rgba(157,78,221,0.12)';
                        return createHorizontalGradient(context.chart.ctx, area, [
                            { pos: 0, color: 'rgba(157,78,221,0.18)' },
                            { pos: 1, color: 'rgba(157,78,221,0.02)' }
                        ]);
                    },
                    borderWidth: 3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    tension: 0.36,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    labels: { color: '#fff', boxWidth: 14, boxHeight: 8 }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const v = context.parsed.y;
                            return context.dataset.label + ': ' + formatCurrency(v);
                        }
                    },
                    backgroundColor: 'rgba(20,20,30,0.95)',
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: 'rgba(255,255,255,0.85)' },
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: {
                        color: 'rgba(255,255,255,0.75)',
                        callback: function (value) { return formatNumber(value); }
                    }
                }
            },
            animation: { duration: 450 }
        }
    });
}

// ---------- Category doughnut ----------
let categoryChart = null;

// Helper function to get legend configuration based on screen width
function getCategoryLegendConfig() {
    const isMobile = window.innerWidth <= 768;
    return {
        position: isMobile ? 'bottom' : 'right',
        labels: {
            color: '#fff',
            boxWidth: isMobile ? 16 : 20,
            padding: isMobile ? 8 : 10,
            font: {
                size: isMobile ? 12 : 13,
                weight: '500'
            }
        }
    };
}

function initCategoryChart() {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                label: 'Expenses by Category',
                data: [],
                // Vibrant purple-centric palette; Chart.js will cycle through
                backgroundColor: [
                    'rgba(148,50,255,0.95)',
                    'rgba(95,46,206,0.95)',
                    'rgba(204,52,140,0.95)',
                    'rgba(170,80,220,0.95)',
                    'rgba(255,120,160,0.95)',
                    'rgba(90,200,250,0.95)',
                    'rgba(120,90,220,0.95)',
                    'rgba(160,75,230,0.95)',
                    'rgba(255,180,100,0.95)',
                    'rgba(100,220,180,0.95)'
                ],
                hoverOffset: 10,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: {
                legend: getCategoryLegendConfig(),
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const v = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((v / total) * 100).toFixed(1);
                            return context.label + ': ' + formatCurrency(v) + ' (' + percentage + '%)';
                        }
                    },
                    backgroundColor: 'rgba(20,20,30,0.95)',
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            animation: { duration: 420 }
        }
    });
}

// Update category chart legend position on resize
function updateCategoryChartLegendPosition() {
    if (categoryChart) {
        const newConfig = getCategoryLegendConfig();
        const currentPosition = categoryChart.options.plugins.legend.position;

        // Only update if position changed (to avoid unnecessary re-renders)
        if (currentPosition !== newConfig.position) {
            categoryChart.options.plugins.legend = newConfig;
            categoryChart.update();
        }
    }
}

// ---------- Fetch & update ----------
async function fetchWeeklyAndUpdate() {
    if (!window.CHART_WEEKLY_URL) { console.warn('CHART_WEEKLY_URL not set'); return; }

    const noDataDiv = document.getElementById('weeklyNoData');
    const canvas = document.getElementById('weeklyChart');

    try {
        const res = await fetch(CHART_WEEKLY_URL + `?week_offset=${weekOffset}`, { credentials: 'same-origin' });
        if (!res.ok) { console.error('weekly fetch failed', res.status); return; }
        const json = await res.json();

        // convert ISO date labels to readable labels: 'Mon 21'
        const labels = json.labels.map(d => {
            const dt = new Date(d);
            return dt.toLocaleDateString(undefined, { weekday: 'short', day: '2-digit', month: 'short' });
        });

        // ensure numbers are numbers
        const incomeData = (json.datasets[0] && json.datasets[0].data) ? json.datasets[0].data.map(Number) : [];
        const expenseData = (json.datasets[1] && json.datasets[1].data) ? json.datasets[1].data.map(Number) : [];

        // Check if there's any data
        const hasData = incomeData.some(v => v > 0) || expenseData.some(v => v > 0);

        if (!hasData) {
            // Show "No Transactions" message
            if (canvas) canvas.style.display = 'none';
            if (noDataDiv) noDataDiv.style.display = 'block';
        } else {
            // Show chart
            if (canvas) canvas.style.display = 'block';
            if (noDataDiv) noDataDiv.style.display = 'none';

            if (weeklyChart) {
                weeklyChart.data.labels = labels;
                weeklyChart.data.datasets[0].data = incomeData;
                weeklyChart.data.datasets[1].data = expenseData;
                weeklyChart.update();
            }
        }

        // Update week label
        updateWeekLabel();
    } catch (err) {
        console.error('fetchWeeklyAndUpdate error', err);
    }
}

async function fetchCategoriesAndUpdate() {
    if (!window.CHART_CATEGORIES_URL) { console.warn('CHART_CATEGORIES_URL not set'); return; }
    try {
        const res = await fetch(CHART_CATEGORIES_URL, { credentials: 'same-origin' });
        if (!res.ok) { console.error('categories fetch failed', res.status); return; }
        const json = await res.json();

        const labels = json.labels || [];
        const data = (json.datasets && json.datasets[0] && json.datasets[0].data) ? json.datasets[0].data.map(Number) : [];

        if (categoryChart) {
            categoryChart.data.labels = labels;
            categoryChart.data.datasets[0].data = data;

            // if categories exceed palette, expand by repeating palette colors
            const palette = categoryChart.data.datasets[0].backgroundColor;
            while (palette.length < labels.length) {
                palette.push(...palette.slice(0, Math.min(8, labels.length - palette.length)));
            }

            categoryChart.update();
        }
    } catch (err) {
        console.error('fetchCategoriesAndUpdate error', err);
    }
}

// ---------- Monthly (doughnut) ----------
let monthlyChart = null;
function initMonthlyChart() {
    const canvas = document.getElementById('monthlyChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    monthlyChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                label: 'Monthly Overview',
                data: [],
                backgroundColor: [
                    'rgba(157, 78, 221, 0.95)', // Expense (Purple - matches weekly)
                    'rgba(124, 255, 178, 0.95)'  // Savings (Green - matches weekly)
                ],
                hoverOffset: 10,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            rotation: -90,
            circumference: 180,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#fff', boxWidth: 14, padding: 12 }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const v = context.parsed;
                            return context.label + ': ' + formatCurrency(v);
                        }
                    },
                    backgroundColor: 'rgba(20,20,30,0.95)',
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            animation: { duration: 420 }
        }
    });
}

async function fetchMonthlyAndUpdate() {
    if (!window.CHART_MONTHLY_URL) { console.warn('CHART_MONTHLY_URL not set'); return; }
    try {
        const res = await fetch(CHART_MONTHLY_URL + `?month_offset=${monthOffset}`, { credentials: 'same-origin' });
        if (!res.ok) { console.error('monthly fetch failed', res.status); return; }
        const json = await res.json();

        const labels = json.labels || [];
        const data = (json.datasets && json.datasets[0] && json.datasets[0].data) ? json.datasets[0].data.map(Number) : [];

        if (monthlyChart) {
            monthlyChart.data.labels = labels;
            monthlyChart.data.datasets[0].data = data;
            monthlyChart.update();
        }

        // Update month label
        updateMonthLabel();
    } catch (err) {
        console.error('fetchMonthlyAndUpdate error', err);
    }
}

// ---------- Navigation ----------
function updateWeekLabel() {
    const label = document.getElementById('weekLabel');
    if (!label) return;

    const today = new Date();
    const targetDate = new Date(today);
    targetDate.setDate(today.getDate() + (weekOffset * 7));

    if (weekOffset === 0) {
        label.textContent = 'This Week';
    } else if (weekOffset === -1) {
        label.textContent = 'Last Week';
    } else {
        const startOfWeek = new Date(targetDate);
        startOfWeek.setDate(targetDate.getDate() - 6);
        label.textContent = `Week of ${startOfWeek.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
    }
}

function updateMonthLabel() {
    const label = document.getElementById('monthLabel');
    if (!label) return;

    const today = new Date();
    const targetDate = new Date(today.getFullYear(), today.getMonth() + monthOffset, 1);

    if (monthOffset === 0) {
        label.textContent = 'This Month';
    } else if (monthOffset === -1) {
        label.textContent = 'Last Month';
    } else {
        label.textContent = targetDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    }
}

function navigateWeek(direction) {
    weekOffset += direction;
    fetchWeeklyAndUpdate();
}

function navigateMonth(direction) {
    monthOffset += direction;
    fetchMonthlyAndUpdate();
}

// ---------- Kickoff ----------
document.addEventListener('DOMContentLoaded', function () {
    initWeeklyChart();
    initCategoryChart();
    initMonthlyChart();

    // initial load
    fetchWeeklyAndUpdate();
    fetchCategoriesAndUpdate();
    fetchMonthlyAndUpdate();

    // Setup navigation buttons
    const weekPrev = document.getElementById('weekPrev');
    const weekNext = document.getElementById('weekNext');
    const monthPrev = document.getElementById('monthPrev');
    const monthNext = document.getElementById('monthNext');

    if (weekPrev) weekPrev.addEventListener('click', () => navigateWeek(-1));
    if (weekNext) weekNext.addEventListener('click', () => navigateWeek(1));
    if (monthPrev) monthPrev.addEventListener('click', () => navigateMonth(-1));
    if (monthNext) monthNext.addEventListener('click', () => navigateMonth(1));

    // Add resize listener for responsive legend positioning
    let resizeTimeout;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function () {
            updateCategoryChartLegendPosition();
        }, 250); // Debounce resize events
    });
});
