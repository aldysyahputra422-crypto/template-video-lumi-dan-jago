---
description: "Siapkan naskah video Ata: riset dan verifikasi jurnal, lalu buat prompt ChatGPT. Argumen: <nama-video> \"<topik>\""
---

1. Buat folder `video/<nama-video>/` bila belum ada.
2. **Riset (satu-satunya bagian yang memakai LLM dan konektor):** cari temuan jurnal internasional untuk topik itu lewat konektor riset yang tersedia (Consensus, Elicit, SciSpace). Utamakan temuan yang sudah direplikasi atau meta-analisis; hindari temuan yang gagal direplikasi (power pose, ego depletion, efek Mozart). Verifikasi setiap angka ke abstrak atau teks makalah, atau ke sumber sekunder tepercaya yang mengutip makalah itu, dan catat caranya.
3. Tulis `video/<nama>/kartu-riset.yaml` mengikuti contoh `contoh/tenggat-planning-fallacy/kartu-riset.yaml`. Jangan pernah mengarang angka; tulis batas temuannya. Isi juga `nama_konsep` (istilah yang baru boleh disebut sesudah putaran cerita).
4. Jalankan `.venv/bin/python -m scripts.prompt_naskah video/<nama> --topik "<topik>"`.
5. Sampaikan ke pemilik dalam 3 baris: tempel `video/<nama>/prompt-chatgpt.md` ke ChatGPT, simpan jawabannya sebagai `video/<nama>/tempelan.txt` (atau tempel ke chat dan Claude menyimpannya apa adanya), lalu jalankan `/olah <nama>`. Berhenti.

Topik harus aman untuk merek (tanpa politik, agama, tuduhan, orang sungguhan). Jangan menulis naskahnya sendiri kecuali pemilik meminta.
