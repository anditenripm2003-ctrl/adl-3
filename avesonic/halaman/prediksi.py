import hashlib
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from avesonic import tema, mesin
from avesonic.tema import angka, persen


def _tingkat(p):
    """Batas 80% dan 50% sama dengan tiga rentang keyakinan yang diperiksa di data uji (hasil.json: kalibrasi)."""
    if p >= 0.80:
        return "Cukup yakin"
    if p >= 0.50:
        return "Agak yakin"
    return "Ragu-ragu"


def _grafik_spektrogram(x, jendela=None):
    db, t, f = mesin.spektrogram(x)
    fig = go.Figure(go.Heatmap(z=db, x=t, y=f, colorscale=[[i / 5, c] for i, c in enumerate(tema.RAMP)], showscale=False,
                               hovertemplate="detik %{x:.1f} · %{y:.1f} kHz<extra></extra>"))
    for j in jendela or []:
        if j["dipakai"]:
            fig.add_vrect(x0=j["mulai"], x1=min(j["mulai"] + 3, t[-1] if len(t) else 3), line=dict(color=tema.TINTA, width=1.4), fillcolor="rgba(0,0,0,0)", layer="above")
    tema.gaya(fig, tinggi=230, kiri=6)
    fig.update_xaxes(title_text="waktu (detik)", showgrid=False); fig.update_yaxes(title_text="nada (kHz)", showgrid=False)
    return fig


def _tampil_hasil(p, labels, x=None, jendela=None, kebenaran=None, wilayah=None):
    h = mesin.hasil(); kal = h.get("kalibrasi", [])
    urut = np.argsort(-p); top = int(urut[0]); lab = labels[top]; idn, eng, latin = mesin.SPESIES[lab]; yakin = float(p[top])
    st.markdown(f"""
<div class="hasil" aria-live="polite">
  <div class="eyebrow">Tebakan model</div>
  <div class="nama">{idn}</div>
  <div class="latin">{eng} · <i>{latin}</i></div>
  <div class="yakin"><b>{persen(yakin)}</b><span>keyakinan model · {_tingkat(yakin)}</span></div>
  <div class="batang"><i style="width:{max(4, round(100 * yakin))}%"></i></div>
</div>""", unsafe_allow_html=True)

    if kebenaran is not None:
        b_idn = mesin.nama_id(kebenaran)
        if kebenaran == lab:
            st.markdown(f'<div style="margin-top:14px"><span class="lencana baik">{tema.IKON_CEK} Benar. Klip ini memang {b_idn}.</span></div>', unsafe_allow_html=True)
        else:
            posisi = int(np.where(np.array(labels)[urut] == kebenaran)[0][0]) + 1
            st.markdown(f'<div style="margin-top:14px"><span class="lencana kritis">{tema.IKON_SILANG} Belum tepat. Sebenarnya {b_idn} (tebakan ke-{posisi} model).</span></div>', unsafe_allow_html=True)

    k = next((b for b in kal if b["lo"] <= yakin < b["hi"]), None)
    if k:
        tema.catatan(f"<b>Seberapa bisa dipercaya?</b> Pada data uji, tebakan satu potongan dengan keyakinan di rentang ini ({persen(k['lo'])}–{persen(min(k['hi'], 1.0))}) "
                     f"benar pada <b>{persen(k['akurasi'])}</b> dari {angka(k['n'])} klip."
                     + (" Keyakinan serendah ini juga bisa berarti suaranya <b>bukan salah satu dari 10 spesies</b> yang dikenal model." if yakin < 0.50 else ""))
    if wilayah:
        st.caption(f"Tebakan ini memperhitungkan lokasi perekaman ({wilayah}): spesies yang jarang direkam di wilayah itu diturunkan peluangnya.")

    st.markdown('<div class="eyebrow" style="margin-top:26px">Lima kemungkinan teratas</div>', unsafe_allow_html=True)
    lima = urut[:5]
    fig = tema.batang_h([mesin.nama_id(labels[i]) for i in lima], [float(p[i]) for i in lima], [persen(p[i]) for i in lima],
                        [f"<b>{mesin.nama_id(labels[i])}</b><br><i>{mesin.SPESIES[labels[i]][2]}</i><br>keyakinan {persen(p[i], 1)}" for i in lima],
                        tinggi=250, maks=1.14, sorot=[0])
    fig.update_xaxes(tickformat=".0%", tickvals=[0, 0.25, 0.5, 0.75, 1.0])
    st.plotly_chart(fig, width="stretch", config=tema.KONFIG)

    if x is not None:
        st.markdown('<div class="eyebrow" style="margin-top:18px">Potret suaranya (spektrogram)</div>', unsafe_allow_html=True)
        st.plotly_chart(_grafik_spektrogram(x, jendela), width="stretch", config=tema.KONFIG)
    if jendela and len(jendela) > 1:
        dipakai = [j for j in jendela if j["dipakai"]]
        st.caption(f"Rekaman dibagi menjadi {len(jendela)} potongan 3 detik. Kotak hitam menandai {len(dipakai)} potongan paling bersuara yang dianalisis; tebakan akhir adalah gabungan semuanya.")
        keping = "".join(f'<div class="keping"><span class="w">detik {int(j["mulai"])}–{int(j["mulai"]) + 3}</span><b>{mesin.nama_id(labels[int(np.argmax(j["peluang"]))])}</b> · {persen(float(np.max(j["peluang"])))}</div>'
                         for j in sorted(dipakai, key=lambda j: j["mulai"]))
        st.markdown(f'<div class="keping-baris">{keping}</div>', unsafe_allow_html=True)


