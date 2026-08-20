# Panduan Edit Tampilan SELAMET

File CSS dan JS sudah dipecah per fungsi supaya gampang dicari. Berikut peta lengkapnya.

## 🎨 CSS — urutan baca: 1 → 2 → 3 → 4

| File | Isinya | Kapan diedit |
|---|---|---|
| `static/css/1-variables.css` | **Semua warna, radius sudut, kecepatan animasi.** | Paling sering. Mau ganti warna kuning/hijau, mode gelap, ukuran sudut kartu — edit di sini saja, otomatis berubah di semua halaman. |
| `static/css/2-base.css` | Font, reset dasar, animasi masuk halaman. | Jarang. Edit kalau mau ganti font atau matikan animasi fade-in. |
| `static/css/3-layout.css` | Sidebar, header atas, bottom nav (mobile), tombol mengambang. | Kalau mau ubah SUSUNAN sidebar/header, lebar sidebar, dll. |
| `static/css/4-components.css` | **Kartu, tombol, badge, tabel, switch, filter pill.** | Paling sering kedua. Mau ubah gaya tombol (`.btn-honey`, `.btn-outline-soft`, `.btn-danger-soft`), bentuk kartu (`.card-soft`), atau warna badge status. |
| `static/css/login.css` | Khusus halaman login (background gelap + kartu tengah). | Kalau cuma mau ubah tampilan halaman login. |

**Contoh:** mau ganti warna kuning honey jadi warna lain? Buka `1-variables.css`, cari baris:
```css
--honey-gold: #E9A23B;
```
Ganti kode warnanya — semua tombol, ikon, dan aksen kuning di seluruh web ikut berubah.

**Contoh lain:** mau tombol jadi lebih kotak (sudut kurang bulat)? Di `1-variables.css`:
```css
--radius-sm: 10px;   /* kecilkan angka ini untuk sudut lebih kotak */
```

## 📊 Grafik & gauge (bukan cuma angka persen)

Beberapa kartu sekarang punya elemen visual, bukan cuma teks angka:
- **Ring gauge kecil** (lingkaran progres) — dipakai di kartu risiko Beranda & KPI Wawasan AI. Markup-nya ada di file HTML masing-masing (`home.html`, `prediction.html`), animasinya diatur di `ui.js` (`animateRings()`), warnanya di-set lewat `style="stroke:var(--nama-warna)"` di tag `<circle>`.
- **Sparkline mini** — grafik tren kecil di kartu Pemantauan Lingkungan, dibuat lewat `selametSparkline()` di `charts.js`.
- **Donut chart** — proporsi perilaku lebah di halaman Kamera, dibuat lewat `selametDoughnut()`.

Mau tambah gauge/grafik serupa di kartu lain? Tinggal contek pola yang sudah ada di `home.html` atau `prediction.html`, lalu panggil fungsi yang sesuai dari `charts.js`.

## ⚙️ JavaScript

| File | Isinya |
|---|---|
| `static/js/theme.js` | Logika tombol mode gelap/terang (ikon matahari/bulan di header) + menyimpan pilihan di browser. |
| `static/js/ui.js` | Panel notifikasi, filter pill (7 Hari/14 Hari/dst), animasi ring skor & progress bar, efek tombol ditekan. |
| `static/js/charts.js` | Pengaturan tampilan semua grafik (Chart.js) — warna garis, gaya tooltip, dll. |
| `static/js/socket-client.js` | Update data real-time di Beranda tanpa refresh halaman. |

## 📄 HTML (Jinja templates)

Semua ada di folder `templates/`. Satu file = satu halaman:

| File | Halaman |
|---|---|
| `layout.html` | Kerangka bersama (sidebar, header, bottom nav) — dipakai semua halaman lain lewat `{% extends "layout.html" %}` |
| `login.html` | Halaman login/daftar |
| `home.html` | Beranda |
| `prediction.html` | Wawasan AI |
| `history.html` | Riwayat & Rekomendasi |
| `camera.html` | Kamera |
| `misting.html` | Pengabutan Pintar |
| `settings.html` | Pengaturan |

**Menambah tombol baru?** Contoh menambah tombol kuning di halaman manapun:
```html
<button class="btn-honey">Teks Tombol</button>
```
Ganti `btn-honey` dengan `btn-outline-soft` (netral) atau `btn-danger-soft` (merah/bahaya) sesuai kebutuhan — gayanya sudah otomatis mengikuti tema.

**Menambah kartu baru?** Bungkus dengan:
```html
<div class="card-soft hoverable">
  <p class="card-label">Judul Kecil</p>
  <p class="card-value">123</p>
  <p class="card-sub">Keterangan</p>
</div>
```

## Alur setelah edit

Tidak perlu build/compile apapun — ini murni HTML/CSS/JS yang dibaca langsung oleh Flask.
Simpan file, refresh browser (`Ctrl+Shift+R` / hard refresh kalau perubahan CSS tidak muncul karena cache), selesai.
