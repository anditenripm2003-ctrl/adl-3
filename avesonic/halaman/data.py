import plotly.graph_objects as go
import streamlit as st
from avesonic import tema, mesin
from avesonic.tema import angka, persen


def tampil():
    h = mesin.hasil(); meta = mesin.metadata(); daftar, _ = mesin.contoh()
    st.markdown('<div class="eyebrow">Kenali datanya</div>', unsafe_allow_html=True)
    st.title("Sepuluh suara dari hutan dan pekarangan Indonesia")
    st.markdown(f"Dataset ini berisi **{angka(h['n_klip'])} klip suara berdurasi 3 detik**, dipotong dari {angka(h['n_rekaman'])} rekaman lapangan di Xeno-canto, "
                f"arsip suara burung terbuka yang diisi oleh relawan dan peneliti. Semua rekaman diambil di Indonesia oleh {h['n_perekam']} perekam berbeda.")

    # ---------------------------------------------------------------- galeri
    tema.judul_bagian("Spesies", "Dengarkan kesepuluh spesiesnya",
                      "Gambar hijau di tiap kartu adalah spektrogram: \"potret\" suara, dengan waktu ke kanan dan nada makin tinggi ke atas. Tiap spesies punya pola yang khas.")
    per = meta.groupby("label").agg(klip=("label", "size"), rekaman=("id_rekaman", "nunique"))
    urut = per.sort_values("klip", ascending=False).index.tolist()
    for baris in (urut[:5], urut[5:]):
        kol = st.columns(5, gap="small")
        for k, lab in zip(kol, baris):
            idn, eng, latin = mesin.SPESIES[lab]
            c = next(x for x in daftar if x["label"] == lab)
            with k:
                st.markdown(f'<div class="spesies"><div class="nama">{idn}</div><div class="latin">{latin}</div><div class="inggris">{eng}</div>'
                            f'<div class="jml">{angka(per.loc[lab, "klip"])} klip · {per.loc[lab, "rekaman"]} rekaman</div></div>', unsafe_allow_html=True)
                st.image(mesin.png_spektrogram_contoh(c["berkas"]), width="stretch")
                st.audio(mesin.jalur_contoh(c["berkas"]))
                st.caption(f"Perekam: {c['perekam']} · [{c['id_rekaman']}]({c['halaman_sumber']})")

    # ---------------------------------------------------------------- komposisi
    tema.judul_bagian("Komposisi", "Seberapa banyak data tiap spesies?",
                      "Jumlahnya tidak sama: spesies terbanyak punya lebih dari tiga kali klip spesies tersedikit. Karena itu hasil model dilaporkan per spesies, bukan hanya rata-ratanya.")
    satuan = st.segmented_control("Hitung berdasarkan", ["Klip", "Rekaman"], default="Klip", label_visibility="collapsed")
    kol_nilai = "klip" if satuan != "Rekaman" else "rekaman"
    p = per.sort_values(kol_nilai, ascending=False)
    bagi = meta.pivot_table(index="label", columns="bagian", values="spesies", aggfunc="count").reindex(p.index)
    hover = [f"<b>{mesin.nama_id(l)}</b><br>{angka(p.loc[l, 'klip'])} klip dari {p.loc[l, 'rekaman']} rekaman<br>"
             f"latih {angka(bagi.loc[l, 'latih'])} · validasi {angka(bagi.loc[l, 'validasi'])} · uji {angka(bagi.loc[l, 'uji'])}" for l in p.index]
    fig = tema.batang_h([mesin.nama_id(l) for l in p.index], p[kol_nilai].tolist(), [angka(v) for v in p[kol_nilai]], hover, maks=p[kol_nilai].max() * 1.14,
                        judul_x=f"jumlah {kol_nilai}")
    st.plotly_chart(fig, width="stretch", config=tema.KONFIG)

    # ---------------------------------------------------------------- peta
    tema.judul_bagian("Lokasi", "Di mana suara-suara ini direkam?",
                      "Tiap titik adalah satu lokasi perekaman. Makin besar titiknya, makin banyak klip dari lokasi itu.")
    pilihan = ["Semua spesies"] + [mesin.nama_id(l) for l in urut]
    pilih = st.selectbox("Tampilkan spesies", pilihan, label_visibility="collapsed")
    m = meta.dropna(subset=["lat", "lon"])
    if pilih != "Semua spesies":
        m = m[m["label"] == urut[pilihan.index(pilih) - 1]]
    g = m.groupby(["lat", "lon"]).agg(klip=("label", "size"), lokasi=("lokasi", "first"), spesies=("label", lambda s: ", ".join(sorted({mesin.nama_id(x) for x in s})))).reset_index()
    fig = go.Figure(go.Scattermap(
        lat=g["lat"], lon=g["lon"], mode="markers",
        marker=dict(size=(6 + 3.2 * g["klip"] ** 0.5).clip(upper=34), color=tema.DATA, opacity=0.62),
        customdata=g[["lokasi", "klip", "spesies"]].values,
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} klip<br>%{customdata[2]}<extra></extra>"))
    fig.update_layout(map=dict(style="carto-positron", center=dict(lat=-2.3, lon=119.5), zoom=3.6), height=470, margin=dict(l=0, r=0, t=0, b=0),
                      hoverlabel=dict(bgcolor="#ffffff", bordercolor=tema.GARIS, font=dict(family=tema.FONT, size=13, color=tema.TINTA)))
    st.plotly_chart(fig, width="stretch", config=tema.KONFIG)
    st.caption(f"{angka(len(g))} lokasi · {angka(len(m))} klip ditampilkan. Peta dasar: © CARTO, © OpenStreetMap contributors.")

    # ---------------------------------------------------------------- pembagian & kualitas
    tema.judul_bagian("Pembagian data", "Belajar, berlatih soal, lalu ujian",
                      "Seperti murid, model tidak boleh diuji dengan soal yang sama dengan latihannya. Klip dibagi tiga, dan klip dari satu sesi rekaman (perekam, tanggal, dan lokasi yang sama) selalu masuk ke bagian yang sama.")
    n = h["n_klip"]
    st.markdown(f"""
<div class="pecahan" role="img" aria-label="Pembagian data: latih {h['n_latih']}, validasi {h['n_validasi']}, uji {h['n_uji']}">
  <div style="flex:{h['n_latih']};background:#12372A;color:#F7F4EA">Latih · {angka(h['n_latih'])} klip ({persen(h['n_latih'] / n)})</div>
  <div style="flex:{h['n_validasi']};background:#2E7D5B;color:#ffffff">Validasi · {angka(h['n_validasi'])}</div>
  <div style="flex:{h['n_uji']};background:#DDE8DF;color:#12372A">Uji · {angka(h['n_uji'])}</div>
</div>""", unsafe_allow_html=True)
    st.markdown("""
<div class="langkah">
  <div><div class="eyebrow">Latih</div><b>Bahan belajar</b><span>Model mempelajari ciri suara tiap spesies dari klip ini.</span></div>
  <div><div class="eyebrow">Validasi</div><b>Latihan soal</b><span>Bersama data latih, dipakai untuk memilih pengaturan terbaik tiap metode, lalu ikut menjadi bahan belajar model akhir.</span></div>
  <div><div class="eyebrow">Uji</div><b>Ujian akhir</b><span>Tidak dipakai untuk memilih apa pun. Angka hasil utama di dashboard ini berasal dari sini.</span></div>
</div>""", unsafe_allow_html=True)

    tema.judul_bagian("Kualitas klip", "Tidak semua klip sama jernihnya",
                      "Klip dipilih otomatis oleh komputer berdasarkan kerasnya suara di rentang nada burung, tanpa didengarkan satu per satu oleh manusia.")
    na = int((meta["seleksi"] == "aktivitas").sum()); nc = int((meta["seleksi"] == "cadangan").sum())
    tema.ubin([
        (angka(na), "klip \"jelas\"", f"{persen(na / n)} · suara burung menonjol dari latar"),
        (angka(nc), "klip \"cadangan\"", f"{persen(nc / n)} · suara terus-menerus, sangat sunyi, atau bernada di luar 1–7,5 kHz"),
        (angka(meta["snr_db"].median(), 1).replace(".", ",") + " dB", "median kejernihan", "perkiraan kasar selisih suara dan derau"),
    ])
    tema.catatan("<b>Mengapa ini penting?</b> Sebagian klip bisa berisi suara burung lain di latar, atau hanya derau. Pengaruhnya terhadap ketepatan model ditunjukkan di halaman Hasil Analisis.")

    with st.expander("Lihat tabel data mentah"):
        st.dataframe(meta[["spesies", "nama_ilmiah", "bagian", "id_rekaman", "seleksi", "snr_db", "jenis_suara", "perekam", "lokasi", "tanggal", "lisensi"]], width="stretch", height=360, hide_index=True)
