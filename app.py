import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import re

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="GenGuru AI Pro 2025", page_icon="🎓", layout="wide")

# Custom CSS Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    .stApp { background-color: #f8fafc; }
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background: #2563eb; color: white; border-radius: 10px;
        font-weight: 600; width: 100%; transition: 0.3s;
        height: 3em;
    }
    .stButton>button:hover { background: #1e40af; transform: translateY(-2px); }
    
    /* Area Pratinjau Teks */
    .preview-box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE AI SETUP ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY, transport="rest")
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except:
    st.error("⚠️ API Key tidak ditemukan. Selesaikan setup di Secrets!")

# --- PDF GENERATOR ENGINE (STANDAR DINAS) ---
class RPP_PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            self.set_font('Arial', 'B', 14)
            self.set_text_color(30, 58, 138)
            self.cell(0, 10, self.school_info['nama'].upper(), 0, 1, 'C')
            self.set_font('Arial', '', 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, 5, "TAHUN AJARAN 2025/2026", 0, 1, 'C')
            self.line(10, 28, 200, 28)
            self.ln(15)

    def draw_table(self, header, data):
        self.set_fill_color(37, 99, 235) # Warna Biru Header
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10)
        # Header Tabel
        self.cell(60, 10, header[0], 1, 0, 'C', 1)
        self.cell(130, 10, header[1], 1, 1, 'C', 1)
        
        # Isi Tabel
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 10)
        for row in data:
            self.cell(60, 8, row[0], 1)
            self.cell(130, 8, row[1], 1)
            self.ln()

# --- HELPER FUNCTIONS ---
def clean_markdown(text):
    # Membersihkan karakter markdown agar teks bersih di PDF
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+', '', text)
    text = re.sub(r'\|', '', text)
    return text.strip()

