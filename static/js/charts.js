/**
 * static/js/charts.js
 * Pembungkus tipis di atas Chart.js supaya semua grafik di dashboard
 * memakai palet warna, garis membulat, dan grid minimal yang sama —
 * jadi template halaman cukup panggil fungsi-fungsi ini tanpa mengulang
 * konfigurasi Chart.js setiap kali.
 *
 * Palet resmi SELAMET — tiap warna punya peran tetap:
 *   green (Sage Green)   → data umum / kesehatan / progress
 *   honey (Honey Gold)   → highlight / produksi madu
 *   blue (Sky Blue)      → suhu, kelembapan, cuaca
 *   coral (Warm Orange)  → stres panas / aktivitas tinggi
 *   red (Muted Red)      → HANYA critical / danger
 */

const SELAMET_COLORS = {
  honey: "#22D3AA",    // (direpurpose) Teal — CTA / highlight, BUKAN emas
  amber: "#22D3AA",
  green: "#16866D",    // Primary Green — identitas, koloni, kesehatan
  blue: "#2E9FE0",     // Environmental Blue — suhu, kelembapan, cuaca
  cyan: "#67C9F2",     // Sky Blue muda — alias
  coral: "#F28C38",    // Warning Orange — stres panas
  red: "#E5544D",      // Critical Red — kondisi kritis
  forest: "#0F5B4D",   // Deep Forest Green — identitas utama
  sage: "#34D399",     // Healthy Green — swarming, sehat
  gradBlue: "#3B82F6", // Stop gradient identitas (biru)
  gradGreen: "#22D3AA",// Stop gradient identitas (hijau)
  grid: "rgba(23, 34, 46, 0.06)",
  text: "#5A6B7C",
};

/** Buat gradient linear biru→hijau untuk stroke garis grafik utama —
 *  dipakai supaya grafik penting terasa jadi "identitas" halaman. */
function selametBrandGradient(ctx, height = 200) {
  const g = ctx.createLinearGradient(0, 0, 0, height);
  g.addColorStop(0, SELAMET_COLORS.gradBlue);
  g.addColorStop(1, SELAMET_COLORS.gradGreen);
  return g;
}


Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 11.5;
Chart.defaults.color = SELAMET_COLORS.text;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.boxWidth = 7;
Chart.defaults.plugins.legend.labels.boxHeight = 7;

/** Grafik garis standar (dipakai untuk tren 24 jam, prediksi, riwayat, dll). */
function selametLineChart(ctx, labels, datasets, opts = {}) {
  return new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: datasets.map((d) => ({
        tension: 0.4,
        borderWidth: 3,
        pointRadius: 3,
        pointHoverRadius: 6,
        pointBackgroundColor: d.borderColor || SELAMET_COLORS.green,
        pointBorderColor: "#fff",
        pointBorderWidth: 1.5,
        fill: d.fill !== undefined ? d.fill : true,
        ...d,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: datasets.length > 1, position: "top", align: "end" },
        tooltip: { backgroundColor: "#0B2A3D", padding: 10, cornerRadius: 10, displayColors: true },
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 6 } },
        y: { grid: { color: SELAMET_COLORS.grid }, ticks: { maxTicksLimit: 5 } },
      },
      ...opts,
    },
  });
}

/** Grafik batang (durasi misting, curah hujan, lalu lintas, dll). */
function selametBarChart(ctx, labels, datasets, opts = {}) {
  return new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: datasets.map((d) => ({ borderRadius: 6, maxBarThickness: 22, ...d })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: datasets.length > 1 } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: SELAMET_COLORS.grid }, ticks: { maxTicksLimit: 5 } },
      },
      ...opts,
    },
  });
}

/** Donat/pie — dipakai untuk proporsi (mis. perilaku lebah normal/abnormal/fanning).
 *  Bisa diberi teks di tengah lingkaran lewat opts.centerText: {value, label}. */
function selametDoughnut(ctx, labels, data, colors, opts = {}) {
  const centerText = opts.centerText;
  delete opts.centerText;

  const centerTextPlugin = {
    id: "centerText",
    afterDraw(chart) {
      if (!centerText) return;
      const { ctx, chartArea: { left, right, top, bottom } } = chart;
      const cx = (left + right) / 2;
      const cy = (top + bottom) / 2;
      ctx.save();
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = SELAMET_COLORS.text;
      ctx.font = "700 18px 'Plus Jakarta Sans', sans-serif";
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim() || "#14201B";
      ctx.fillText(centerText.value, cx, cy - (centerText.label ? 9 : 0));
      if (centerText.label) {
        ctx.font = "600 10.5px 'Plus Jakarta Sans', sans-serif";
        ctx.fillStyle = SELAMET_COLORS.text;
        ctx.fillText(centerText.label, cx, cy + 12);
      }
      ctx.restore();
    },
  };

  return new Chart(ctx, {
    type: "doughnut",
    data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0, hoverOffset: 6 }] },
    plugins: centerText ? [centerTextPlugin] : [],
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "68%",
      plugins: { legend: { position: "bottom" } },
      ...opts,
    },
  });
}

/**
 * Radar/spider chart — dipakai untuk melihat beberapa jenis risiko
 * sekaligus dalam satu tampilan (mirip grafik "Leverages" pada referensi),
 * lebih mudah dibaca polanya dibanding 4 angka terpisah.
 */
function selametRadarChart(ctx, labels, data, color) {
  return new Chart(ctx, {
    type: "radar",
    data: {
      labels,
      datasets: [{
        data,
        borderColor: color,
        borderWidth: 2.5,
        pointBackgroundColor: color,
        pointBorderColor: "#fff",
        pointBorderWidth: 1.5,
        pointRadius: 4,
        pointHoverRadius: 6,
        backgroundColor: color + "26",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { backgroundColor: "#0B2A3D", padding: 10, cornerRadius: 10 } },
      scales: {
        r: {
          min: 0, max: 100,
          grid: { color: SELAMET_COLORS.grid },
          angleLines: { color: SELAMET_COLORS.grid },
          pointLabels: { font: { size: 11, weight: 600 }, color: SELAMET_COLORS.text },
          ticks: { display: false, stepSize: 25 },
        },
      },
    },
  });
}

/**
 * Sparkline mini — grafik tren kecil tanpa sumbu/label, dipakai di dalam
 * kartu statistik (mis. Suhu Luar, Kelembapan) supaya angka tidak berdiri
 * sendiri tanpa konteks tren beberapa jam terakhir.
 */
function selametSparkline(ctx, data, color) {
  return new Chart(ctx, {
    type: "line",
    data: {
      labels: data.map(() => ""),
      datasets: [{
        data,
        borderColor: color,
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.45,
        fill: true,
        backgroundColor: (context) => {
          const g = context.chart.ctx.createLinearGradient(0, 0, 0, 34);
          g.addColorStop(0, color + "33");
          g.addColorStop(1, color + "00");
          return g;
        },
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 700 },
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: {
        x: { display: false },
        y: { display: false },
      },
      elements: { point: { hoverRadius: 0 } },
    },
  });
}
