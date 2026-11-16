import numpy as np
import plotly.graph_objects as go
import streamlit as st
from avesonic import tema, mesin
from avesonic.tema import angka, persen

GAGASAN = {
    "fusi": "Dua model terlatih (BirdNET dan Perch) masing-masing membuat \"sidik suara\" tiap klip; keduanya digabung sebelum model sederhana memutuskan. Paling tepat, tetapi butuh dua model berjalan sekaligus.",
    "perch2": "Model Perch v2 (Google), yang sudah belajar dari suara ribuan spesies, membuat \"sidik suara\" tiap klip. Model sederhana (regresi logistik) lalu diajari membedakan 10 spesies ini.",
    "birdnet24": "Sama seperti di atas, memakai model BirdNET 2.4 (Cornell dan TU Chemnitz). Ini model yang dipakai di halaman Coba Tebak.",
    "cnn": "Jaringan saraf melihat potret suara (spektrogram) seperti melihat gambar, dan belajar dari nol hanya dari data ini. Tidak diubah di versi 2.",
    "klasik": "Tiap klip diringkas menjadi ratusan angka statistik (tinggi nada, irama, kekasaran), kini diukur di atas derau latar, lalu model statistik sederhana belajar membedakannya.",
    "dtw": "Satu detik paling bersuara dari klip baru dicocokkan di mana saja dalam ribuan klip contoh. Sumbu waktu boleh sedikit \"ditarik-ulur\" agar tempo yang berbeda tetap cocok.",
    "euclid": "Seperti DTW, tetapi tanpa tarik-ulur: potongan satu detik hanya digeser sampai posisinya paling cocok.",
}
PENDEK = {"fusi": "Fusi BirdNET + Perch", "perch2": "Perch v2", "birdnet24": "BirdNET 2.4", "cnn": "CNN dari nol", "klasik": "Fitur ringkasan", "dtw": "DTW", "euclid": "Euclid"}
PERUBAHAN = {
    "perch2": "SVM diganti regresi logistik ber-regularisasi kuat; dilatih di data latih + validasi.",
    "birdnet24": "SVM diganti regresi logistik ber-regularisasi kuat; dilatih di data latih + validasi; angka keyakinan dikalibrasi.",
    "klasik": "Ditambah 350 fitur baru: suara diukur di atas derau latar, dibobot keaktifan, dan irama diringkas dengan spektrum modulasi.",
    "dtw": "Yang dicocokkan kini potongan 1 detik paling bersuara, di mana pun letaknya, dengan pelengkungan kecil; tetangga dibobot jaraknya.",
    "euclid": "Potongan 1 detik paling bersuara digeser sepanjang klip contoh; tanpa pelengkungan.",
}
BILANGAN = {5: "Lima", 6: "Enam", 7: "Tujuh", 8: "Delapan"}


def _kunci(m):
    return (m["model"] if isinstance(m, dict) else m).split("_")[0]