def _analisis_unggahan(data: bytes, wilayah=None):
    kunci = "hasil_" + hashlib.md5(data).hexdigest()
    if kunci not in st.session_state:
        try:
            x, sr = mesin.muat_audio(data)
        except Exception as e:
            st.error(str(e)); return
        x = mesin.ke_16k(x, sr)
        terpotong = len(x) > mesin.MAKS_DETIK * mesin.SR
        x = x[: mesin.MAKS_DETIK * mesin.SR]
        if len(x) < mesin.SR // 2 or float(np.abs(x).max()) < 1e-4:
            st.error("Rekaman terlalu pendek atau nyaris tanpa suara. Coba rekaman lain yang lebih jelas."); return
        pesan = "Menganalisis suara…" if mesin.model_tersedia() else "Menyiapkan model untuk pertama kali (unduhan sekitar 77 MB), lalu menganalisis…"
        try:
            with st.spinner(pesan):
                emb, jendela = mesin.tebak_audio(x)
        except Exception as e:
            st.error(f"Model belum bisa dijalankan di lingkungan ini ({type(e).__name__}). Klip contoh tetap bisa dicoba."); return
        st.session_state[kunci] = (emb, jendela, x, terpotong)
    emb, jendela, x, terpotong = st.session_state[kunci]
    P, labels = mesin.peluang(emb, wilayah)                       # sidik suara disimpan; lokasi boleh diganti tanpa menghitung ulang
    for j, pj in zip([j for j in jendela if j["dipakai"]], P):
        j["peluang"] = pj
    if terpotong:
        st.caption(f"Rekaman lebih panjang dari {mesin.MAKS_DETIK} detik; hanya {mesin.MAKS_DETIK} detik pertama yang dianalisis.")
    _tampil_hasil(mesin.gabung(P), labels, x=x, jendela=jendela, wilayah=wilayah)


