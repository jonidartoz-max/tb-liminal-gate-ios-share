# Save Data Editor — Terra Battle (Liminal Gate)

Editor HTML offline untuk save file (`bootstrap-state.json`): tambah/hapus
karakter, lalu unduh save yang **sudah dipastikan aman**.

## Cara pakai

1. Buka `OPEN-EDITOR.bat` (atau klik 2x `SAVE-EDITOR.html`) — jalan di browser, tanpa install.
2. **Open Save File...** → pilih `bootstrap-state.json` server kamu.
3. Pilih karakter di kiri → **→ ADD TO SAVE**. (Ctrl/Shift+klik untuk banyak sekaligus.)
4. Hapus karakter: pilih di kanan → **← REMOVE FROM SAVE**.
5. Klik **Check & Fix** — lihat laporan. Harus muncul centang hijau.
6. **Save (download)** → hasilnya `<nama>-EDITED.json`.
7. Ganti nama jadi `bootstrap-state.json`, taruh di folder server (timpa yang lama).
   **Matikan server dulu**, dan simpan backup save lama.

## Check & Fix — kenapa ini penting

Save yang bentuknya salah bikin game **langsung crash** (SIGTRAP) saat load.
Editor ini menormalkan otomatis setiap kali kamu klik Save:

| Yang dinormalkan | Kenapa |
|---|---|
`teamMembers` → 90 slot | client mengindeks 9 tim × 10; kurang = baca lewat ujung → crash |
`summonList` → 16 slot | slot companion/summon; kosong = crash |
`teamMembers_VS` / `teamBuddies_VS` → 18 | squad VS |
`itemList` → 181 slot | inventory |
`lastupdate`, `refillStartTime`, `date`, `jobSlots`, `jobLevels` → **desimal** | client unbox sebagai `double`; angka bulat → InvalidCast → crash |
`chrdata` | diurutkan naik per id, duplikat dibuang, level 0 diganti 10 |
field wajib hilang | ditambahkan dengan default yang sama seperti server |
`chapter`/`section` | dihitung dari `progressCode` (bukan ditulis manual) |
`valuables` | disamakan dengan `coins`/`freeEnergy` |

Kalau **Check & Fix** bilang "No structural issues found" dua kali berturut-turut,
save kamu aman.

## Catatan

- Karakter baru mulai di **Job 1, Level 10** (sama seperti hasil Pact draw).
- `jobID` adalah **indeks job** (0/1/2), bukan id job.
- Selalu simpan backup save sebelum mengedit.
- Editor hanya mengubah data karakter; tidak menyentuh kredit/akun.
