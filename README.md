# Process Mining — Enterprise Batch Job Process Mining Dashboard

Generic Process Mining & BPI Dashboard untuk analisis backend batch job di sistem Enterprise.

---

##  Cara Menjalankan

### 1. Install dependencies
```bash
pip install -r requirements.txt

# Install graphviz (untuk Heuristic Net visualization)
# Windows:  choco install graphviz  ATAU  download dari https://graphviz.org/download/
# Mac:      brew install graphviz
# Linux:    apt-get install graphviz
```

### 2. Jalankan aplikasi
```bash
streamlit run processmine_app.py
```

### 3. Buka browser
Aplikasi otomatis terbuka di `http://localhost:8501`

---

## Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| **Upload Log** | Upload file .txt/.log dari backend job APAPUN |
| **Configurable Mapping** | Definisikan sendiri keyword → aktivitas (tidak hardcoded) |
| **CSV Event Log** | Atau langsung upload CSV yang sudah berstruktur |
| **Process Discovery** | DFG, Heuristic Net, Variant Analysis |
| **Conformance Checking** | Fitness & Precision vs BPMN referensi |
| **Bottleneck Analysis** | 4 dimensi: total time, frekuensi, mean duration, delay transisi |
| **BPI Recommendations** | Auto-generate rekomendasi teknis & bisnis |
| **Export Report** | Download CSV: bottleneck, BPI, event log, full summary |

---


### Step 1: Upload log file
Upload file .txt atau .log dari job yang ingin dianalisis.

### Step 2: Configure mapping
Buat aturan pemetaan: *"jika ada keyword X di baris log → catat sebagai aktivitas Y"*

Contoh untuk job billing:
```
keyword,activity
START BILLING,Start Batch
FETCH INVOICE,Fetch Invoice Data
```

Atau gunakan **Template** yang sudah tersedia:
- **Repayment Job Template** — untuk insertRepaymentToFrontend
- **Generic Batch Template** — template umum

### Step 3: Parse & Analyze
Klik Parse → Preview event log → Run Full Analysis → lihat hasil

---

##  Struktur Mapping CSV

Kolom:
- `keyword`: substring yang dicari di setiap baris log
- `activity`: nama aktivitas yang akan direkam

---

## Tech Stack

- **Streamlit** — Web UI framework
- **PM4Py** — Process Mining library (Heuristic Miner, Token-Based Replay, Alignment)
- **Plotly** — Interactive charts
- **Pandas** — Data processing
- **Graphviz** — Process model visualization

---

## Output Analisis

### Process Discovery
- Heuristic Net (model proses visual)
- Tabel varian proses + frekuensi
- Distribusi durasi case

### Conformance Checking
- Average Trace Fitness (0-1)
- Precision (0-1)  
- % Trace yang sepenuhnya fit
- Top deviasi: Log Moves & Model Moves

### Bottleneck Analysis
- **Total Time Ranking** — aktivitas dengan beban waktu kumulatif tertinggi
- **Frequency Ranking** — aktivitas yang paling sering dieksekusi
- **Mean Duration Ranking** — aktivitas yang paling lambat per eksekusi
- **Transition Delay** — pasangan aktivitas A→B dengan delay terpanjang

### BPI Recommendations
- Auto-generated berdasarkan hasil analisis
- Dimensi teknis + bisnis
- Prioritas: Tinggi / Sedang / Rendah
