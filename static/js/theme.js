/**
 * static/js/theme.js
 * Mengatur mode terang/gelap: menyimpan pilihan pengguna di browser
 * (localStorage) dan menerapkannya, plus efek putar halus pada ikon
 * saat tombol tema di header diklik.
 *
 * Cara kerja singkat:
 *  1. applyStoredTheme() jalan duluan (sebelum halaman selesai dimuat)
 *     supaya tema langsung benar tanpa "kedip".
 *  2. initThemeToggle() memasang event klik pada tombol matahari/bulan
 *     di pojok kanan atas (elemen dengan atribut data-theme-toggle).
 */

(function () {
  "use strict";

  function applyStoredTheme() {
    try {
      const saved = localStorage.getItem("selamet-theme");
      if (saved === "dark" || saved === "light") {
        document.documentElement.setAttribute("data-theme", saved);
      }
    } catch (e) { /* localStorage tidak tersedia — pakai tema bawaan server */ }
  }

  function syncToggleIcon() {
    const toggleBtn = document.querySelector("[data-theme-toggle]");
    if (!toggleBtn) return;
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const icon = toggleBtn.querySelector(".material-symbols-rounded");
    if (icon) icon.textContent = isDark ? "light_mode" : "dark_mode";
  }

  function initThemeToggle() {
    const toggleBtn = document.querySelector("[data-theme-toggle]");
    if (!toggleBtn) return;

    toggleBtn.addEventListener("click", function () {
      const root = document.documentElement;
      const isDark = root.getAttribute("data-theme") === "dark";

      // Efek putar halus pada ikon saat diklik — ganti nilai di sini
      // kalau mau efeknya berbeda.
      toggleBtn.style.transform = "rotate(-25deg) scale(0.9)";
      setTimeout(() => { toggleBtn.style.transform = ""; }, 220);

      root.setAttribute("data-theme", isDark ? "light" : "dark");
      syncToggleIcon();
      try { localStorage.setItem("selamet-theme", isDark ? "light" : "dark"); } catch (e) {}
    });
  }

  applyStoredTheme();
  document.addEventListener("DOMContentLoaded", function () {
    syncToggleIcon();
    initThemeToggle();
  });
})();
