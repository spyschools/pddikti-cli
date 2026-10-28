#!/usr/bin/env python3
"""
pddikti_cli.py - CLI untuk semua fitur library `pddiktipy` (PDDIKTI, unofficial).

Contoh:
  python pddikti_cli.py search all "Universitas Diponegoro"
  python pddikti_cli.py search mahasiswa "nama mahasiswa"
  python pddikti_cli.py pt detail <PT_ID>
  python pddikti_cli.py pt prodi <PT_ID> --tahun 2024
  python pddikti_cli.py prodi graduation-rate <PRODI_ID>
  python pddikti_cli.py dosen profile <DOSEN_ID>
  python pddikti_cli.py stats count
  python pddikti_cli.py stats dosen-jenjang
  python pddikti_cli.py site news --page 1 --page-size 5
  python pddikti_cli.py methods            # daftar semua method yang tersedia
  python pddikti_cli.py menu               # mode interaktif

Akses Cloudflare (pilih salah satu):
  --auto-cookie                          baca cf_clearance dari browser lokal
  --cf-clearance XXX --user-agent "UA"   cookie manual (atau env CF_CLEARANCE / PDDIKTI_UA)
  --base-url http://localhost:8080/api   proxy solver (mis. FlareSolverr)
"""

import argparse
import inspect
import json
import os
import sys

try:
    from pddiktipy import api
except ImportError:
    sys.exit("pddiktipy belum terpasang. Jalankan: pip install 'pddiktipy[auto]'")

# ---------------------------------------------------------------------------
# Peta perintah -> nama method di pddiktipy
# Format: grup -> {subperintah: (method, [argumen posisional], [opsi])}
# Argumen: "id" = ID wajib, "keyword" = kata kunci. Opsi: "tahun".
# ---------------------------------------------------------------------------
COMMANDS = {
    "search": {
        "all": ("search_all", ["keyword"], []),
        "mahasiswa": ("search_mahasiswa", ["keyword"], []),
        "dosen": ("search_dosen", ["keyword"], []),
        "pt": ("search_pt", ["keyword"], []),
        "prodi": ("search_prodi", ["keyword"], []),
    },
    "mahasiswa": {
        "detail": ("get_detail_mhs", ["id"], []),
    },
    "dosen": {
        "profile": ("get_dosen_profile", ["id"], []),
        "penelitian": ("get_dosen_penelitian", ["id"], []),
        "pengabdian": ("get_dosen_pengabdian", ["id"], []),
        "karya": ("get_dosen_karya", ["id"], []),
        "paten": ("get_dosen_paten", ["id"], []),
        "riwayat-studi": ("get_dosen_study_history", ["id"], []),
        "riwayat-mengajar": ("get_dosen_teaching_history", ["id"], []),
    },
    "pt": {
        "detail": ("get_detail_pt", ["id"], []),
        "prodi": ("get_prodi_pt", ["id"], ["tahun"]),
        "logo": ("get_logo_pt", ["id"], []),
        "rasio": ("get_rasio_pt", ["id"], []),
        "mahasiswa": ("get_mahasiswa_pt", ["id"], []),
        "waktu-studi": ("get_waktu_studi_pt", ["id"], []),
        "riwayat-nama": ("get_name_histories_pt", ["id"], []),
        "biaya": ("get_cost_range_pt", ["id"], []),
        "kelulusan": ("get_graduation_rate_pt", ["id"], []),
        "jumlah-prodi": ("get_jumlah_prodi_pt", ["id"], []),
        "jumlah-mahasiswa": ("get_jumlah_mahasiswa_pt", ["id"], []),
        "jumlah-dosen": ("get_jumlah_dosen_pt", ["id"], []),
        "sarpras-nama-file": ("get_sarpras_file_name_pt", ["id"], []),
        "sarpras-blob": ("get_sarpras_blob_pt", ["id"], []),
        "lokasi": ("get_pt_locations", [], []),
    },
    "prodi": {
        "detail": ("get_detail_prodi", ["id"], []),
        "deskripsi": ("get_desc_prodi", ["id"], []),
        "riwayat-nama": ("get_name_histories_prodi", ["id"], []),
        "jumlah-mhs-dosen": ("get_num_students_lecturers_prodi", ["id"], []),
        "biaya": ("get_cost_range_prodi", ["id"], []),
        "daya-tampung": ("get_daya_tampung_prodi", ["id"], []),
        "rasio": ("get_rasio_dosen_mahasiswa_prodi", ["id"], []),
        "graduation-rate": ("get_graduation_rate_prodi", ["id"], []),
        "logo": ("get_logo_prodi", ["id"], []),
        "homebase": ("get_homebase_prodi", ["id"], ["tahun"]),
        "hitung-rasio": ("get_penghitung_ratio_prodi", ["id"], ["tahun"]),
        "bidang-ilmu": ("get_bidang_ilmu_prodi", [], []),
    },
    "stats": {
        "count": None,  # khusus: gabungan semua jumlah
        "pt-count": ("get_pt_count", [], []),
        "prodi-count": ("get_prodi_count", [], []),
        "dosen-count": ("get_dosen_count", [], []),
        "dosen-count-active": ("get_dosen_count_active", [], []),
        "mahasiswa-count": ("get_mahasiswa_count", [], []),
        "mahasiswa-count-active": ("get_mahasiswa_count_active", [], []),
        "dosen-keaktifan": ("get_data_dosen_keaktifan", [], []),
        "dosen-bidang": ("get_data_dosen_bidang", [], []),
        "dosen-jenis-kelamin": ("get_data_dosen_jenis_kelamin", [], []),
        "dosen-jenjang": ("get_data_dosen_jenjang", [], []),
        "dosen-ikatan": ("get_data_dosen_ikatan", [], []),
        "mahasiswa-bidang": ("get_data_mahasiswa_bidang", [], []),
        "mahasiswa-jenis-kelamin": ("get_data_mahasiswa_jenis_kelamin", [], []),
        "mahasiswa-jenjang": ("get_data_mahasiswa_jenjang", [], []),
        "mahasiswa-kelompok-lembaga": ("get_data_mahasiswa_kelompok_lembaga", [], []),
        "mahasiswa-status": ("get_data_mahasiswa_status", [], []),
        "pt-bentuk": ("get_data_pt_bentuk", [], []),
        "pt-akreditasi": ("get_data_pt_akreditasi", [], []),
        "pt-kelompok-pembina": ("get_data_pt_kelompok_pembina", [], []),
        "pt-provinsi": ("get_data_pt_provinsi", [], []),
        "prodi-jenjang": ("get_data_prodi_jenjang", [], []),
        "prodi-akreditasi": ("get_data_prodi_akreditasi", [], []),
        "prodi-bidang-ilmu": ("get_data_prodi_bidang_ilmu", [], []),
        "prodi-kelompok-pembina": ("get_data_prodi_kelompok_pembina", [], []),
    },
    "site": {
        "beranda": ("get_beranda", [], ["content_limit"]),
        "contributor": ("get_contributor", [], []),
        "news": ("get_news", [], ["page", "page_size", "search"]),
        "announcements": ("get_announcements", [], ["page", "page_size", "search"]),
        "publications": ("get_publications", [], ["page", "page_size", "search"]),
        "activities": ("get_activities", [], ["page", "page_size", "search"]),
        "activity-detail": ("get_activity_detail", ["id"], []),
    },
}

