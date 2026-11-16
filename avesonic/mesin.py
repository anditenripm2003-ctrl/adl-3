"""Aset, pengolahan audio, dan mesin prediksi (BirdNET 2.4 sebagai pengubah fitur + regresi logistik)."""
import io, json, os, shutil, subprocess, tempfile, threading, urllib.request, warnings, zipfile
import numpy as np
import pandas as pd
import streamlit as st

ASET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "aset")
SR = 16000                      # laju cuplik dataset
KLIP = 3 * SR                   # panjang satu jendela (3 detik)
MAKS_DETIK = 60                 # rekaman unggahan dianalisis paling banyak 60 detik pertama
MAKS_JENDELA = 8                # paling banyak 8 jendela paling "bersuara" yang dianalisis
URL_BIRDNET = "https://zenodo.org/records/15050749/files/BirdNET_v2.4_tflite.zip"
EMB_TENSOR = 545                # keluaran GLOBAL_AVG_POOL (1.024 angka) pada BirdNET 2.4

# Nama Indonesia mengikuti "Daftar nama burung di Indonesia" (Wikipedia bahasa Indonesia).
SPESIES = {
    "common_paradise_kingfisher": ("Cekakak-pita biasa", "Common Paradise Kingfisher", "Tanysiptera galatea"),
    "hair_crested_drongo": ("Srigunting jambul-rambut", "Hair-crested Drongo", "Dicrurus hottentottus"),
    "ivory_breasted_pitta": ("Paok halmahera", "Ivory-breasted Pitta", "Pitta maxima"),
    "mountain_tailorbird": ("Cinenen gunung", "Mountain Tailorbird", "Phyllergates cucullatus"),
    "olive_backed_sunbird": ("Burung-madu sriganti", "Olive-backed Sunbird", "Cinnyris jugularis"),
    "pygmy_cupwing": ("Berencet kerdil", "Pygmy Cupwing", "Pnoepyga pusilla"),
    "red_cheeked_parrot": ("Nuri pipi-merah", "Red-cheeked Parrot", "Geoffroyus geoffroyi"),
    "rusty_breasted_cuckoo": ("Wiwik uncuing", "Rusty-breasted Cuckoo", "Cacomantis sepulcralis"),
    "spangled_drongo": ("Srigunting lencana", "Spangled Drongo", "Dicrurus bracteatus"),
    "sulawesi_bush_warbler": ("Ceret sulawesi", "Sulawesi Bush Warbler", "Locustella castanea"),
}


def nama_id(label):
    return SPESIES[label][0]


# ------------------------------------------------------------------ aset
@st.cache_data(show_spinner=False)
def hasil():
    return json.load(open(os.path.join(ASET, "hasil.json"), encoding="utf-8"))


@st.cache_data(show_spinner=False)
def metadata():
    return pd.read_csv(os.path.join(ASET, "metadata.csv"))


@st.cache_data(show_spinner=False)
def contoh():
    daftar = json.load(open(os.path.join(ASET, "contoh", "contoh.json"), encoding="utf-8"))
    emb = np.load(os.path.join(ASET, "contoh", "embedding.npy"))
    return daftar, emb


def jalur_contoh(berkas):
    return os.path.join(ASET, "contoh", berkas)


@st.cache_data(show_spinner=False)
def baca_wav_contoh(berkas):
    import soundfile as sf
    x, sr = sf.read(jalur_contoh(berkas), dtype="float32")
    return x


@st.cache_resource(show_spinner=False)
def pengklasifikasi():
    """Model akhir analisis versi 2: regresi logistik di atas embedding BirdNET, disimpan sebagai tabel angka biasa.

    Isi berkas: W (10 x 1.024) dan b (standardisasi sudah dilebur ke dalamnya), suhu kalibrasi,
    tabel prior lokasi (wilayah x spesies) beserta kekuatannya (beta).
    """
    d = np.load(os.path.join(ASET, "model_birdnet_lr.npz"))
    return dict(W=d["W"].astype(np.float64), b=d["b"].astype(np.float64), suhu=float(d["suhu"]), prior=d["prior"].astype(np.float64),
                beta=float(d["beta"]), wilayah=[str(w) for w in d["wilayah"]], labels=[str(l) for l in d["labels"]])