def tampil():
    daftar, emb = mesin.contoh()
    st.markdown('<div class="eyebrow">Coba tebak</div>', unsafe_allow_html=True)
    st.title("Suara burung apa ini?")
    st.markdown("Pilih salah satu klip contoh, unggah rekaman Anda sendiri, atau rekam langsung. Model akan menebak spesiesnya di antara **10 spesies** yang dikenalnya.")

    kiri, kanan = st.columns([5, 7], gap="large")
    with kiri:
        sumber = st.segmented_control("Sumber suara", ["Klip contoh", "Unggah", "Rekam"], default="Klip contoh", label_visibility="collapsed") or "Klip contoh"
        if sumber == "Klip contoh":
            acak = np.random.default_rng(7).permutation(len(daftar)).tolist()
            i = st.selectbox("Pilih klip misteri", acak, format_func=lambda k: f"Klip misteri {acak.index(k) + 1:02d}")
            c = daftar[i]
            st.audio(mesin.jalur_contoh(c["berkas"]))
            st.caption("Dengarkan dulu, tebak sendiri, lalu bandingkan dengan tebakan model. Klip ini berasal dari data uji, jadi model belum pernah mendengarnya saat belajar.")
            tebak = st.button("Tebak spesiesnya", type="primary", width="stretch", key="btn_contoh")
            if tebak:
                st.session_state["contoh_dibuka"] = i
            st.caption(f"Perekam: {c['perekam']} · {c['lokasi']} · [{c['id_rekaman']} di Xeno-canto]({c['halaman_sumber']}) · lisensi [Creative Commons]({c['lisensi']})")
        elif sumber == "Unggah":
            berkas = st.file_uploader("Unggah rekaman suara burung", type=["wav", "mp3", "flac", "ogg", "m4a"], label_visibility="collapsed")
            st.caption("Format WAV, MP3, FLAC, OGG, atau M4A. Rekaman pendek (5–30 detik) dengan suara burung yang jelas memberi hasil terbaik.")
            if berkas is not None:
                st.audio(berkas)
        else:
            berkas = st.audio_input("Rekam suara burung", label_visibility="collapsed")
            st.caption("Izinkan akses mikrofon, lalu rekam beberapa detik. Dekatkan ke sumber suara dan hindari angin.")
        opsi_w = ["Tidak tahu"] + mesin.daftar_wilayah()
        pilih_w = st.selectbox("Direkam di wilayah mana? (opsional)", opsi_w, index=0,
                               help="Bila diisi, model ikut menimbang spesies mana yang biasa direkam di wilayah itu. Bila tidak tahu, biarkan kosong: tebakan hanya dari suara.")
        wilayah = None if pilih_w == "Tidak tahu" else pilih_w
        tema.catatan("<b>Ingat batasannya.</b> Model hanya mengenal 10 spesies. Suara apa pun, termasuk burung lain, ucapan, atau musik, tetap akan ditebak sebagai salah satu dari sepuluh itu. "
                     "Angka keyakinan yang rendah adalah tanda untuk tidak mempercayai tebakannya, tetapi keyakinan tinggi pun bukan jaminan.")

    with kanan:
        if sumber == "Klip contoh":
            if st.session_state.get("contoh_dibuka") == i:
                P, labels = mesin.peluang(emb[i], wilayah)
                _tampil_hasil(P[0], labels, x=mesin.baca_wav_contoh(c["berkas"]), kebenaran=c["label"], wilayah=wilayah)
            else:
                st.markdown('<div class="kartu" style="min-height:240px;display:flex;flex-direction:column;justify-content:center"><div class="no">MENUNGGU</div><h3>Dengarkan klipnya, lalu tekan "Tebak spesiesnya".</h3><p>Hasil tebakan, tingkat keyakinan, dan potret suaranya akan muncul di sini.</p></div>', unsafe_allow_html=True)
        elif berkas is not None:
            _analisis_unggahan(berkas.getvalue(), wilayah)
        else:
            st.markdown('<div class="kartu" style="min-height:240px;display:flex;flex-direction:column;justify-content:center"><div class="no">MENUNGGU</div><h3>Belum ada suara untuk dianalisis.</h3><p>Unggah atau rekam suara di sebelah kiri. Analisis biasanya selesai dalam beberapa detik.</p></div>', unsafe_allow_html=True)