COUNT_METHODS = [
    "get_pt_count", "get_prodi_count", "get_dosen_count", "get_dosen_count_active",
    "get_mahasiswa_count", "get_mahasiswa_count_active",
]


# ---------------------------------------------------------------------------
def build_client(args):
    kwargs = {}
    if args.base_url:
        kwargs["base_url"] = args.base_url
    cf = args.cf_clearance or os.getenv("CF_CLEARANCE")
    ua = args.user_agent or os.getenv("PDDIKTI_UA")
    if cf:
        kwargs["cf_clearance"] = cf
    if ua:
        kwargs["user_agent"] = ua
    if args.auto_cookie:
        kwargs["auto_cookie"] = True
    return api(**kwargs)


def run_method(client, method, call_args=(), call_kwargs=None):
    fn = getattr(client, method, None)
    if fn is None:
        return {"error": f"method '{method}' tidak ada di versi pddiktipy yang terpasang"}
    try:
        result = fn(*call_args, **(call_kwargs or {}))
    except Exception as exc:  # noqa: BLE001 - tampilkan error apa adanya
        return {"error": f"{type(exc).__name__}: {exc}"}
    if result is None:
        return {"error": "tidak ada hasil / request gagal (cek akses Cloudflare & input)"}
    return result


def output(data, args):
    if isinstance(data, (bytes, bytearray)):
        data = {"bytes": len(data), "note": "data biner; gunakan --out untuk menyimpan"}
    text = json.dumps(data, indent=None if args.compact else 2, ensure_ascii=False, default=str)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Tersimpan ke {args.out}")
    else:
        print(text)


def execute(client, group, sub, ns, args):
    spec = COMMANDS[group][sub]
    if spec is None:  # stats count
        return {m.replace("get_", ""): run_method(client, m) for m in COUNT_METHODS}
    method, positional, options = spec
    call_args = []
    for name in positional:
        call_args.append(getattr(ns, name))
    call_kwargs = {}
    if "tahun" in options:
        if ns.tahun is None:
            return {"error": "opsi --tahun wajib untuk perintah ini, mis. --tahun 2024"}
        call_args.append(ns.tahun)
    for opt in ("content_limit", "page", "page_size", "search"):
        if opt in options and getattr(ns, opt, None) not in (None, ""):
            call_kwargs[opt] = getattr(ns, opt)
    return run_method(client, method, call_args, call_kwargs)


