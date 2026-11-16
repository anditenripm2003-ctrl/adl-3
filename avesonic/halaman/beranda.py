import streamlit as st
from avesonic import tema, mesin
from avesonic.tema import angka, persen


def tampil():
    h = mesin.hasil()
    m = {x["model"].split("_")[0]: x for x in h["metode"]}
    terbaik, app, dtw = h["metode"][0], m["birdnet24"], m["dtw"]
    md = h["model_dashboard"]; n_met = {6: "enam", 7: "tujuh", 8: "delapan"}.get(len(h["metode"]), str(len(h["metode"])))

    batang = mesin.batang_gelombang("mountain_tailorbird_1.wav", n=44)
    st.markdown(f"""
<div class="hero">
  <div>
    <div class="brand">AVESONIC</div>
    <div class="tagline">Dengar. Ukur. Kenali.</div>
    <div class="sub">Pengenalan suara burung Indonesia</div>
    <div class="lead">Bisakah komputer mengenali burung hanya dari suaranya?</div>
    <p class="desc">Kami mengumpulkan {angka(h['n_klip'])} potongan suara dari 10 spesies burung yang direkam di Indonesia, memeriksa sifat datanya, lalu menguji dan memperbaiki {n_met} cara berbeda untuk menebak spesiesnya. Dashboard ini merangkum datanya, hasilnya, dan memberi Anda kesempatan mencobanya sendiri.</p>
  </div>
  <div>{tema.svg_hero(batang)}</div>
</div>""", unsafe_allow_html=True)

    tema.ubin([
        (angka(h["n_klip"]), "klip suara", "masing-masing 3 detik"),
        (angka(h["n_rekaman"]), "rekaman lapangan", "sumber: Xeno-canto"),
        ("10", "spesies burung", "direkam di Indonesia"),
        (angka(h["n_perekam"]), "perekam", "relawan dan peneliti"),
    ])

    tema.judul_bagian("Temuan utama", "Tiga hal yang kami pelajari",
                      "Semua angka di bawah diukur pada klip yang tidak pernah dipakai untuk melatih model.")
    st.markdown(f"""
<div class="kartu-baris">
  <div class="kartu gelap">
    <div class="no">01</div>
    <h3>Ya, bisa. Lebih dari 8 dari 10 tebakan benar.</h3>
    <div class="besar">{persen(terbaik['uji_akurasi'])} <small>klip ditebak benar</small></div>
    <p>Itu hasil cara terbaik yang kami uji ({terbaik['nama'].split(' + regresi')[0]}). Sebagai pembanding, menebak asal-asalan di antara 10 spesies hanya benar sekitar 10%.</p>
  </div>
  <div class="kartu emas">
    <div class="no">02</div>
    <h3>Model yang sudah "berpengalaman" jauh lebih unggul.</h3>
    <div class="besar">{persen(app['uji_akurasi'])} <small>vs {persen(dtw['uji_akurasi'])}</small></div>
    <p>Model yang sebelumnya sudah belajar dari sangat banyak suara burung mengalahkan cara pencocokan pola klasik (DTW) dengan selisih {angka(100 * (app['uji_akurasi'] - dtw['uji_akurasi']))} poin persen, bahkan setelah DTW diperbaiki.</p>
  </div>
  <div class="kartu sage">
    <div class="no">03</div>
    <h3>Makin lama didengar, makin tepat.</h3>
    <div class="besar">{persen(app['rekaman_akurasi'])} <small>per rekaman utuh</small></div>
    <p>Jika model mendengar beberapa potongan dari rekaman yang sama lalu menggabungkan tebakannya, ketepatannya naik dari {persen(app['uji_akurasi'])} menjadi {persen(app['rekaman_akurasi'])}.</p>
  </div>
</div>""", unsafe_allow_html=True)

    tema.judul_bagian("Yang perlu diingat", "Angka di atas berlaku untuk perekam yang sudah dikenal",
                      f"Sebagian besar klip uji berasal dari perekam yang rekaman lainnya ikut dipakai melatih. Saat perekam dipisahkan sepenuhnya, nilai rapor model di halaman Coba Tebak turun dari {angka(md['cv_sesi'], 2)} menjadi {angka(md['cv_perekam'], 2)} (macro-F1 per klip). "
                      "Untuk rekaman Anda sendiri, harapkan ketepatan di sekitar angka yang kedua, dan lebih tinggi bila rekamannya cukup panjang untuk dipotong menjadi beberapa bagian.")

    tema.judul_bagian("Cara kerja", "Dari kicauan menjadi nama spesies")
    st.markdown("""
<div class="langkah">
  <div><div class="eyebrow">Langkah 1</div><b>Dengarkan potongan 3 detik</b><span>Rekaman dipotong menjadi klip pendek. Bagian yang hanya berisi angin atau senyap dilewati.</span></div>
  <div><div class="eyebrow">Langkah 2</div><b>Ubah menjadi "sidik suara"</b><span>Tiap klip diringkas menjadi 1.024 angka yang menggambarkan nada, irama, dan warna suaranya.</span></div>
  <div><div class="eyebrow">Langkah 3</div><b>Cocokkan dengan 10 spesies</b><span>Model sederhana yang sudah belajar dari ribuan contoh menimbang sidik suara itu dan memberi peluang untuk tiap spesies.</span></div>
</div>""", unsafe_allow_html=True)

    tema.judul_bagian("Jelajahi", "Mulai dari mana?")
    a, b, c = st.columns(3)
    with a:
        st.page_link(st.session_state["_hal"]["tebak"], label="Coba tebak suara burung", icon=":material/graphic_eq:")
    with b:
        st.page_link(st.session_state["_hal"]["data"], label="Kenali 10 spesiesnya", icon=":material/travel_explore:")
    with c:
        st.page_link(st.session_state["_hal"]["hasil"], label="Lihat perbandingan metode", icon=":material/leaderboard:")
