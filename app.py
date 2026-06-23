import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import re

# --- UI CONFIGURATION ---
st.set_page_config(page_title="GenGuru AI Dashboard", layout="wide", page_icon="🎓")

# CSS Dashboard Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .main { background-color: #f0f2f5; }
    
    /* Hero Header */
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 60px;
        border-radius: 0 0 30px 30px;
        color: white;
        text-align: center;
        margin: -60px -60px 40px -60px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Dashboard Cards */
    .card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: white !important; }
    
    /* Button Premium */
    .stButton>button {
        background: linear-gradient(to right, #2563eb, #1d4ed8);
        color: white; border: none; padding: 15px;
        border-radius: 12px; font-weight: 700; width: 100%;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(37,99,235,0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- AI CORE (ANTI-404 LOGIC) ---
def setup_ai():
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=API_KEY, transport="rest")
        
        # Cari model yang tersedia secara dinamis
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Coba urutan model terbaik
        for target in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if target in models:
                return genai.GenerativeModel(target)
        return genai.GenerativeModel(models[0])
    except Exception as e:
        st.error(f"⚠️ Koneksi Gagal: {str(e)}")
        return None

model = setup_ai()

# --- HELPER PDF ---
class FormalPDF(FPDF):
    def draw_table_header(self, title):
        self.set_fill_color(30, 58, 138)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 10, title, 1, 1, 'C', 1)
        self.set_text_color(0, 0, 0)

    def add_row(self, label, value):
        self.set_font('Arial', 'B', 9)
        self.cell(60, 8, label, 1, 0, 'L')
        self.set_font('Arial', '', 9)
        self.cell(130, 8, value, 1, 1, 'L')

# --- APP UI ---
st.markdown('<div class="hero"><h1>🎓 GenGuru Pro Dashboard</h1><p>Versi 3.0: Sistem Administrasi Cerdas & Standar Dinas Pendidikan</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Pengaturan Dokumen")
    sekolah = st.text_input("Nama Sekolah", "SD NEGERI CIPTA ILMU")
    guru = st.text_input("Nama Guru", "AHMAD FATHONI, S.Pd.")
    nip = st.text_input("NIP/NUPTK", "19920101 202001 1 001")
    kepsek = st.text_input("Kepala Sekolah", "DRA. HJ. SITI AMINAH, M.Pd.")
    
    st.divider()
    mapel = st.selectbox("Mata Pelajaran (Lengkap)", [
        "Pendidikan Pancasila (PKN)", "Bahasa Indonesia", "Matematika", 
        "IPAS", "PABP (Agama)", "PJOK", "Bahasa Inggris", 
        "Seni Musik", "Seni Rupa", "Seni Tari", "Bahasa Jawa/Daerah"
    ])
    kelas = st.text_input("Kelas", "4")
    fase = st.selectbox("Fase", ["A", "B", "C", "D", "E", "F"])

if 'store' not in st.session_state:
    st.session_state.store = {"prota": "", "ma": ""}

def run_gen(prompt):
    if not model: return "AI Tidak Aktif."
    try:
        res = model.generate_content(f"Tulis langsung isinya tanpa basa-basi. Format rapi standar dinas. {prompt}")
        return res.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- LAYOUT DASHBOARD ---
c1, c2 = st.columns([1, 2.5])

with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🛠️ Panel Kontrol")
    if st.button("📊 GENERATE PROTA"):
        st.session_state.store["prota"] = run_gen(f"Buat Tabel Prota {mapel} Kelas {kelas} Fase {fase} Kurikulum Merdeka.")
    
    if st.button("📘 GENERATE MODUL AJAR"):
        # Logika 2 JP atau 1 Pertemuan Tuntas
        logic = "1 pertemuan tuntas" if any(x in mapel for x in ["PABP", "PJOK", "Inggris", "Jawa"]) else "bagi per 2 JP per pertemuan"
        st.session_state.store["ma"] = run_gen(f"Buat Modul Ajar {mapel} Kelas {kelas}. Aturan waktu: {logic}. Lengkap dengan Asesmen & Bahan Ajar.")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    tab1, tab2 = st.tabs(["📝 Pratinjau Dokumen", "📥 Download PDF"])
    
    with tab1:
        if st.session_state.store["ma"]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### Pratinjau Modul Ajar: {mapel}")
            st.write(st.session_state.store["ma"])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Silakan pilih tombol di panel kontrol untuk memulai.")

    with tab2:
        if st.session_state.store["ma"]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if st.button("📑 PROSES KE PDF DINAS"):
                pdf = FormalPDF()
                pdf.add_page()
                
                # Header Table
                pdf.draw_table_header(f"MODUL AJAR / RPP - {mapel.upper()}")
                pdf.add_row("Satuan Pendidikan", sekolah)
                pdf.add_row("Nama Penyusun", guru)
                pdf.add_row("Mata Pelajaran", mapel)
                pdf.add_row("Kelas / Fase", f"{kelas} / {fase}")
                
                pdf.ln(10)
                pdf.set_font('Arial', '', 10)
                # Bersihkan teks dari simbol markdown
                clean_body = re.sub(r'[*#|_]', '', st.session_state.store["ma"])
                pdf.multi_cell(0, 6, clean_body)
                
                # Signature
                pdf.ln(20)
                pdf.cell(90, 5, "Mengetahui,", 0, 0, 'C')
                pdf.cell(90, 5, "Semarang, ................. 2025", 0, 1, 'C')
                pdf.cell(90, 5, "Kepala Sekolah", 0, 0, 'C')
                pdf.cell(90, 5, "Guru Mata Pelajaran,", 0, 1, 'C')
                pdf.ln(20)
                pdf.set_font('Arial', 'BU', 10)
                pdf.cell(90, 5, kepsek, 0, 0, 'C')
                pdf.cell(90, 5, guru, 0, 1, 'C')
                
                pdf.output("RPP_Premium.pdf")
                with open("RPP_Premium.pdf", "rb") as f:
                    st.download_button("📥 DOWNLOAD PDF SEKARANG", f, "Administrasi_Guru_Pro.pdf")
            st.markdown('</div>', unsafe_allow_html=True)
