import streamlit as st
from avesonic import tema, mesin
from avesonic.tema import angka, persen


def tampil():
    h = mesin.hasil(); meta = mesin.metadata()
    st.markdown('<div class="eyebrow">Catatan & sumber</div>', unsafe_allow_html=True)
    st.title("Yang perlu diketahui sebelum mempercayai angkanya")
    st.markdown("Hasil di dashboard ini berasal dari satu rangkaian percobaan pada satu dataset. Berikut batasannya, cara membaca istilahnya, dan dari mana datanya berasal.")

    tema.judul_bagian("Batasan", "Delapan hal yang membatasi kesimpulan")
    st.markdown("""
<div class="kartu-baris">
  <div class="kartu"><div class="no">01</div><h3>Hanya 10 spesies</h3><p>Indonesia punya lebih dari 1.700 spesies burung. Model ini hanya bisa memilih di antara sepuluh, dan akan memaksakan salah satunya untuk suara apa pun.</p></div>
  <div class="kartu"><div class="no">02</div><h3>Model terlatih mungkin pernah mendengar rekamannya</h3><p>BirdNET dan Perch dilatih antara lain dari Xeno-canto, sumber dataset ini. Skor keduanya bisa sedikit terlalu bagus.</p></div>
  <div class="kartu"><div class="no">03</div><h3>Klip tidak diperiksa manusia</h3><p>Klip dipilih otomatis. Sebagian bisa berisi burung lain di latar atau hanya derau, dan itu menurunkan skor semua metode.</p></div>
  <div class="kartu"><div class="no">04</div><h3>CNN versi kecil, tidak diperbarui</h3><p>Jaringan saraf di sini kecil, dilatih singkat tanpa GPU, dan tidak dilatih ulang di versi 2. Versi yang lebih besar atau memakai bobot terlatih bisa lebih baik.</p></div>
  <div class="kartu"><div class="no">05</div><h3>Data uji sudah pernah dilihat</h3><p>Data uji yang sama dipakai melaporkan versi 1. Di versi 2 tidak ada pengaturan yang dipilih dengan melihatnya, tetapi ia bukan lagi ujian yang sepenuhnya baru.</p></div>
  <div class="kartu"><div class="no">06</div><h3>Perekam yang sama di latihan dan ujian</h3><p>Data dibagi per sesi, bukan per perekam. Hampir semua klip uji berasal dari perekam yang sudah dikenal model, sehingga skor uji lebih tinggi daripada yang akan didapat pada rekaman orang lain.</p></div>
  <div class="kartu"><div class="no">07</div><h3>Suara di atas 8 kHz hilang</h3><p>Klip disimpan pada 16 kHz. Ceret sulawesi bernada sekitar 6 kHz dan sebagian suaranya mepet batas itu. Ini keterbatasan data, bukan model.</p></div>
  <div class="kartu"><div class="no">08</div><h3>Bukan pengganti ahli</h3><p>Ini alat bantu belajar, bukan alat identifikasi resmi. Untuk keperluan penelitian atau konservasi, hasilnya perlu dikonfirmasi pengamat burung.</p></div>
</div>""", unsafe_allow_html=True)

    tema.judul_bagian("Kamus kecil", "Cara membaca istilah di dashboard ini")
    st.markdown("""
<div class="langkah">
  <div><div class="eyebrow">Akurasi</div><b>Berapa bagian yang benar</b><span>Dari 100 klip, berapa yang spesiesnya ditebak benar. Mudah dipahami, tetapi bisa menipu jika satu spesies datanya jauh lebih banyak.</span></div>
  <div><div class="eyebrow">Macro-F1</div><b>Rapor rata-rata per spesies</b><span>Tiap spesies diberi nilai 0 sampai 1, lalu dirata-rata. Spesies langka sama pentingnya dengan yang banyak. Inilah ukuran utama di sini.</span></div>
  <div><div class="eyebrow">Rentang 95%</div><b>Seberapa goyah angkanya</b><span>Jika rekaman ujinya diganti dengan rekaman lain yang setara, skor kemungkinan besar tetap jatuh di dalam rentang ini.</span></div>
</div>""", unsafe_allow_html=True)

    tema.judul_bagian("Sumber data", "Terima kasih kepada para perekam",
                      f"Semua {angka(h['n_rekaman'])} rekaman berasal dari Xeno-canto dan tetap menjadi milik {h['n_perekam']} perekamnya. Tabel berikut memuat semua perekam beserta jumlah rekaman yang dipakai.")
    per = meta.drop_duplicates("id_rekaman").groupby("perekam").agg(rekaman=("id_rekaman", "size"), spesies=("label", "nunique")).sort_values("rekaman", ascending=False).reset_index()
    per.columns = ["Perekam", "Rekaman", "Spesies"]
    a, b = st.columns([6, 5], gap="large")
    with a:
        st.dataframe(per, width="stretch", height=380, hide_index=True)
    with b:
        lis = meta.drop_duplicates("id_rekaman")["lisensi"].str.extract(r"licenses/([a-z\-]+)")[0].str.upper().value_counts()
        nd = int(lis[[k for k in lis.index if "ND" in k]].sum())
        st.markdown(f"""
<div class="kartu">
  <div class="no">LISENSI</div>
  <h3>Creative Commons, hampir semuanya non-komersial</h3>
  <p>{" · ".join(f"{k}: {angka(v)}" for k, v in lis.items())} rekaman.</p>
  <p style="margin-top:10px">{angka(nd)} rekaman berlisensi "tanpa turunan" (ND). Karena itu klip contoh yang bisa diputar di dashboard ini hanya diambil dari rekaman berlisensi BY-NC-SA atau lebih longgar, masing-masing dengan nama perekam dan tautan sumbernya.</p>
</div>""", unsafe_allow_html=True)
        st.markdown("")
        st.page_link("https://xeno-canto.org", label="Buka Xeno-canto", icon=":material/open_in_new:")

    tema.judul_bagian("Metode singkat", "Bagaimana analisis dilakukan")
    st.markdown(f"""
- **Data.** {angka(h['n_klip'])} klip 3 detik (16 kHz, mono) dari 10 spesies dengan rekaman Indonesia terbanyak di Xeno-canto. Satu spesies (kepudang kuduk-hitam) diganti karena rekamannya tidak dapat diunduh.
- **Pembagian.** Latih {angka(h['n_latih'])}, validasi {angka(h['n_validasi'])}, uji {angka(h['n_uji'])} klip; dibagi per sesi rekaman.
- **Pembersihan.** {h['n_duplikat_pasang']} rekaman ternyata diunggah ganda di Xeno-canto dengan nomor berbeda, satu di antaranya ada di data latih sekaligus uji. Salinannya ({h['n_duplikat_klip']} klip) dibuang dari data latih dan validasi.
- **Pemilihan pengaturan.** Semua pengaturan dipilih di data latih + validasi dengan validasi silang 5-lipatan, dua kali: dikelompokkan per sesi dan per perekam. Tambahan yang membuat model lebih rumit dipakai hanya bila membantu di keduanya. Data uji tidak dipakai untuk memilih.
- **Ketidakpastian.** Rentang 95% dihitung dengan mengambil ulang rekaman uji secara acak sebanyak 2.000 kali (bootstrap per rekaman).
- **Model di halaman Coba Tebak.** BirdNET 2.4 sebagai pembuat sidik suara + regresi logistik (C = {angka(h['model_dashboard']['C'], 3)}), dilatih pada data latih + validasi, dengan angka keyakinan yang dikalibrasi. Pada data uji: {persen(h['model_dashboard']['akurasi'])} klip benar, {persen(h['model_dashboard']['top3'])} jika tiga tebakan teratas dihitung, dan {persen(h['model_dashboard']['rekaman_akurasi'])} per rekaman utuh.
- **Kenapa bukan model paling tepat?** Fusi BirdNET + Perch sedikit lebih tepat, tetapi membutuhkan dua model besar berjalan untuk tiap unggahan. Dashboard memakai BirdNET saja agar ringan dan bisa dipasang di layanan gratis.
- **Lokasi (opsional).** Bila wilayah perekaman diisi, peluang tiap spesies ditimbang dengan seberapa sering spesies itu direkam di wilayah tersebut dalam data latih. Pada data uji, dengan wilayah yang benar, macro-F1 per klip berubah {'+' if h['lokasi']['selisih'] >= 0 else '−'}{angka(abs(h['lokasi']['selisih']), 3)} (rentang 95%: {angka(h['lokasi']['selisih_lo'], 3)} sampai {angka(h['lokasi']['selisih_hi'], 3)}). Tabel itu mencerminkan tempat orang merekam, bukan sebaran burung yang sebenarnya.
- **Perangkat.** Python, NumPy, SciPy, scikit-learn, PyTorch (CNN versi 1), BirdNET, Perch, Streamlit, dan Plotly. Model BirdNET berlisensi CC BY-NC-SA 4.0.
""")
