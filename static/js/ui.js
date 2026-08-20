/**
 * static/js/ui.js
 * Interaksi UI umum yang dipakai di banyak halaman:
 *  - Panel notifikasi (buka/tutup lewat ikon lonceng)
 *  - Filter pill (7 Hari / 14 Hari / dst — highlight yang aktif)
 *  - Animasi ring skor & progress bar risiko saat halaman dimuat
 *  - Efek "tekan" halus pada tombol supaya terasa hidup
 *
 * Tema (mode gelap/terang) ada di file terpisah: theme.js
 */

(function () {
  "use strict";

  function initNotificationPanel() {
    const bell = document.querySelector("[data-notif-bell]");
    const panel = document.querySelector("[data-notif-panel]");
    if (!bell || !panel) return;

    bell.addEventListener("click", function (e) {
      e.stopPropagation();
      panel.classList.toggle("d-none");
    });
    document.addEventListener("click", function (e) {
      if (!panel.contains(e.target)) panel.classList.add("d-none");
    });
  }

  function initFilterPills() {
    document.querySelectorAll("[data-filter-group]").forEach(function (group) {
      group.querySelectorAll(".filter-pill").forEach(function (pill) {
        pill.addEventListener("click", function () {
          group.querySelectorAll(".filter-pill").forEach((p) => p.classList.remove("active"));
          pill.classList.add("active");
        });
      });
    });
  }

  // Progress bar risiko (Beranda, Misting, dll): mulai dari 0% lalu
  // animasi mengisi ke nilai aslinya (dibaca dari atribut data-risk-fill).
  function animateRiskBars() {
    document.querySelectorAll("[data-risk-fill]").forEach(function (el) {
      const pct = el.getAttribute("data-risk-fill");
      requestAnimationFrame(() => { el.style.width = pct + "%"; });
    });
  }

  // Ring lingkaran skor kesehatan lebah — animasi dari kosong ke penuh.
  function animateRings() {
    document.querySelectorAll("[data-ring-value]").forEach(function (circle) {
      const pct = parseFloat(circle.getAttribute("data-ring-value")) || 0;
      const radius = circle.r.baseVal.value;
      const circumference = 2 * Math.PI * radius;
      circle.style.strokeDasharray = `${circumference} ${circumference}`;
      circle.style.strokeDashoffset = circumference;
      requestAnimationFrame(() => {
        const offset = circumference - (pct / 100) * circumference;
        circle.style.strokeDashoffset = offset;
      });
    });
  }

  // Efek "press" halus (mengecil dikit) saat tombol/ikon ditekan.
  function initButtonPress() {
    document.querySelectorAll(".btn-honey, .btn-outline-soft, .btn-danger-soft, .icon-btn").forEach(function (btn) {
      btn.addEventListener("pointerdown", () => { btn.style.transform = "scale(0.97)"; });
      btn.addEventListener("pointerup", () => { btn.style.transform = ""; });
      btn.addEventListener("pointerleave", () => { btn.style.transform = ""; });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initNotificationPanel();
    initFilterPills();
    animateRiskBars();
    animateRings();
    initButtonPress();
  });
})();
