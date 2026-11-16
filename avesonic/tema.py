"""Tema visual AVESONIC: token warna, CSS global, komponen HTML kecil, dan gaya grafik Plotly."""
import streamlit as st
import plotly.graph_objects as go

# --- Token ---------------------------------------------------------------
HIJAU = "#12372A"       # hijau tua: judul, sidebar, kartu gelap
TEAL = "#164E63"
EMAS = "#D6A84B"        # aksen
LANGIT = "#6CB4C8"
KRIM = "#F7F4EA"
TINTA = "#12372A"
TINTA2 = "#3d4f47"
REDUP = "#5C6F66"
GARIS = "#E6E3D4"
DATA = "#2E7D5B"        # satu warna data
DATA_PUCAT = "#b5d2c2"
BAIK, KRITIS = "#2E7D5B", "#b3412f"
RAMP = ["#ffffff", "#DDE8DF", "#a9cdb8", "#5fa583", "#2E7D5B", "#12372A"]   # sekuensial: terang -> gelap

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap');

:root{
  --hijau:#12372A; --teal:#164E63; --emas:#D6A84B; --langit:#6CB4C8; --krim:#F7F4EA; --tinta2:#3d4f47; --redup:#5C6F66; --garis:#E6E3D4; --garis2:#DAD9CC; --data:#2E7D5B;
  --ease-out:cubic-bezier(0.23,1,0.32,1);
  --serif:'Fraunces',Georgia,serif; --badan:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
}
html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button{ font-family:var(--badan); }
.stApp{ background:#ffffff; color:var(--hijau); }
.block-container{ max-width:1180px; padding-top:2.4rem; padding-bottom:4rem; }
h1,h2,h3,h4{ font-family:var(--serif) !important; color:var(--hijau); letter-spacing:-0.01em; }
h1{ font-size:2.5rem !important; font-weight:700 !important; padding-bottom:0.2rem !important; text-wrap:balance; }
p, li{ color:var(--redup); line-height:1.6; }
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stMainMenu"], [data-testid="stAppDeployButton"], [data-testid="stToolbarActions"]{ display:none !important; }
[data-testid="stHeader"]{ background:transparent; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"]{ background:linear-gradient(180deg,#12372A 0%,#0E2B21 100%); }
section[data-testid="stSidebar"] *{ color:var(--krim); }
[data-testid="stSidebarNav"] a{ border-radius:10px; margin:2px 6px; padding:7px 12px; transition:background-color 160ms ease; }
[data-testid="stSidebarNav"] a span{ color:rgba(247,244,234,0.82); font-weight:500; font-size:0.95rem; }
[data-testid="stSidebarNav"] a:hover{ background:rgba(247,244,234,0.08); }
[data-testid="stSidebarNav"] a[aria-current="page"]{ background:rgba(214,168,75,0.18); }
[data-testid="stSidebarNav"] a[aria-current="page"] span{ color:var(--emas); font-weight:600; }
[data-testid="stLogo"]{ height:2.9rem; }
.sb-garis{ border-top:1px solid rgba(247,244,234,0.35); margin:1.2rem 0.4rem 1.4rem; }
.sb-tag{ font-size:0.72rem; letter-spacing:0.18em; text-transform:uppercase; color:var(--langit) !important; padding:0 0.4rem 0.6rem; }
.sb-alur{ font-size:0.8rem; color:rgba(247,244,234,0.78) !important; padding:0 0.4rem 1rem; }
.sb-note{ font-size:0.78rem; line-height:1.5; color:rgba(247,244,234,0.6) !important; padding:0 0.4rem; }

/* ---- Hero ---- */
.hero{ background:radial-gradient(1200px 400px at 85% -10%, rgba(108,180,200,0.28), transparent 60%), linear-gradient(135deg,#12372A 0%,#164E63 100%);
  border-radius:26px; padding:3rem 3rem 2.6rem; color:var(--krim); display:grid; grid-template-columns:1.15fr 1fr; gap:2rem; align-items:center; overflow:hidden; }
.hero .brand{ font-family:var(--serif); font-size:4rem; font-weight:700; letter-spacing:0.06em; line-height:1; color:var(--krim); }
.hero .tagline{ color:var(--emas); letter-spacing:0.32em; text-transform:uppercase; font-size:0.82rem; font-weight:600; margin:0.9rem 0 0.2rem; }
.hero .sub{ color:var(--langit); font-size:1.05rem; font-weight:500; margin-bottom:1.1rem; }
.hero .lead{ font-family:var(--serif); font-size:1.45rem; line-height:1.35; color:var(--krim); margin-bottom:0.8rem; text-wrap:balance; }
.hero .desc{ color:rgba(247,244,234,0.78); font-size:0.98rem; line-height:1.6; max-width:34rem; margin:0; }
.hero svg{ width:100%; height:auto; overflow:visible; }
.bar-anim{ transform-box:fill-box; transform-origin:center; animation:denyut 2.8s ease-in-out infinite; }
@keyframes denyut{ 0%,100%{ transform:scaleY(0.55); } 50%{ transform:scaleY(1); } }
.ombak{ animation:hanyut 7s ease-in-out infinite; }
@keyframes hanyut{ 0%,100%{ transform:translateX(0); } 50%{ transform:translateX(-14px); } }
.daun{ transform-box:fill-box; transform-origin:20% 90%; animation:ayun 5.6s ease-in-out infinite; }
@keyframes ayun{ 0%,100%{ transform:rotate(-3deg); } 50%{ transform:rotate(4deg); } }

/* ---- Tipografi halaman ---- */
.eyebrow{ font-size:0.74rem; letter-spacing:0.22em; text-transform:uppercase; color:var(--data); font-weight:700; }
.judul-bagian{ border-left:4px solid var(--emas); padding:0.2rem 0 0.2rem 1rem; margin:2.6rem 0 0.9rem; }
.judul-bagian h2{ font-family:var(--serif); font-size:1.45rem !important; color:var(--hijau); font-weight:600; margin:0; padding:0; text-wrap:balance; }
.judul-bagian p{ color:var(--redup); font-size:0.95rem; margin:0.15rem 0 0; max-width:65ch; }

/* ---- Strip angka ---- */
.ubin-baris{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:0; margin:1.6rem 0 0.4rem; border-top:1px solid var(--garis2); border-bottom:1px solid var(--garis2); }
.ubin{ padding:1.1rem 1rem; border-right:1px solid var(--garis2); } .ubin:last-child{ border-right:none; }
.ubin .angka{ font-family:var(--serif); font-size:2.3rem; font-weight:700; color:var(--hijau); line-height:1.1; font-variant-numeric:tabular-nums; }
.ubin .label{ font-size:0.78rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--redup); margin-top:0.2rem; }
.ubin .catatan{ font-size:0.8rem; color:var(--redup); margin-top:0.25rem; opacity:0.85; }

/* ---- Kartu ---- */
.kartu-baris{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; margin-top:1rem; }
.kartu{ background:#ffffff; border:1px solid var(--garis); border-radius:18px; padding:1.3rem 1.4rem; }
.kartu .no{ font-size:0.72rem; letter-spacing:0.2em; color:var(--emas); font-weight:700; }
.kartu h3{ font-family:var(--serif); font-size:1.2rem !important; margin:0.3rem 0 0.4rem; padding:0; color:var(--hijau); font-weight:600; line-height:1.25; text-wrap:balance; }
.kartu p{ color:var(--redup); font-size:0.93rem; line-height:1.55; margin:0; }
.kartu .besar{ font-family:var(--serif); font-size:2.4rem; font-weight:700; color:var(--hijau); line-height:1.1; font-variant-numeric:tabular-nums; margin:0.7rem 0 0.3rem; }
.kartu .besar small{ font-family:var(--badan); font-size:0.74rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--redup); font-weight:500; }
.kartu.gelap{ background:linear-gradient(145deg,#12372A,#164E63); border:none; }
.kartu.gelap h3, .kartu.gelap .besar{ color:var(--krim); } .kartu.gelap p{ color:rgba(247,244,234,0.8); } .kartu.gelap .besar small{ color:var(--langit); }
.kartu.emas{ background:#FBF3DE; border:1px solid #EAD59B; }
.kartu.sage{ background:#DDE8DF; border:none; }

/* ---- Langkah ---- */
.langkah{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:0; margin-top:1rem; background:#ffffff; border:1px solid var(--garis); border-radius:18px; overflow:hidden; }
.langkah > div{ padding:1.3rem 1.4rem; border-right:1px solid var(--garis); } .langkah > div:last-child{ border-right:0; }
.langkah .eyebrow{ color:var(--emas); letter-spacing:0.2em; font-size:0.72rem; }
.langkah b{ display:block; font-family:var(--serif); font-size:1.12rem; color:var(--hijau); margin:0.3rem 0 0.35rem; font-weight:600; }
.langkah span{ color:var(--redup); font-size:0.93rem; line-height:1.55; }

/* ---- Spesies ---- */
.spesies{ background:#ffffff; border:1px solid var(--garis); border-radius:18px; padding:1rem 1rem 0.9rem; min-height:178px; display:flex; flex-direction:column; }
.spesies .nama{ font-family:var(--serif); font-weight:600; font-size:1.05rem; color:var(--hijau); line-height:1.2; }
.spesies .latin{ font-style:italic; color:var(--redup); font-size:0.8rem; margin-top:2px; }
.spesies .inggris{ color:var(--tinta2); font-size:0.8rem; }
.spesies .jml{ margin-top:auto; padding-top:10px; font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--data); font-weight:600; white-space:nowrap; font-variant-numeric:tabular-nums; }

/* ---- Hasil prediksi ---- */
.hasil{ background:radial-gradient(700px 260px at 90% -20%, rgba(108,180,200,0.26), transparent 60%), linear-gradient(135deg,#12372A 0%,#164E63 100%); border-radius:22px; padding:1.8rem 1.8rem 1.6rem; color:var(--krim); }
.hasil .eyebrow{ color:var(--emas); }
.hasil .nama{ font-family:var(--serif); font-size:clamp(1.9rem,4vw,2.6rem); font-weight:700; color:var(--krim); line-height:1.08; margin:0.6rem 0 0.25rem; }
.hasil .latin{ color:var(--langit); font-size:0.95rem; } .hasil .latin i{ color:rgba(247,244,234,0.9); }
.hasil .yakin{ display:flex; align-items:baseline; gap:10px; margin-top:1.3rem; }
.hasil .yakin b{ font-family:var(--serif); font-size:3rem; font-weight:700; color:var(--krim); font-variant-numeric:tabular-nums; line-height:1; }
.hasil .yakin span{ color:rgba(247,244,234,0.78); font-size:0.95rem; }
.hasil .batang{ height:8px; border-radius:99px; background:rgba(247,244,234,0.16); margin-top:0.9rem; overflow:hidden; }
.hasil .batang i{ display:block; height:100%; border-radius:99px; background:linear-gradient(90deg,#6CB4C8,#D6A84B); transform-origin:left center; animation:isi 520ms var(--ease-out) both; }
@keyframes isi{ from{ transform:scaleX(0.2); opacity:0.4; } to{ transform:scaleX(1); opacity:1; } }
.lencana{ display:inline-flex; align-items:center; gap:7px; padding:6px 12px; border-radius:99px; font-size:0.86rem; font-weight:500; border:1px solid var(--garis); background:#ffffff; color:var(--hijau); }
.lencana.baik svg{ color:#2E7D5B; } .lencana.kritis svg{ color:#b3412f; }
.keping-baris{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }
.keping{ border-radius:99px; background:#DDE8DF; padding:6px 14px; font-size:0.84rem; color:var(--tinta2); }
.keping b{ color:var(--hijau); font-weight:600; } .keping .w{ font-size:0.72rem; color:var(--redup); margin-right:8px; font-variant-numeric:tabular-nums; }

/* ---- Catatan ---- */
.catatan-kotak{ background:#DDE8DF; border-radius:14px; padding:1rem 1.1rem; color:var(--tinta2); font-size:0.95rem; line-height:1.6; margin-top:0.9rem; }
.catatan-kotak b{ color:var(--hijau); }
.pecahan{ display:flex; height:40px; border-radius:12px; overflow:hidden; gap:2px; margin-top:0.9rem; }
.pecahan > div{ display:flex; align-items:center; padding:0 14px; font-size:0.85rem; font-weight:600; white-space:nowrap; font-variant-numeric:tabular-nums; }
.kaki{ margin-top:3.4rem; padding-top:1.2rem; border-top:1px solid var(--garis2); color:var(--redup); font-size:0.82rem; }

/* ---- Komponen Streamlit ---- */
.stButton > button, .stDownloadButton > button, [data-testid="stPageLink"] a{ border-radius:12px; font-weight:600; transition:transform 160ms var(--ease-out), background-color 160ms ease, border-color 160ms ease; }
.stButton > button:active, [data-testid="stPageLink"] a:active{ transform:scale(0.97); }
.stButton > button p, .stDownloadButton > button p, [data-testid="stPageLink"] a p{ color:inherit; }
.stButton > button[kind="primary"]{ background:var(--hijau); border-color:var(--hijau); color:var(--krim); padding:0.6rem 1rem; }
.stButton > button[kind="primary"]:hover{ background:#1a4a39; border-color:#1a4a39; color:var(--krim); }
[data-testid="stPageLink"] a{ background:#ffffff; border:1px solid var(--garis); padding:10px 16px; color:var(--hijau); }
[data-testid="stPageLink"] a:hover{ border-color:var(--emas); background:#FBF3DE; }
[data-testid="stImage"] img{ border:1px solid var(--garis); border-radius:12px; display:block; }
[data-testid="stAudio"] audio{ height:38px; }
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"]{ background:#ffffff; border:1px solid var(--garis); border-radius:18px; padding:8px; }
[data-testid="stExpander"] details{ border-radius:14px; border-color:var(--garis); background:#ffffff; }
[data-testid="stFileUploaderDropzone"]{ border-radius:14px; background:#ffffff; }
@media (prefers-reduced-motion: reduce){ .bar-anim, .ombak, .daun, .hasil .batang i{ animation:none !important; } .stButton > button, [data-testid="stPageLink"] a{ transition:none; } }
@media (max-width:900px){ .hero{ grid-template-columns:1fr; padding:2rem; } .hero .brand{ font-size:2.8rem; } .langkah > div{ border-right:0; border-bottom:1px solid var(--garis); } .ubin{ border-bottom:1px solid var(--garis2); } }
</style>
"""

IKON_CEK = '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8.5l3.2 3.2L13 4.8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
IKON_SILANG = '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'


def pasang_css():
    st.markdown(CSS, unsafe_allow_html=True)


def angka(x, desimal=0):
    """Format angka gaya Indonesia: 7.171 ; 0,82."""
    s = f"{x:,.{desimal}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def persen(x, desimal=0):
    return angka(100 * x, desimal) + "%"


def kepala(eyebrow, judul, lede=""):
    """Kepala halaman: label kecil, judul besar, kalimat pembuka."""
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(judul)
    if lede:
        st.markdown(f'<p style="font-size:1.08rem;max-width:46rem;margin:-0.3rem 0 1.2rem">{lede}</p>', unsafe_allow_html=True)


def judul_bagian(eyebrow, judul, teks=""):
    st.markdown(f'<div class="judul-bagian"><h2>{judul}</h2>{"<p>" + teks + "</p>" if teks else ""}</div>', unsafe_allow_html=True)


def ubin(butir):
    """butir: daftar (angka, label, catatan)."""
    isi = "".join(f'<div class="ubin"><div class="angka">{a}</div><div class="label">{l}</div>{"<div class=catatan>" + c + "</div>" if c else ""}</div>' for a, l, c in butir)
    st.markdown(f'<div class="ubin-baris">{isi}</div>', unsafe_allow_html=True)


def catatan(html):
    st.markdown(f'<div class="catatan-kotak">{html}</div>', unsafe_allow_html=True)


def sidebar():
    st.sidebar.markdown('<div class="sb-garis"></div><div class="sb-tag">Dengar · Ukur · Kenali</div>'
                        '<div class="sb-alur">Kenali data → Coba tebak → Lihat hasil</div>'
                        '<div class="sb-note">Alat bantu identifikasi berbasis pola suara. Bukan pengganti identifikasi oleh ahli.</div>', unsafe_allow_html=True)


def kaki():
    st.markdown('<div class="kaki">AVESONIC · Tugas Data Mining, Institut Teknologi Sepuluh Nopember · Rekaman bersumber dari Xeno-canto dan tetap milik perekamnya masing-masing (lisensi Creative Commons).</div>', unsafe_allow_html=True)


def svg_hero(tinggi_batang):
    """Ilustrasi hero: batang gelombang (dari klip nyata) yang berdenyut, garis ombak, dan sehelai daun emas."""
    n = len(tinggi_batang); lebar, jarak, x0, tengah = 5.2, 10.4, 18, 158
    batang = []
    for i, b in enumerate(tinggi_batang):
        t = 22 + 150 * b; warna = "#D6A84B" if i % 9 == 4 else "#6CB4C8"
        batang.append(f'<rect class="bar-anim" x="{x0 + i * jarak:.1f}" y="{tengah - t / 2:.1f}" width="{lebar}" height="{t:.1f}" rx="2.6" fill="{warna}" opacity="{0.95 if warna == "#D6A84B" else 0.78}" style="animation-delay:{-(i % 11) * 0.26:.2f}s"/>')
    L = x0 + n * jarak
    ombak = "M 18 272 " + " ".join(f"Q {18 + (k * 2 + 1) * 24} {272 + (22 if k % 2 == 0 else -22) * (1 - abs(k - 4) / 6):.0f} {18 + (k + 1) * 48} 272" for k in range(int((L - 18) // 48)))
    return (f'<svg viewBox="0 0 {L + 30:.0f} 300" role="img" aria-label="Ilustrasi gelombang suara burung yang bergerak">'
            + "".join(batang)
            + f'<g class="ombak"><path d="{ombak}" fill="none" stroke="#F7F4EA" stroke-opacity="0.75" stroke-width="2" stroke-linecap="round"/></g>'
            + f'<g transform="translate({L - 104:.0f} 6)"><g class="daun"><path d="M6 78 C 10 34, 44 6, 96 2 C 94 48, 62 82, 6 78 Z" fill="#D6A84B"/><path d="M8 76 C 34 52, 62 28, 94 4" fill="none" stroke="#12372A" stroke-opacity="0.45" stroke-width="2"/></g></g>'
            + "</svg>")


# --- Plotly -------------------------------------------------------------
FONT = "Inter, system-ui, sans-serif"
KONFIG = {"displayModeBar": False, "responsive": True}


def gaya(fig, tinggi=380, kiri=10, legenda=False):
    fig.update_layout(
        height=tinggi, margin=dict(l=kiri, r=18, t=16, b=14), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=13, color=TINTA2), showlegend=legenda,
        hoverlabel=dict(bgcolor="#ffffff", bordercolor=GARIS, font=dict(family=FONT, size=13, color=TINTA)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=TINTA2)),
    )
    fig.update_xaxes(gridcolor=GARIS, zeroline=False, linecolor=GARIS, tickfont=dict(color=REDUP), title_font=dict(color=REDUP, size=12))
    fig.update_yaxes(gridcolor=GARIS, zeroline=False, linecolor=GARIS, tickfont=dict(color=TINTA2), title_font=dict(color=REDUP, size=12))
    return fig


def batang_h(nama, nilai, teks, hover, tinggi=None, maks=None, bawah=None, atas=None, judul_x="", sorot=None):
    """Batang horizontal satu warna dengan label langsung di ujungnya. `sorot`: indeks batang yang ditonjolkan."""
    n = len(nama)
    warna = [DATA if (sorot is None or i in sorot) else DATA_PUCAT for i in range(n)]
    fig = go.Figure(go.Bar(
        y=nama, x=nilai, orientation="h", marker=dict(color=warna, cornerradius=4), width=0.62,
        text=teks, textposition="outside", textfont=dict(color=TINTA, size=13, family=FONT), cliponaxis=False,
        customdata=hover, hovertemplate="%{customdata}<extra></extra>",
        error_x=None if bawah is None else dict(type="data", symmetric=False, array=[a - v for a, v in zip(atas, nilai)], arrayminus=[v - b for b, v in zip(bawah, nilai)], color=TINTA, thickness=1.3, width=4),
    ))
    if bawah is not None:
        fig.update_traces(textposition="none")
        for y, a, t in zip(nama, atas, teks):
            fig.add_annotation(x=a, y=y, text=f"<b>{t}</b>", showarrow=False, xanchor="left", xshift=8, font=dict(color=TINTA, size=13, family=FONT))
    gaya(fig, tinggi or (70 + 44 * n))
    fig.update_layout(margin=dict(r=44))
    fig.update_yaxes(autorange="reversed", showgrid=False, ticksuffix="  ")
    fig.update_xaxes(range=[0, maks] if maks else None, title_text=judul_x)
    return fig
