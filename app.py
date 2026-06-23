import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import re

# --- UI CONFIG ---
st.set_page_config(page_title="GenGuru AI Pro", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    .main { background-color: #f0f2f5; }
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 40px; border-radius: 20px; color: white; text-align: center;
        margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    .stButton>button {
        background: #2563eb; color: white; border-radius: 10px;
        height: 3.5em; font-weight: 700; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AI SETUP ---
def init_ai():
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            return None, "API Key tidak ditemukan di Secrets."
        
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key, transport="rest")
        
        # Cari model aktif
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if target in models:
                return genai.GenerativeModel(target), None
        return genai.GenerativeModel(models[0]), None
    except Exception as e:
        return None, str(e)

model, err_msg = init_ai()

# --- APP UI ---
st.markdown('<div class="hero"><h1>🎓 GenGuru Pro Dashboard</h1><p>Sistem Administrasi Guru Otomatis 2025</p></div>', unsafe_allow_html=True)

if err_msg:
    st.error(f"❌ Masalah Koneksi: {err_msg}")

with st.sidebar:
    st.header("📋 Identitas")
    sekolah = st.text_input("Nama Sekolah", "SD NEGERI CIPTA ILMU")
    guru = st.text_input("Nama Guru", "AHMAD FATHONI, S.Pd.")
    nip = st.text_input("NIP", "19920101 202001 1 001")
    kepsek = st.text_input("Kepala Sekolah", "DRA. HJ. SITI AMINAH, M.Pd.")
    st.divider()
    mapel = st.selectbox("Mata Pelajaran", ["Pendidikan Pancasila (PKN)", "Bahasa Indonesia", "Matematika", "IPAS", "PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"])
    kelas = st.text_input("Kelas", "4")

# PENTING: Inisialisasi penyimpanan agar data tidak hilang
if 'prota_res' not in st.session_state: st.session_state.prota_res = ""
if 'ma_res' not in st.session_state: st.session_state.ma_res = ""

def run_ai(prompt):
    if not model: return "AI Tidak Siap."
    try:
        res = model.generate_content(f"Format formal dinas, tanpa basa-basi: {prompt}")
        return res.text
    except Exception as e:
        return f"GAGAL: {str(e)}"

# --- LAYOUT DASHBOARD ---
c1, c2 = st.columns([1, 2.5])

with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🛠️ Kontrol")
    if st.button("📊 BUAT PROTA"):
        with st.spinner("Menyusun Prota..."):
            st.session_state.prota_res = run_ai(f"Buat Tabel Prota {mapel} Kelas {kelas} sesuai Permen 13/2025")
    
    if st.button("📘 BUAT MODUL AJAR (RPP)"):
        with st.spinner("Menyusun Modul..."):
            is_special = any(x in mapel for x in ["PABP", "PJOK", "Inggris", "Jawa"])
            logic = "1 pertemuan tuntas" if is_special else "bagi per 2 JP per pertemuan"
            st.session_state.ma_res = run_ai(f"Buat Modul Ajar {mapel} Kelas {kelas}. Aturan JP: {logic}. Lengkap dengan Asesmen.")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    t1, t2, t3 = st.tabs(["📄 Pratinjau PROTA", "📗 Pratinjau MODUL AJAR", "📥 Download PDF"])
    
    with t1:
        if st.session_state.prota_res:
            st.markdown(f"### Prota {mapel}")
            st.write(st.session_state.prota_res)
        else:
            st.info("Belum ada data Prota. Klik tombol 'BUAT PROTA' di sebelah kiri.")

    with t2:
        if st.session_state.ma_res:
            st.markdown(f"### Modul Ajar {mapel}")
            st.write(st.session_state.ma_res)
        else:
            st.info("Belum ada data Modul Ajar. Klik tombol 'BUAT MODUL AJAR' di sebelah kiri.")

    with t3:
        if st.session_state.ma_res:
            if st.button("📑 PROSES CETAK PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, sekolah.upper(), 0, 1, "C")
                pdf.ln(10)
                pdf.set_font("Arial", "", 10)
                clean_text = re.sub(r'[*#|_]', '', st.session_state.ma_res)
                pdf.multi_cell(0, 6, clean_text)
                pdf.output("Modul_Ajar.pdf")
                with open("Modul_Ajar.pdf", "rb") as f:
                    st.download_button("📥 DOWNLOAD FILE SEKARANG", f, "Modul_Ajar.pdf")
        else:
            st.warning("Generate Modul Ajar terlebih dahulu agar bisa dicetak.")