def list_methods():
    print("Perintah yang tersedia:\n")
    for group, subs in COMMANDS.items():
        for sub, spec in subs.items():
            method = "(gabungan)" if spec is None else spec[0]
            extra = ""
            if spec:
                extra = " " + " ".join(f"<{p}>" for p in spec[1])
                if "tahun" in spec[2]:
                    extra += " --tahun TAHUN"
            print(f"  {(group + ' ' + sub + extra):<45} -> {method}")
    print("\nTambahan: search-pt-filter / search-prodi-filter / menu / methods")


def parse_filters(items):
    filters = {}
    for item in items or []:
        if "=" not in item:
            sys.exit(f"Filter harus berformat key=value, dapat: {item}")
        k, v = item.split("=", 1)
        filters[k] = v
    return filters


def interactive_menu(client, args):
    flat = [(g, s) for g, subs in COMMANDS.items() for s in subs]
    while True:
        print("\n=== PDDIKTI MENU ===")
        for i, (g, s) in enumerate(flat, 1):
            print(f"{i:>3}. {g} {s}")
        print("  0. Keluar")
        choice = input("Pilih nomor: ").strip()
        if choice in ("0", "q", ""):
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(flat):
            print("Pilihan tidak valid.")
            continue
        group, sub = flat[int(choice) - 1]
        spec = COMMANDS[group][sub]
        ns = argparse.Namespace(page=None, page_size=None, search=None,
                                content_limit=None, tahun=None)
        if spec:
            for p in spec[1]:
                setattr(ns, p, input(f"{p}: ").strip())
            if "tahun" in spec[2]:
                ns.tahun = input("tahun: ").strip() or None
            for opt in ("page", "page_size", "search", "content_limit"):
                if opt in spec[2]:
                    val = input(f"{opt} (kosong = default): ").strip()
                    setattr(ns, opt, (int(val) if val.isdigit() else val) or None)
        output(execute(client, group, sub, ns, args), args)


# ---------------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(
        description="CLI untuk pddiktipy (PDDIKTI unofficial API wrapper)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--auto-cookie", action="store_true",
                   help="baca cf_clearance dari browser lokal (butuh pddiktipy[auto])")
    p.add_argument("--cf-clearance", help="nilai cookie cf_clearance (atau env CF_CLEARANCE)")
    p.add_argument("--user-agent", help="User-Agent browser (atau env PDDIKTI_UA)")
    p.add_argument("--base-url", help="URL proxy solver, mis. http://localhost:8080/api")
    p.add_argument("--out", help="simpan hasil JSON ke file")
    p.add_argument("--compact", action="store_true", help="JSON satu baris")

    sub = p.add_subparsers(dest="group", required=True)

    for group, subs in COMMANDS.items():
        gp = sub.add_parser(group, help=f"perintah grup '{group}'")
        sp = gp.add_subparsers(dest="sub", required=True)
        for name, spec in subs.items():
            cp = sp.add_parser(name)
            if spec:
                for pos in spec[1]:
                    cp.add_argument(pos)
                if "tahun" in spec[2]:
                    cp.add_argument("--tahun", type=int, help="tahun, mis. 2024")
                if "content_limit" in spec[2]:
                    cp.add_argument("--content-limit", dest="content_limit", type=int)
                if "page" in spec[2]:
                    cp.add_argument("--page", type=int, default=1)
                    cp.add_argument("--page-size", dest="page_size", type=int, default=10)
                    cp.add_argument("--search", default="")

    for name in ("search-pt-filter", "search-prodi-filter"):
        fp = sub.add_parser(name, help="pencarian dengan filter lanjutan")
        fp.add_argument("--limit", type=int, default=10)
        fp.add_argument("--offset", type=int, default=0)
        fp.add_argument("--filter", action="append", metavar="KEY=VALUE",
                        help="bisa dipakai berulang")

    sub.add_parser("methods", help="daftar semua perintah")
    sub.add_parser("menu", help="mode interaktif")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.group == "methods":
        return list_methods()

    with build_client(args) as client:
        if args.group == "menu":
            return interactive_menu(client, args)
        if args.group in ("search-pt-filter", "search-prodi-filter"):
            method = args.group.replace("-", "_")
            result = run_method(client, method, [],
                                {"limit": args.limit, "offset": args.offset,
                                 **parse_filters(args.filter)})
            return output(result, args)
        output(execute(client, args.group, args.sub, args, args), args)


if __name__ == "__main__":
    main()
