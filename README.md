# AVESONIC: dashboard pengenalan spesies burung Indonesia dari suara

Dashboard Streamlit untuk tugas Data Mining. Lima halaman:

| Halaman | Isi |
|---|---|
| Beranda | Ringkasan dan tiga temuan utama dalam bahasa sehari-hari |
| Kenali Datanya | Sepuluh spesies (audio + spektrogram), tiga temuan pemeriksaan data, lalu tab: jumlah per spesies, lokasi (peta dan spesies per wilayah), pembagian data, tabel |
| Coba Tebak | Tebak spesies dari klip contoh, unggahan, atau rekaman mikrofon; wilayah perekaman bisa diisi (opsional) |
| Hasil Analisis | Empat tab: papan peringkat (sebelum–sesudah dalam satu tampilan), per spesies, seberapa bisa dipercaya, peragaan DTW |
| Catatan & Sumber | Batasan, kamus istilah, daftar perekam, lisensi, ringkasan metode |

## Yang baru di versi 2

- Model di halaman Coba Tebak: BirdNET 2.4 + **regresi logistik** (sebelumnya SVM), dilatih pada data latih + validasi setelah 5 rekaman ganda dibuang, dengan angka keyakinan yang dikalibrasi. Data uji: akurasi per klip 83,2% (sebelumnya 81,3%), per rekaman 89,4%.
- Tiap metode pembanding diperbaiki berdasarkan sifat data; halaman Hasil Analisis menampilkan sebelum dan sesudahnya, serta metode ketujuh (fusi BirdNET + Perch).
- Bagian baru "Seberapa tahan model terhadap perekam yang belum dikenal?" dan pilihan wilayah perekaman (opsional).
- Analisis lengkapnya ada di notebook `analisis_suara_burung_v2.ipynb`.

## Menjalankan di komputer sendiri

Butuh Python 3.12.

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

Lalu buka http://localhost:8501.

## Memasang di Streamlit Community Cloud

1. Unggah seluruh isi folder ini ke sebuah repositori GitHub.
2. Di https://share.streamlit.io pilih repositori itu, berkas utama `app.py`, dan Python 3.12.
3. `requirements.txt` dan `packages.txt` dibaca otomatis.

Pemasangan di Streamlit Community Cloud belum diuji.

## Status pengujian

- Versi 2 (model baru) sudah dijalankan pemiliknya dengan Streamlit.
- **Perombakan tampilan (versi 2.1) belum dijalankan dengan Streamlit sungguhan.** Lingkungan tempat perombakan dibuat tidak memiliki Streamlit maupun Plotly. Yang diperiksa: semua berkas lolos kompilasi; kelima halaman dan keempat tab dijalankan dengan Streamlit dan Plotly tiruan; komponen HTML/CSS buatan sendiri (kartu temuan, papan peringkat, pita, daftar batasan) dipotret dengan Chrome. Grafik Plotly, tab, dan widget asli Streamlit tidak terlihat di pemeriksaan itu. Buka kelima halaman dan tiap tab sekali sebelum dipakai.

## Catatan penting

- **Model BirdNET diunduh otomatis.** Saat pertama kali ada unggahan atau rekaman, aplikasi mengunduh model BirdNET 2.4 (sekitar 77 MB) dari Zenodo ke `aset/birdnet/`. Klip contoh tidak membutuhkan unduhan ini. Model BirdNET berlisensi CC BY-NC-SA 4.0.
- **Model pengklasifikasi tidak lagi bergantung pada scikit-learn.** Regresi logistik hasil analisis versi 2 disimpan sebagai tabel angka (`aset/model_birdnet_lr.npz`, sekitar 40 KB) dan dihitung langsung dengan NumPy.
- **Lokasi bersifat opsional.** Bila wilayah diisi di halaman Coba Tebak, peluang ditimbang dengan tabel "spesies mana direkam di wilayah mana" dari data latih. Bawaannya kosong (tebakan dari suara saja).
- **Rekaman panjang** dianalisis 60 detik pertamanya, paling banyak 8 potongan 3 detik yang paling bersuara.
- **Klip contoh** diambil dari data uji, hanya dari rekaman berlisensi BY-NC-SA atau lebih longgar, dipilih berdasarkan kejernihan tanpa melihat benar-salahnya tebakan model.

## Struktur

```
app.py                  titik masuk + navigasi
avesonic/tema.py           CSS, komponen, gaya grafik
avesonic/mesin.py          aset, pengolahan audio, BirdNET + regresi logistik, MFCC/DTW peragaan
avesonic/halaman/*.py      lima halaman
aset/                   model (npz), ringkasan hasil, metadata, 30 klip contoh, logo
alat/siapkan_aset.py    membangun ulang isi aset/ dari ekspor notebook analisis versi 2
```

## Sumber

Rekaman berasal dari Xeno-canto (https://xeno-canto.org) dan tetap milik perekamnya masing-masing di bawah lisensi Creative Commons. Nama Indonesia spesies mengikuti "Daftar nama burung di Indonesia" di Wikipedia bahasa Indonesia.
