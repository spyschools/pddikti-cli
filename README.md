# PDDIKTI CLI

Command-line tool (CLI) untuk mengakses data **PDDIKTI** (Pangkalan Data Pendidikan Tinggi, Kemdiktisaintek) lewat terminal. Dibangun di atas library Python [`pddiktipy`](https://pypi.org/project/pddiktipy/) dan mencakup seluruh method yang tersedia: pencarian, detail mahasiswa, dosen, perguruan tinggi, dan program studi, statistik nasional, serta konten situs.

> **Disclaimer:** Proyek ini **tidak resmi** dan tidak berafiliasi dengan PDDIKTI atau Kemdiktisaintek. Seluruh data adalah milik PDDIKTI. Gunakan secara bertanggung jawab dan patuhi ketentuan layanan PDDIKTI. Hasil pencarian mahasiswa dan dosen memuat data pribadi, jadi gunakan hanya untuk keperluan yang sah.

## Fitur

- Pencarian: `all`, `mahasiswa`, `dosen`, `pt`, `prodi`, plus pencarian dengan filter lanjutan
- Detail mahasiswa, dosen (profil, penelitian, pengabdian, karya, paten, riwayat studi dan mengajar)
- Detail perguruan tinggi dan prodi (rasio, biaya, kelulusan, daya tampung, riwayat nama, dan lainnya)
- Statistik nasional (jumlah PT/prodi/dosen/mahasiswa dan sebaran per jenjang, provinsi, akreditasi, dan lainnya)
- Konten situs: berita, pengumuman, publikasi, kegiatan
- Mode interaktif (`menu`) dan output JSON (bisa disimpan ke file)
- Tiga cara melewati Cloudflare (cookie otomatis, cookie manual, proxy solver)

## Instalasi

Dites di Kali Linux. Kali versi baru memblokir `pip install` global (PEP 668), jadi gunakan virtual environment.

```bash
# 1. Siapkan Python
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# 2. Clone repo
git clone https://github.com/spyschools/pddikti-cli.git
cd pddikti-cli

# 3. Buat dan aktifkan virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependensi
pip install -r requirements.txt
```

Isi `requirements.txt`:

```
pddiktipy[auto]
```

## Akses Cloudflare (baca ini dulu)

API PDDIKTI dilindungi **Cloudflare Turnstile**. Request HTTP biasa akan mendapat `403`, jadi kamu perlu menyediakan *clearance* dengan salah satu cara berikut.

### Opsi A: Cookie otomatis (paling mudah)

1. Buka <https://pddikti.kemdiktisaintek.go.id> di Chrome atau Edge dan selesaikan "Verify you are human" sekali.
2. Jalankan dengan `--auto-cookie`:

```bash
python pddikti_cli.py --auto-cookie search all "Universitas Diponegoro"
```

### Opsi B: Cookie manual

1. Lolos pengecekan di browser, lalu buka DevTools (`F12`) → **Application** → **Cookies** → salin nilai `cf_clearance`.
2. Di tab **Network**, salin header `User-Agent` dari salah satu request.

```bash
export CF_CLEARANCE="isi_cookie"
export PDDIKTI_UA="isi_user_agent_browser"
python pddikti_cli.py search pt "Diponegoro"
```

Atau lewat argumen: `--cf-clearance "..." --user-agent "..."`.

### Opsi C: Proxy solver (paling stabil)

Arahkan ke layanan yang menyelesaikan Cloudflare untuk kamu, misalnya proxy berbasis [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr):

```bash
python pddikti_cli.py --base-url http://localhost:8080/api stats count
```

> Cookie `cf_clearance` terikat ke IP dan User-Agent, dan kedaluwarsa sekitar 30 menit.

## Penggunaan

```bash
python pddikti_cli.py [opsi global] <grup> <perintah> [argumen]
```

### Opsi global

| Opsi | Fungsi |
|------|--------|
| `--auto-cookie` | Baca `cf_clearance` dari browser lokal |
| `--cf-clearance` | Nilai cookie manual (atau env `CF_CLEARANCE`) |
| `--user-agent` | User-Agent browser (atau env `PDDIKTI_UA`) |
| `--base-url` | URL proxy solver |
| `--out FILE` | Simpan hasil JSON ke file |
| `--compact` | JSON satu baris |

### Contoh

```bash
python pddikti_cli.py methods                    # daftar semua perintah
python pddikti_cli.py menu                       # mode interaktif

python pddikti_cli.py search mahasiswa "nama"
python pddikti_cli.py pt detail <PT_ID>
python pddikti_cli.py pt prodi <PT_ID> --tahun 2024
python pddikti_cli.py prodi graduation-rate <PRODI_ID>
python pddikti_cli.py dosen profile <DOSEN_ID>

python pddikti_cli.py stats count
python pddikti_cli.py stats pt-provinsi
python pddikti_cli.py site news --page 1 --page-size 5

python pddikti_cli.py --out hasil.json search pt "Bandung"
python pddikti_cli.py search-pt-filter --limit 20 --filter provinsi=Jawa
```

**Alur umum:** jalankan `search` dulu untuk mendapat ID (PT, prodi, dosen, atau mahasiswa), lalu pakai ID itu di perintah detail.

### Daftar perintah

| Grup | Perintah |
|------|----------|
| `search` | `all`, `mahasiswa`, `dosen`, `pt`, `prodi` |
| `mahasiswa` | `detail` |
| `dosen` | `profile`, `penelitian`, `pengabdian`, `karya`, `paten`, `riwayat-studi`, `riwayat-mengajar` |
| `pt` | `detail`, `prodi`, `logo`, `rasio`, `mahasiswa`, `waktu-studi`, `riwayat-nama`, `biaya`, `kelulusan`, `jumlah-prodi`, `jumlah-mahasiswa`, `jumlah-dosen`, `sarpras-nama-file`, `sarpras-blob`, `lokasi` |
| `prodi` | `detail`, `deskripsi`, `riwayat-nama`, `jumlah-mhs-dosen`, `biaya`, `daya-tampung`, `rasio`, `graduation-rate`, `logo`, `homebase`, `hitung-rasio`, `bidang-ilmu` |
| `stats` | `count`, `pt-count`, `prodi-count`, `dosen-count`, `dosen-count-active`, `mahasiswa-count`, `mahasiswa-count-active`, `dosen-*`, `mahasiswa-*`, `pt-*`, `prodi-*` (sebaran data) |
| `site` | `beranda`, `contributor`, `news`, `announcements`, `publications`, `activities`, `activity-detail` |
| lainnya | `search-pt-filter`, `search-prodi-filter`, `methods`, `menu` |

Perintah `pt prodi`, `prodi homebase`, dan `prodi hitung-rasio` mewajibkan opsi `--tahun`.

## Catatan

- Jika sebuah method tidak ada di versi `pddiktipy` yang terpasang, CLI menampilkan pesan error yang jelas dan tidak crash.
- Library mengembalikan `None` saat request gagal. CLI menampilkan ini sebagai pesan error, biasanya karena Cloudflare belum lolos atau input salah.
- Pesan `Could not fetch public IP` saat tidak ada internet hanya warning dan bisa diabaikan.

## Kredit

- [`pddiktipy`](https://github.com/IlhamriSKY/PDDIKTI-kemdikbud-API) oleh [Ilham Riski Wibowo (IlhamriSKY)](https://github.com/IlhamriSKY), lisensi MIT. Library ini adalah fondasi proyek ini.
- Data: [PDDIKTI](https://pddikti.kemdiktisaintek.go.id/), Kemdiktisaintek.

## Lisensi

Didistribusikan di bawah [MIT License](LICENSE). Pastikan juga mematuhi lisensi dan atribusi `pddiktipy`.

## Penulis

[spyschools](https://github.com/spyschools)