# --- APP UI ---
st.markdown('<div class="main-header"><h1>🎓 GenGuru AI Pro 2025</h1><p>Revisi: Daftar Mapel Lengkap | Sesuai Permendikdasmen No. 13 Tahun 2025</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📋 Identitas Sekolah & Guru")
    nama_sekolah = st.text_input("Nama Sekolah", "SD NEGERI 1 MERDEKA")
    nama_guru = st.text_input("Nama Guru", "AHMAD FATHONI, S.Pd.")
    nip = st.text_input("NIP", "19920101 202001 1 001")
    kepsek = st.text_input("Kepala Sekolah", "DRA. SITI NURJANAH, M.Pd.")
    
    st.divider()
    st.markdown("### 📚 Pilihan Mata Pelajaran")
    # SEKARANG SUDAH KOMPLIT PAK!
    mapel = st.selectbox("Mata Pelajaran", [
        "Pendidikan Pancasila (PKN)", 
        "Bahasa Indonesia", 
        "Matematika", 
        "IPAS", 
        "PABP (Agama)", 
        "PJOK", 
        "Bahasa Inggris", 
        "Bahasa Jawa / Daerah",
        "Seni Musik",
        "Seni Rupa",
        "Seni Tari"
    ])
    kelas = st.text_input("Kelas", "4")
    fase = st.selectbox("Fase", ["A", "B", "C", "D", "E", "F"])

# State Management
if 'steps' not in st.session_state:
    st.session_state.steps = {"prota": "", "promes": "", "atp": "", "ma": ""}

def generate_ai(prompt):
    full_prompt = f"Tuliskan langsung ke isi dokumen tanpa kata pengantar. Gunakan Bahasa Indonesia formal standar dinas pendidikan. {prompt}"
    try:
        res = model.generate_content(full_prompt)
        return res.text
    except Exception as e:
        return f"Gagal Generate: {str(e)}"

# --- WORKFLOW ---
col_nav, col_content = st.columns([1, 2.5])

with col_nav:
    st.markdown("### 🛠️ Dashboard Kerja")
    if st.button("🚀 1. Generate PROTA"):
        with st.spinner("AI sedang merangkum program tahunan..."):
            st.session_state.steps["prota"] = generate_ai(f"Buat Program Tahunan (PROTA) {mapel} Kelas {kelas} Fase {fase} sesuai kurikulum merdeka 2025 dalam poin-poin bab.")
    
    if st.button("📅 2. Generate PROMES"):
        if not st.session_state.steps["prota"]: st.warning("Prota belum dibuat.")
        else:
            with st.spinner("Menyusun Program Semester..."):
                st.session_state.steps["promes"] = generate_ai(f"Berdasarkan Prota: {st.session_state.steps['prota']}, buatkan Program Semester (PROMES) ganjil genap.")

    if st.button("📘 3. Generate MODUL AJAR (RPP)"):
        # Logika khusus permintaan User (PABP, PJOK, Inggris, Jawa = 1 Pertemuan Tuntas)
        is_special = any(x in mapel for x in ["PABP", "PJOK", "Inggris", "Jawa"])
        logic = "buat 1 modul untuk 1 kali pertemuan utuh (tuntas)" if is_special else "bagi materi per 2 Jam Pelajaran (JP) per pertemuan agar rapi"
        
        with st.spinner("Menyusun Modul Ajar (RPP) Lengkap..."):
            st.session_state.steps["ma"] = generate_ai(f"Buat Modul Ajar {mapel} Kelas {kelas} Fase {fase}. Aturan JP: {logic}. Harus mencakup Profil Pelajar Pancasila, Langkah Pembelajaran, Bahan Ajar, Asesmen Formatif & Sumatif sesuai Permen 13/2025.")

with col_content:
    tab1, tab2, tab3 = st.tabs(["📄 Pratinjau Dokumen", "📘 RPP (Siap Dinas)", "📥 Cetak PDF"])
    
    with tab1:
        if st.session_state.steps["prota"]:
            st.markdown(f"### PROTA {mapel.upper()}")
            st.markdown(f'<div class="preview-box">{clean_markdown(st.session_state.steps["prota"]).replace("\n", "<br>")}</div>', unsafe_allow_html=True)
        else:
            st.image("https://illustrations.popsy.co/blue/creative-writing.svg", width=350)
            st.info("Klik tombol di kiri untuk mulai men-generate dokumen.")

    with tab2:
        if st.session_state.steps["ma"]:
            st.markdown(f"### MODUL AJAR {mapel.upper()}")
            st.markdown(f'<div class="preview-box">{clean_markdown(st.session_state.steps["ma"]).replace("\n", "<br>")}</div>', unsafe_allow_html=True)
        else:
            st.warning("Silakan generate Modul Ajar terlebih dahulu.")

    with tab3:
        if st.session_state.steps["ma"]:
            if st.button("✨ CETAK SEMUA KE PDF"):
                pdf = RPP_PDF()
                pdf.school_info = {"nama": nama_sekolah, "guru": nama_guru}
                pdf.add_page()
                
                # Identitas dalam Tabel (REAL TABLE)
                identitas = [
                    ["Mata Pelajaran", mapel],
                    ["Fase / Kelas", f"{fase} / {kelas}"],
                    ["Nama Guru", nama_guru],
                    ["Target Peserta", "Reguler / Tipikal"]
                ]
                pdf.draw_table(["KOMPONEN", "KETERANGAN"], identitas)
                
                pdf.ln(10)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, "ISI MODUL AJAR / RPP", 0, 1, 'L')
                pdf.set_font('Arial', '', 10)
                
                # Konten Bersih
                isi_rpp = clean_markdown(st.session_state.steps["ma"])
                pdf.multi_cell(0, 6, isi_rpp)
                
                # Tanda Tangan
                pdf.ln(20)
                y_sign = pdf.get_y()
                pdf.set_font('Arial', '', 10)
                pdf.set_x(20)
                pdf.cell(80, 5, "Mengetahui,", 0, 1, 'C')
                pdf.set_x(20)
                pdf.cell(80, 5, "Kepala Sekolah,", 0, 0, 'C')
                
                pdf.set_xy(110, y_sign)
                pdf.cell(80, 5, "Semarang, ................. 2025", 0, 1, 'C')
                pdf.set_x(110)
                pdf.cell(80, 5, "Guru Mata Pelajaran,", 0, 1, 'C')
                
                pdf.ln(20)
                pdf.set_font('Arial', 'BU', 10)
                pdf.set_x(20)
                pdf.cell(80, 5, kepsek, 0, 0, 'C')
                pdf.cell(80, 5, nama_guru, 0, 1, 'C')
                
                pdf.set_font('Arial', '', 10)
                pdf.set_x(20)
                pdf.cell(80, 5, f"NIP. .........................", 0, 0, 'C')
                pdf.cell(80, 5, f"NIP. {nip}", 0, 1, 'C')
                
                # Output
                pdf.output("RPP_GenGuru_Final.pdf")
                with open("RPP_GenGuru_Final.pdf", "rb") as f:
                    st.download_button("📥 KLIK DISINI UNTUK DOWNLOAD PDF", f, file_name=f"RPP_{mapel}_{kelas}.pdf")