def tampil():
    h = mesin.hasil(); met = h["metode"]; labels = h["labels"]
    terbaik = met[0]; app = next(m for m in met if _kunci(m) == "birdnet24"); terlatih = [i for i, m in enumerate(met) if m["keluarga"] == "Model suara burung terlatih"]
    st.markdown('<div class="eyebrow">Hasil analisis</div>', unsafe_allow_html=True)
    st.title(f"{BILANGAN.get(len(met), str(len(met)))} cara menebak, satu ujian yang sama")
    st.markdown(f"Semua metode diuji pada **{angka(h['n_uji'])} klip dari {h['n_rekaman_uji']} rekaman** yang tidak pernah dipakai saat melatih. "
                f"Pemenangnya jelas: metode yang memanfaatkan model suara burung terlatih menebak benar **{persen(app['uji_akurasi'])}–{persen(terbaik['uji_akurasi'])}** klip. "
                f"Di versi ini tiap metode juga diperbaiki berdasarkan sifat datanya; hasil sebelum dan sesudahnya ada di bawah.")

    # ------------------------------------------------------------ perbandingan
    tema.judul_bagian("Perbandingan", "Metode mana yang paling tepat?")
    ukuran = st.segmented_control("Ukuran", ["Macro-F1", "Akurasi per klip", "Akurasi per rekaman"], default="Macro-F1", label_visibility="collapsed") or "Macro-F1"
    if ukuran == "Macro-F1":
        d = met; nilai = [m["uji_f1"] for m in d]
        fig = tema.batang_h([m["nama"] for m in d], nilai, [angka(v, 2) for v in nilai],
                            [f"<b>{m['nama']}</b><br>{m['keluarga']}<br>macro-F1 {angka(m['uji_f1'], 3)} (rentang 95%: {angka(m['lo'], 2)}–{angka(m['hi'], 2)})<br>akurasi per klip {persen(m['uji_akurasi'], 1)}" for m in d],
                            maks=1.0, bawah=[m["lo"] for m in d], atas=[m["hi"] for m in d], judul_x="macro-F1 di data uji (0 sampai 1)", sorot=terlatih)
        ket = "**Macro-F1** adalah rata-rata nilai ketepatan tiap spesies (0 sampai 1), sehingga spesies yang datanya sedikit sama pentingnya dengan yang banyak. Garis hitam menunjukkan rentang ketidakpastian 95%."
    elif ukuran == "Akurasi per klip":
        d = met; nilai = [m["uji_akurasi"] for m in d]
        fig = tema.batang_h([m["nama"] for m in d], nilai, [persen(v) for v in nilai], [f"<b>{m['nama']}</b><br>{persen(m['uji_akurasi'], 1)} dari {angka(h['n_uji'])} klip uji ditebak benar" for m in d],
                            maks=1.0, judul_x="bagian klip uji yang ditebak benar", sorot=terlatih)
        fig.update_xaxes(tickformat=".0%")
        fig.add_vline(x=0.1, line=dict(color=tema.REDUP, width=1, dash="dot"), annotation_text="tebak acak 10%", annotation_position="top", annotation_font=dict(color=tema.REDUP, size=11))
        ket = "**Akurasi per klip**: dari semua klip 3 detik di data uji, berapa bagian yang spesiesnya ditebak benar."
    else:
        d = [m for m in met if m["rekaman_akurasi"] is not None]; nilai = [m["rekaman_akurasi"] for m in d]
        fig = tema.batang_h([m["nama"] for m in d], nilai, [persen(v) for v in nilai], [f"<b>{m['nama']}</b><br>{persen(m['rekaman_akurasi'], 1)} dari {h['n_rekaman_uji']} rekaman uji ditebak benar<br>(per klip: {persen(m['uji_akurasi'], 1)})" for m in d],
                            maks=1.0, judul_x="bagian rekaman uji yang ditebak benar", sorot=terlatih)
        fig.update_xaxes(tickformat=".0%")
        ket = "**Akurasi per rekaman**: tebakan semua klip dari satu rekaman digabung menjadi satu jawaban."
    st.plotly_chart(fig, width="stretch", config=tema.KONFIG)
    st.caption(ket)

    with st.expander("Apa bedanya metode-metode itu? (penjelasan sederhana)"):
        for m in met:
            st.markdown(f"**{m['nama']}** · _{m['keluarga']}_  \n{GAGASAN[_kunci(m)]}")

    # ------------------------------------------------------------ sebelum-sesudah
    tema.judul_bagian("Perbaikan", "Sebelum dan sesudah: apa yang berubah di versi 2?",
                      "Sebelum memperbaiki apa pun, datanya diperiksa dulu. Tiap perubahan di bawah menjawab satu sifat data: klip dipotong di titik sembarang, derau latar berbeda antar-perekam, dan jumlah rekaman yang benar-benar berbeda hanya ratusan.")
    dua = [m for m in met if m.get("lama")]
    yl = [PENDEK[_kunci(m)] for m in dua]
    fig = go.Figure()
    for m, y in zip(dua, yl):
        fig.add_trace(go.Scatter(x=[m["lama"]["uji_f1"], m["uji_f1"]], y=[y, y], mode="lines", line=dict(color=tema.DATA_PUCAT, width=4), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=[m["lama"]["uji_f1"] for m in dua], y=yl, mode="markers", name="versi 1", marker=dict(size=13, color="#ffffff", line=dict(color=tema.DATA, width=2.5)),
                             customdata=[[m["lama"]["nama"], angka(m["lama"]["uji_f1"], 3)] for m in dua], hovertemplate="<b>versi 1</b> · %{customdata[0]}<br>macro-F1 %{customdata[1]}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[m["uji_f1"] for m in dua], y=yl, mode="markers", name="versi 2", marker=dict(size=13, color=tema.DATA, line=dict(color="#ffffff", width=2)),
                             customdata=[[m["nama"], angka(m["uji_f1"], 3), angka(m["lama"]["selisih"], 3), angka(m["lama"]["lo"], 3), angka(m["lama"]["hi"], 3)] for m in dua],
                             hovertemplate="<b>versi 2</b> · %{customdata[0]}<br>macro-F1 %{customdata[1]}<br>selisih %{customdata[2]} (rentang 95%: %{customdata[3]} sampai %{customdata[4]})<extra></extra>"))
    for m, y in zip(dua, yl):
        nyata = m["lama"]["lo"] > 0
        fig.add_annotation(x=max(m["uji_f1"], m["lama"]["uji_f1"]), y=y, showarrow=False, xanchor="left", xshift=14, font=dict(size=12, color=tema.TINTA if nyata else tema.REDUP),
                           text=f"<b>{'+' if m['lama']['selisih'] >= 0 else '−'}{angka(abs(m['lama']['selisih']), 2)}</b>" + ("" if nyata else " · belum pasti"))
    tema.gaya(fig, tinggi=90 + 46 * len(dua), legenda=True); fig.update_yaxes(autorange="reversed", showgrid=False, ticksuffix="  "); fig.update_xaxes(title_text="macro-F1 di data uji", range=[0.3, 1.0])
    st.plotly_chart(fig, width="stretch", config=tema.KONFIG)
    st.caption("Lingkaran kosong: versi 1. Lingkaran penuh: versi 2. \"Belum pasti\" berarti rentang ketidakpastian 95% selisihnya masih memuat nol. CNN tidak dilatih ulang, dan fusi adalah metode baru, sehingga keduanya tidak punya pasangan.")
    with st.expander("Apa persisnya yang diubah pada tiap metode?"):
        for m in dua:
            st.markdown(f"**{PENDEK[_kunci(m)]}** · {angka(m['lama']['uji_f1'], 2)} → {angka(m['uji_f1'], 2)}  \n{PERUBAHAN[_kunci(m)]}")
    if h.get("uji_gagasan"):
        with st.expander("Gagasan yang dicoba tetapi tidak dipakai"):
            st.markdown("Tiap gagasan dinilai dua kali di data latih + validasi: dengan klip dikelompokkan per sesi, dan per perekam. Angka adalah selisih macro-F1 beserta rentang 95%-nya. Sebuah gagasan dipakai hanya bila membantu di **kedua** cara.")
            st.dataframe([{"Perbandingan": g["perbandingan"], "Per sesi": g["sesi"].replace(".", ","), "Per perekam": g["perekam"].replace(".", ","), "Membantu di keduanya": "ya" if g["membantu"] else "tidak"} for g in h["uji_gagasan"]],
                         width="stretch", hide_index=True)

    # ------------------------------------------------------------ selisih
    tema.judul_bagian("Kepastian", "Apakah selisihnya sungguhan, atau kebetulan?",
                      "Selisih skor antara dua metode yang peringkatnya berurutan. Jika garisnya tidak menyentuh angka nol, selisih itu dapat dipercaya.")
    S = h["selisih"]; yl = [f"{PENDEK[_kunci(s['a'])]}  vs  {PENDEK[_kunci(s['b'])]}" for s in S]
    fig = go.Figure(go.Scatter(
        x=[s["selisih"] for s in S], y=yl, mode="markers", marker=dict(size=11, color=tema.DATA, line=dict(color="#ffffff", width=2)),
        error_x=dict(type="data", symmetric=False, array=[s["hi"] - s["selisih"] for s in S], arrayminus=[s["selisih"] - s["lo"] for s in S], color=tema.DATA, thickness=2, width=0),
        customdata=[[angka(s["selisih"], 3), angka(s["lo"], 3), angka(s["hi"], 3), "selisih nyata" if s["lo"] > 0 else "belum bisa dibedakan"] for s in S],
        hovertemplate="<b>%{y}</b><br>selisih macro-F1 %{customdata[0]}<br>rentang 95%: %{customdata[1]} sampai %{customdata[2]}<br>%{customdata[3]}<extra></extra>"))
    fig.add_vline(x=0, line=dict(color=tema.TINTA, width=1))
    for s, y in zip(S, yl):
        fig.add_annotation(x=s["hi"], y=y, text="nyata" if s["lo"] > 0 else "<b>belum bisa dibedakan</b>", showarrow=False, xanchor="left", xshift=10, font=dict(size=12, color=tema.TINTA2 if s["lo"] > 0 else tema.TINTA))
    tema.gaya(fig, tinggi=80 + 44 * len(S)); fig.update_yaxes(autorange="reversed", showgrid=False, ticksuffix="  ")
    fig.update_xaxes(title_text="selisih macro-F1 (metode pertama dikurangi metode kedua)", range=[min(-0.06, min(s["lo"] for s in S) - 0.02), max(s["hi"] for s in S) + 0.12])
    st.plotly_chart(fig, width="stretch", config=tema.KONFIG)
    seri = [f"{PENDEK[_kunci(s['a'])]} dan {PENDEK[_kunci(s['b'])]}" for s in S if s["lo"] <= 0]
    fg = next((g for g in h.get("uji_gagasan", []) if g["perbandingan"].startswith("Fusi BirdNET+Perch vs BirdNET")), None)
    tema.catatan((f"<b>Belum bisa dibedakan di data uji ini:</b> {'; '.join(seri)}. " if seri else "<b>Semua selisih antarperingkat nyata.</b> ")
                 + f"Data uji hanya {h['n_rekaman_uji']} rekaman, jadi selisih sekitar 0,02 sulit dipastikan dari sini."
                 + (f" Untuk fusi dan BirdNET, pemeriksaan terpisah di data latih + validasi ({angka(h['n_rekaman_pool'])} rekaman) memberi selisih {fg['sesi'].replace('.', ',')} bila dikelompokkan per sesi dan {fg['perekam'].replace('.', ',')} per perekam: kecil, tetapi konsisten." if fg and fg["membantu"] else ""))

    # ------------------------------------------------------------ perekam baru
    md = h["model_dashboard"]; baru = h["perekam"]["perekam baru"]
    tema.judul_bagian("Kejujuran angka", "Seberapa tahan model terhadap perekam yang belum dikenal?",
                      f"{persen(h['eda']['uji_dari_perekam_dikenal'])} klip uji berasal dari perekam yang rekaman lainnya ikut dipakai melatih. Rekaman yang Anda unggah berasal dari perekam dan alat yang sama sekali baru, jadi angka yang lebih relevan adalah yang tengah.")
    tema.ubin([
        (angka(md["cv_sesi"], 2), "macro-F1, perekam boleh sama", "validasi silang per sesi di data latih + validasi"),
        (angka(md["cv_perekam"], 2), "macro-F1, perekam dipisahkan", "validasi silang per perekam: perkiraan untuk perekam baru"),
        (angka(baru["n"]), "klip uji dari perekam baru", f"dari {baru['rekaman']} rekaman: terlalu sedikit untuk diukur langsung, karena itu dipakai validasi silang"),
    ])
    st.caption("Dua angka pertama untuk model di halaman Coba Tebak (BirdNET 2.4 + regresi logistik), per klip 3 detik. Menggabungkan beberapa potongan dari satu rekaman menaikkan ketepatan lagi.")

    # ------------------------------------------------------------ per spesies
    tema.judul_bagian("Per spesies", "Spesies mana yang mudah, mana yang sulit?")
    pilih = st.selectbox("Metode", [m["nama"] for m in met], index=0)
    m = next(x for x in met if x["nama"] == pilih)
    cm = np.array(m["confusion"]); f1 = np.array(m["f1_spesies"]); idn = [mesin.nama_id(l) for l in labels]
    a, b = st.columns([5, 6], gap="medium")
    with a:
        o = np.argsort(-f1)
        fig = tema.batang_h([idn[i] for i in o], [float(f1[i]) for i in o], [angka(f1[i], 2) for i in o],
                            [f"<b>{idn[i]}</b><br><i>{mesin.SPESIES[labels[i]][2]}</i><br>F1 {angka(f1[i], 3)} · {h['klip_uji_per_spesies'][i]} klip uji · {cm[i, i]} ditebak benar" for i in o],
                            tinggi=470, maks=1.12, judul_x="F1 per spesies (0 sampai 1)")
        st.plotly_chart(fig, width="stretch", config=tema.KONFIG)
    with b:
        norm = cm / cm.sum(1, keepdims=True)
        teks = [[str(v) if v else "" for v in r] for r in cm]
        fig = go.Figure(go.Heatmap(z=norm, x=idn, y=idn, zmin=0, zmax=1, colorscale=[[i / 5, c] for i, c in enumerate(tema.RAMP)], showscale=False, xgap=2, ygap=2,
                                   text=teks, texttemplate="%{text}", textfont=dict(size=11),
                                   customdata=[[[idn[i], idn[j], int(cm[i, j]), persen(norm[i, j])] for j in range(10)] for i in range(10)],
                                   hovertemplate="sebenarnya <b>%{customdata[0]}</b><br>ditebak <b>%{customdata[1]}</b><br>%{customdata[2]} klip (%{customdata[3]} dari spesies ini)<extra></extra>"))
        tema.gaya(fig, tinggi=470); fig.update_yaxes(autorange="reversed", showgrid=False, title_text="spesies sebenarnya", tickfont=dict(size=11)); fig.update_xaxes(showgrid=False, tickangle=-40, title_text="tebakan model", tickfont=dict(size=11, color=tema.TINTA2))
        st.plotly_chart(fig, width="stretch", config=tema.KONFIG)
    st.caption("Kiri: nilai F1 tiap spesies. Kanan: tabel silang; tiap baris adalah spesies sebenarnya, tiap kolom tebakan model. Kotak gelap di diagonal berarti tebakan benar; kotak di luar diagonal adalah salah tebak.")
    luar = cm.copy(); np.fill_diagonal(luar, 0); tiga = np.dstack(np.unravel_index(np.argsort(-luar, axis=None)[:3], luar.shape))[0]
    tema.catatan("<b>Paling sering tertukar:</b> " + " · ".join(f"{idn[i]} ditebak sebagai {idn[j]} ({luar[i, j]} klip)" for i, j in tiga) + ".")

    # ------------------------------------------------------------ kualitas
    tema.judul_bagian("Kualitas klip", "Klip yang jernih jauh lebih mudah ditebak")
    q = m["kualitas"]
    tema.ubin([
        (persen(q["aktivitas"]["akurasi"]), "benar pada klip \"jelas\"", f"{angka(q['aktivitas']['n'])} klip uji"),
        (persen(q["cadangan"]["akurasi"]), "benar pada klip \"cadangan\"", f"{angka(q['cadangan']['n'])} klip uji"),
        (persen(q["aktivitas"]["akurasi"] - q["cadangan"]["akurasi"]).replace("%", " poin"), "selisih", "untuk metode yang dipilih di atas"),
    ])
    st.caption("Klip \"cadangan\" adalah klip yang tidak lolos penyaring otomatis: suaranya terus-menerus, sangat sunyi, atau bernada di luar rentang 1–7,5 kHz yang didengar penyaring (misalnya paok halmahera, sekitar 1 kHz). "
               "Melatih model tanpa klip cadangan sudah diuji dan tidak membantu, jadi semua klip tetap dipakai.")

    # ------------------------------------------------------------ DTW
    tema.judul_bagian("Peragaan", "Bagaimana DTW \"menarik-ulur\" waktu?",
                      "Dua burung sejenis jarang berkicau dengan tempo yang persis sama. DTW (Dynamic Time Warping) mencari cara terbaik menyejajarkan dua suara dengan memelarkan atau memampatkan waktunya. Pilih dua klip untuk melihatnya.")
    daftar, _ = mesin.contoh()
    opsi = list(range(len(daftar))); fmt = lambda i: f"{mesin.nama_id(daftar[i]['label'])} · klip {daftar[i]['berkas'].rsplit('_', 1)[1][0]}"
    ia_awal = next(i for i, c in enumerate(daftar) if c["label"] == "pygmy_cupwing")
    c1, c2 = st.columns(2)
    with c1:
        ia = st.selectbox("Klip A", opsi, index=ia_awal, format_func=fmt); st.audio(mesin.jalur_contoh(daftar[ia]["berkas"]))
    with c2:
        ib = st.selectbox("Klip B", opsi, index=ia_awal + 1, format_func=fmt); st.audio(mesin.jalur_contoh(daftar[ib]["berkas"]))
    D, jalur, d_dtw, d_euc = mesin.dtw_contoh(daftar[ia]["berkas"], daftar[ib]["berkas"])
    t = np.arange(D.shape[0]) * 0.02
    fig = go.Figure(go.Heatmap(z=D.T, x=t, y=t, colorscale=[[i / 5, c] for i, c in enumerate(tema.RAMP[::-1])], showscale=False, hovertemplate="A detik %{x:.2f} · B detik %{y:.2f}<br>jarak %{z:.1f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[0, t[-1]], y=[0, t[-1]], mode="lines", line=dict(color="#ffffff", width=1.5, dash="dot"), name="tanpa tarik-ulur (Euclid)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[i * 0.02 for i, _ in jalur], y=[j * 0.02 for _, j in jalur], mode="lines", line=dict(color=tema.EMAS, width=3), name="jalur DTW", hoverinfo="skip"))
    tema.gaya(fig, tinggi=440, legenda=True); fig.update_xaxes(title_text="waktu klip A (detik)", showgrid=False, constrain="domain"); fig.update_yaxes(title_text="waktu klip B (detik)", showgrid=False, scaleanchor="x")
    g1, g2 = st.columns([6, 5], gap="medium")
    with g1:
        st.plotly_chart(fig, width="stretch", config=tema.KONFIG)
    with g2:
        sama = daftar[ia]["label"] == daftar[ib]["label"]
        tema.ubin([(angka(d_euc, 1), "jarak tanpa tarik-ulur", "rata-rata per langkah (Euclid)"), (angka(d_dtw, 1), "jarak dengan DTW", "rata-rata per langkah di jalur terbaik")])
        st.markdown(f"Kedua klip ini berasal dari **spesies yang {'sama' if sama else 'berbeda'}**. Warna gelap berarti kedua suara mirip pada pasangan waktu itu. "
                    f"Garis emas adalah penyejajaran terbaik yang ditemukan DTW; makin jauh ia melengkung dari garis putus-putus, makin besar perbedaan temponya.")
        st.caption("Peragaan ini memakai DTW seluruh klip (versi 1) agar mudah dilihat. Di versi 2, yang dicocokkan hanya satu detik paling bersuara, karena sebagian besar kenaikan ternyata datang dari menggeser, bukan menarik-ulur. "
                   "DTW selalu menghasilkan jarak yang sama atau lebih kecil daripada Euclid. Yang berguna untuk menebak spesies adalah apakah jarak ke klip sejenis menjadi lebih kecil daripada jarak ke klip spesies lain. Coba bandingkan dengan memilih klip B dari spesies lain.")