def daftar_wilayah():
    return pengklasifikasi()["wilayah"]


# ------------------------------------------------------------------ audio
def muat_audio(data: bytes):
    """Baca berkas audio (WAV/FLAC/OGG/MP3; M4A bila ffmpeg tersedia) -> (mono float32, laju cuplik)."""
    import soundfile as sf
    try:
        x, sr = sf.read(io.BytesIO(data), dtype="float32", always_2d=True)
        return x.mean(axis=1), int(sr)
    except Exception:
        ff = shutil.which("ffmpeg")
        if not ff:
            raise ValueError("Format berkas ini tidak bisa dibaca. Coba WAV, MP3, FLAC, atau OGG.")
        with tempfile.NamedTemporaryFile(suffix=".bin") as f:
            f.write(data); f.flush()
            p = subprocess.run([ff, "-v", "error", "-i", f.name, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
        if p.returncode != 0 or len(p.stdout) < 4:
            raise ValueError("Berkas audio tidak bisa dibaca.")
        return np.frombuffer(p.stdout, dtype=np.float32).copy(), SR


def ke_16k(x, sr):
    if sr == SR:
        return x.astype(np.float32)
    from math import gcd
    from scipy.signal import resample_poly
    g = gcd(int(sr), SR)
    return resample_poly(x, SR // g, int(sr) // g).astype(np.float32)


def energi_pita_db(x, lo=1000, hi=7500, n=400, hop=160):
    """Energi (dB) pita 1-7,5 kHz per frame 25 ms: ukuran kasar "ada suara burung atau tidak"."""
    if len(x) < n:
        x = np.pad(x, (0, n - len(x)))
    nfr = 1 + (len(x) - n) // hop
    idx = np.arange(n)[None, :] + hop * np.arange(nfr)[:, None]
    spek = np.abs(np.fft.rfft(x[idx] * np.hanning(n), axis=1)) ** 2
    f = np.fft.rfftfreq(n, 1 / SR)
    return 10 * np.log10(spek[:, (f >= lo) & (f <= hi)].sum(axis=1) + 1e-12), hop


def pilih_jendela(x):
    """Bagi audio 16 kHz menjadi jendela 3 detik dan pilih yang paling bersuara (aturan sama dengan pembuatan dataset).

    Mengembalikan daftar dict {mulai (detik), aktif (proporsi frame bersuara), dipakai (bool), klip (array)}.
    """
    if len(x) < KLIP:                                   # lebih pendek dari 3 detik: tambah senyap
        x = np.pad(x, (0, KLIP - len(x)))
    e, hop = energi_pita_db(x)
    lantai = np.percentile(e, 20)
    fpw = KLIP // hop
    jendela = []
    for w in range(len(x) // KLIP):
        seg = e[w * fpw:(w + 1) * fpw]
        jendela.append(dict(mulai=w * 3.0, aktif=float((seg > lantai + 10).mean()) if len(seg) else 0.0,
                            puncak=float(np.percentile(seg, 90)) if len(seg) else -120.0, klip=x[w * KLIP:(w + 1) * KLIP]))
    lolos = [j for j in jendela if j["aktif"] >= 0.15]
    kunci = (lambda j: j["aktif"]) if lolos else (lambda j: j["puncak"])
    terpilih = sorted(lolos or jendela, key=kunci, reverse=True)[:MAKS_JENDELA]
    for j in jendela:
        j["dipakai"] = any(j is t for t in terpilih)
    return jendela


def spektrogram(x, n=512, hop=128, fmaks=8000):
    """Spektrogram log (dB) untuk ditampilkan. Mengembalikan (matriks frekuensi x waktu, sumbu waktu, sumbu frekuensi kHz)."""
    if len(x) < n:
        x = np.pad(x, (0, n - len(x)))
    nfr = 1 + (len(x) - n) // hop
    langkah = max(1, nfr // 900)                         # batasi lebar agar ringan di peramban
    idx = np.arange(n)[None, :] + (hop * langkah) * np.arange(nfr // langkah)[:, None]
    S = np.abs(np.fft.rfft(x[idx] * np.hanning(n), axis=1)) ** 2
    f = np.fft.rfftfreq(n, 1 / SR)
    S = S[:, f <= fmaks]
    db = 10 * np.log10(S + 1e-10).T
    db = np.clip(db, np.percentile(db, 99.7) - 62, np.percentile(db, 99.7))
    return db, np.arange(db.shape[1]) * hop * langkah / SR, f[f <= fmaks] / 1000


def gambar_spektrogram(x, tinggi=64):
    """PNG kecil spektrogram (satu warna, terang -> gelap) untuk kartu spesies."""
    from PIL import Image
    db, _, _ = spektrogram(x, n=256, hop=160)
    db = db[::-1]                                         # frekuensi tinggi di atas
    z = (db - db.min()) / max(1e-9, db.max() - db.min())
    ramp = np.array([[255, 255, 255], [221, 232, 223], [169, 205, 184], [95, 165, 131], [46, 125, 91], [18, 55, 42]], dtype=np.float32)
    pos = z * (len(ramp) - 1); i0 = np.floor(pos).astype(int).clip(0, len(ramp) - 2); t = (pos - i0)[..., None]
    rgb = (ramp[i0] * (1 - t) + ramp[i0 + 1] * t).astype(np.uint8)
    return Image.fromarray(rgb).resize((rgb.shape[1], tinggi * 2), Image.BILINEAR)


@st.cache_data(show_spinner=False)
def png_spektrogram_contoh(berkas):
    buf = io.BytesIO(); gambar_spektrogram(baca_wav_contoh(berkas)).save(buf, format="PNG")
    return buf.getvalue()


@st.cache_data(show_spinner=False)
def batang_gelombang(berkas, n=96):
    """Tinggi batang (0-1) dari selubung amplitudo satu klip nyata, untuk hiasan hero."""
    x = np.abs(baca_wav_contoh(berkas))
    b = np.array([seg.max() for seg in np.array_split(x, n)])
    b = np.clip((b - np.percentile(b, 5)) / (b.max() - np.percentile(b, 5) + 1e-9), 0, 1)
    return (0.10 + 0.90 * b ** 0.45).round(3).tolist()


# ------------------------------------------------------------------ BirdNET
def _jalur_model():
    return os.path.join(ASET, "birdnet", "audio-model.tflite")


def model_tersedia():
    return os.path.exists(_jalur_model())


def unduh_model():
    """Unduh model BirdNET 2.4 (sekitar 77 MB, sekali saja) dari Zenodo. Model BirdNET berlisensi CC BY-NC-SA 4.0."""
    tujuan = _jalur_model()
    if os.path.exists(tujuan):
        return tujuan
    os.makedirs(os.path.dirname(tujuan), exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        with urllib.request.urlopen(URL_BIRDNET, timeout=120) as r:
            shutil.copyfileobj(r, tmp)
        zjalur = tmp.name
    try:
        with zipfile.ZipFile(zjalur) as z:
            anggota = next(m for m in z.namelist() if m.endswith("audio-model.tflite"))
            with z.open(anggota) as src, open(tujuan + ".tmp", "wb") as dst:
                shutil.copyfileobj(src, dst)
        os.replace(tujuan + ".tmp", tujuan)
    finally:
        os.remove(zjalur)
    return tujuan


@st.cache_resource(show_spinner=False)
def _penerjemah():
    from ai_edge_litert.interpreter import Interpreter
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        it = Interpreter(model_path=unduh_model(), num_threads=2, experimental_preserve_all_tensors=True)
    it.allocate_tensors()
    return it, it.get_input_details()[0]["index"], threading.Lock()


def embedding(klip16k):
    """Embedding BirdNET (1.024 angka) untuk satu klip 3 detik @16 kHz. Sama persis dengan yang dipakai saat analisis."""
    from scipy.signal import resample
    it, masuk, kunci = _penerjemah()
    x = resample(klip16k.astype(np.float32), 144000).astype(np.float32)[None, :]     # BirdNET bekerja pada 48 kHz
    with kunci:
        it.set_tensor(masuk, x); it.invoke()
        return it.get_tensor(EMB_TENSOR)[0].copy()


def peluang(emb, wilayah=None):
    """emb: (n, 1024) -> peluang (n, 10) sesuai urutan label model.

    Peluang = softmax((W·emb + b) / suhu). Bila `wilayah` diisi, peluang dikalikan prior lokasi^beta lalu dinormalkan ulang.
    """
    m = pengklasifikasi()
    z = (np.atleast_2d(emb).astype(np.float64) @ m["W"].T + m["b"]) / m["suhu"]
    z -= z.max(axis=1, keepdims=True)
    P = np.exp(z); P /= P.sum(axis=1, keepdims=True)
    if wilayah in m["wilayah"]:
        P = P * m["prior"][m["wilayah"].index(wilayah)] ** m["beta"]
        P /= P.sum(axis=1, keepdims=True)
    return P, m["labels"]


def gabung(P):
    """Gabungkan peluang beberapa potongan menjadi satu jawaban: rata-rata log-peluang (sama dengan cara penilaian per rekaman di analisis)."""
    g = np.exp(np.log(np.atleast_2d(P) + 1e-9).mean(axis=0))
    return g / g.sum()


def tebak_audio(x16k):
    """Analisis satu rekaman: pilih jendela, hitung embedding. Mengembalikan (embedding potongan yang dipakai, daftar jendela)."""
    jendela = pilih_jendela(x16k)
    dipakai = [j for j in jendela if j["dipakai"]]
    return np.stack([embedding(j["klip"]) for j in dipakai]), jendela


# ------------------------------------------------------------------ MFCC + DTW (untuk peragaan di halaman hasil)
@st.cache_data(show_spinner=False)
def mfcc_contoh(berkas, n_fft=400, hop=320, n_mel=26, n_mfcc=13):
    """Urutan MFCC (frame 20 ms, 13 koefisien, CMN) satu klip contoh. Implementasi ringkas dengan numpy/scipy."""
    from scipy.fft import dct
    x = baca_wav_contoh(berkas)
    nfr = 1 + (len(x) - n_fft) // hop
    idx = np.arange(n_fft)[None, :] + hop * np.arange(nfr)[:, None]
    P = np.abs(np.fft.rfft(x[idx] * np.hanning(n_fft), axis=1)) ** 2
    f = np.fft.rfftfreq(n_fft, 1 / SR)
    mel = lambda hz: 2595 * np.log10(1 + hz / 700.0)
    tepi = 700 * (10 ** (np.linspace(mel(0), mel(SR / 2), n_mel + 2) / 2595) - 1)
    bank = np.maximum(0, np.minimum((f[None, :] - tepi[:-2, None]) / (tepi[1:-1, None] - tepi[:-2, None]),
                                    (tepi[2:, None] - f[None, :]) / (tepi[2:, None] - tepi[1:-1, None])))
    M = dct(10 * np.log10(P @ bank.T + 1e-10), type=2, axis=1, norm="ortho")[:, :n_mfcc]
    return (M - M.mean(axis=0, keepdims=True)).astype(np.float32)


@st.cache_data(show_spinner=False)
def dtw_contoh(berkas_a, berkas_b, band=30):
    """DTW dua klip contoh. Mengembalikan matriks jarak antarframe, jalur pelengkungan, jarak DTW dan Euclid (rata-rata per langkah)."""
    A, B = mfcc_contoh(berkas_a), mfcc_contoh(berkas_b)
    n, m = len(A), len(B)
    D = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))
    acc = np.full((n + 1, m + 1), np.inf); acc[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(max(1, i - band), min(m, i + band) + 1):
            acc[i, j] = D[i - 1, j - 1] + min(acc[i - 1, j - 1], acc[i - 1, j], acc[i, j - 1])
    i, j, jalur = n, m, []
    while i > 0 and j > 0:
        jalur.append((i - 1, j - 1))
        k = int(np.argmin([acc[i - 1, j - 1], acc[i - 1, j], acc[i, j - 1]]))
        i, j = (i - 1, j - 1) if k == 0 else ((i - 1, j) if k == 1 else (i, j - 1))
    jalur = jalur[::-1]
    return D, jalur, float(acc[n, m] / len(jalur)), float(np.mean(np.diag(D[: min(n, m), : min(n, m)])))
