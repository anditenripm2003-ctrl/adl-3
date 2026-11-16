"""Siapkan aset dashboard dari hasil notebook analisis versi 2.

Pakai: python alat/siapkan_aset.py <folder_dataset> <folder_cache_hasil> <folder_ekspor_dashboard>

- <folder_cache_hasil>      berisi emb_birdnet24.npy (embedding BirdNET tiap klip, urutan sama dengan metadata.csv)
- <folder_ekspor_dashboard> keluaran Bagian 8 notebook: hasil.json dan model_birdnet_lr.npz

Yang dibuat di aset/: hasil.json, model_birdnet_lr.npz, metadata.csv (ringkas), dan contoh/ (30 klip + embedding-nya).
Hanya butuh numpy dan pandas.
"""
import sys, os, json, shutil, numpy as np, pandas as pd

DATA, CACHE, EKSPOR = sys.argv[1], sys.argv[2], sys.argv[3]
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aset')
meta = pd.read_csv(os.path.join(DATA, 'metadata.csv'))
labels = sorted(meta['label'].unique())
te = np.where(meta['bagian'].to_numpy() == 'uji')[0]
E = np.load(os.path.join(CACHE, 'emb_birdnet24.npy')); assert len(E) == len(meta)

# 1) Model dan ringkasan hasil: disalin apa adanya dari ekspor notebook
for f in ('hasil.json', 'model_birdnet_lr.npz'):
    shutil.copy(os.path.join(EKSPOR, f), os.path.join(OUT, f))
lama = os.path.join(OUT, 'model_birdnet_svm.joblib')              # model versi 1, tidak dipakai lagi
if os.path.exists(lama): os.remove(lama)
m = np.load(os.path.join(OUT, 'model_birdnet_lr.npz')); assert [str(l) for l in m['labels']] == labels

# 2) Metadata ringkas (untuk halaman data dan peta)
kol = ['spesies', 'nama_ilmiah', 'label', 'bagian', 'id_rekaman', 'seleksi', 'snr_db', 'jenis_suara', 'kualitas_xc', 'perekam', 'lokasi', 'lat', 'lon', 'tanggal', 'lisensi', 'halaman_sumber']
meta[kol].to_csv(os.path.join(OUT, 'metadata.csv'), index=False)

# 3) Klip contoh: dari data UJI, lolos penyaring suara, lisensi tanpa "ND", tiga rekaman berbeda per spesies dengan SNR tertinggi.
#    Dipilih TANPA melihat benar/salahnya tebakan model (aturan sama dengan versi 1).
shutil.rmtree(os.path.join(OUT, 'contoh'), ignore_errors=True); os.makedirs(os.path.join(OUT, 'contoh'))
uji = meta.iloc[te].copy(); uji['idx'] = te
calon = uji[(uji['seleksi'] == 'aktivitas') & (~uji['lisensi'].str.contains('-nd', case=False))]
contoh, emb = [], []
for lab in labels:
    g = calon[calon['label'] == lab].sort_values('snr_db', ascending=False).drop_duplicates('id_rekaman').head(3)
    for k, (_, r) in enumerate(g.iterrows()):
        nama = f'{lab}_{k+1}.wav'; shutil.copy(os.path.join(DATA, r['berkas']), os.path.join(OUT, 'contoh', nama))
        contoh.append(dict(berkas=nama, label=lab, spesies=r['spesies'], id_rekaman=r['id_rekaman'], perekam=r['perekam'], lokasi=r['lokasi'], lisensi=r['lisensi'], halaman_sumber=r['halaman_sumber'], mulai_ms=int(r['mulai_ms'])))
        emb.append(E[r['idx']])
emb = np.stack(emb).astype(np.float32)
json.dump(contoh, open(os.path.join(OUT, 'contoh', 'contoh.json'), 'w'), indent=1); np.save(os.path.join(OUT, 'contoh', 'embedding.npy'), emb)

# 4) Pemeriksaan: model dari berkas .npz pada 30 klip contoh
z = (emb.astype(np.float64) @ m['W'].astype(np.float64).T + m['b']) / float(m['suhu']); pc = z.argmax(1)
print('klip contoh:', len(contoh), '| ditebak benar oleh model dashboard:', int(sum(labels[p] == c['label'] for p, c in zip(pc, contoh))))
print('ukuran aset (KB):', {f: round(os.path.getsize(os.path.join(OUT, f)) / 1e3, 1) for f in sorted(os.listdir(OUT)) if os.path.isfile(os.path.join(OUT, f))})
