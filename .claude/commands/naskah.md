---
description: "Siapkan naskah episode Ata: riset dan verifikasi jurnal, lalu buat prompt ChatGPT. Argumen: <id-episode> \"<topik>\""
---

1. Buat folder `episode/<id-episode>/` bila belum ada.
2. **Riset (satu-satunya bagian yang memakai LLM dan konektor):** cari temuan jurnal internasional untuk topik itu lewat konektor riset yang tersedia (Consensus, Elicit, SciSpace). Utamakan temuan yang sudah direplikasi atau meta-analisis; hindari temuan yang gagal direplikasi (power pose, ego depletion, efek Mozart). Verifikasi setiap angka ke abstrak atau teks makalah, atau ke sumber sekunder tepercaya yang mengutip makalah itu, dan catat caranya.
3. Tulis `episode/<id>/kartu-riset.yaml` mengikuti contoh `contoh/ep01-planning-fallacy/kartu-riset.yaml`. Jangan pernah mengarang angka; tulis batas temuannya.
4. Jalankan `.venv/bin/python -m scripts.prompt_naskah episode/<id> --topik "<topik>"`.
5. Sampaikan ke pemilik dalam 3 baris: tempel `episode/<id>/prompt-chatgpt.md` ke ChatGPT, simpan jawabannya sebagai `episode/<id>/tempelan.txt` (atau tempel ke chat dan Claude menyimpannya apa adanya), lalu jalankan `/olah <id>`. Berhenti.

Topik harus aman untuk merek (tanpa politik, agama, tuduhan, orang sungguhan). Jangan menulis naskahnya sendiri kecuali pemilik meminta.
