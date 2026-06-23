import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import re

# --- CONFIG HALAMAN ---
st.set_page_config(page_title="AdminGuru Pro AI", layout="wide", page_icon="🎓")

# --- CSS CUSTOM DASHBOARD DARK MODE (FIXED) ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e14; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; min-width: 300px !important; }
    .content-card { background-color: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 20px; }
    .header-title { color: #9333ea; font-size: 28px; font-weight: 700; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
    
    /* Perbaikan CSS Status Tag */
    .status-tag { 
        background-color: rgba(16, 185, 129, 0.1); 
        color: #10b981; 
        padding: 4px 12px; 
        border-radius: 20px; 
        font-size: 12px; 
        border: 1px solid #10b981; 
    }

    .stButton>button {
        background-color: #1f2937; color: white; border: 1px solid #30363d;
        border-radius: 8px; padding: 10px 20px; width: 100%; text-align: left; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #9333ea; border-color: #9333ea; }
    
    .stTextInput>div>div>input, .stSelectbox>div>div {
        background-color: #0d1117 !important; color: white !important; border: 1px solid #30363d !important;
    }
    h1, h2, h3, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- AI SETUP (ANTI-404 & FIX KUNCI AQ) ---
@st.cache_resource
def init_ai():
    try:
        if "GEMINI_API_KEY" not in st.secrets: return None, "API Key tidak ditemukan di Secrets."
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key, transport="rest")
        
        # Cari model yang tersedia secara otomatis
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        return genai.GenerativeModel(target), None
    except Exception as e:
        return None, str(e)

model, err = init_ai()

# --- FUNGSI PDF ANTI-CRASH ---
def safe_text(text):
    if not text: return ""
    # Hapus simbol markdown
    text = re.sub(r'[*#|_]', '', text)
    # Ganti karakter unicode ke standar latin-1
    repl = {'\u2013':'-', '\u2014':'-', '\u2018':"'", '\u2019':"'", '\u201c':'"', '\u201d':'"', '\u2022':'*'}
    for k, v in repl.items(): text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='text-align: center; padding: 20px;'><img src='https://upload.wikimedia.org/wikipedia/commons/9/9c/Logo_Kemdikbud.png' width='50'><h3 style='margin-top:10px;'>SD NEGERI 1 PRO</h3><p style='font-size:12px; color: #8b949e;'>ADMINISTRASI SISTEM AI</p></div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e; font-size:11px; font-weight:bold; margin-left:10px;'>MENU UTAMA</p>", unsafe_allow_html=True)
    menu = st.radio("Nav", ["Dashboard", "Profil Sekolah"], label_visibility="collapsed")
    
    with st.expander("👤 Data Pengampu"):
        nama_guru = st.text_input("Guru", "AHMAD FATHONI, S.Pd.")
        nip = st.text_input("NIP", "1990xxxx")
        sekolah = st.text_input("Sekolah", "SD NEGERI 1")
        kepsek = st.text_input("Kepala Sekolah", "DRA. SURYANI, M.Pd.")

# --- MAIN CONTENT ---
if menu == "Dashboard":
    st.markdown('<div class="header-title"><span>📋</span> Kelayakan Administrasi Pembelajaran</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e;'>Sesuai Permendikdasmen No. 13 Tahun 2025. Data terintegrasi otomatis.</p>", unsafe_allow_html=True)

    # Inisialisasi state agar tidak hilang
    if 'prota' not in st.session_state: st.session_state.prota = ""
    if 'ma' not in st.session_state: st.session_state.ma = ""

    # Area Pilihan
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            mapel = st.selectbox("Mapel", ["Pendidikan Pancasila (PKN)", "Bahasa Indonesia", "Matematika", "IPAS", "PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"])
        with col2:
            kelas = st.text_input("Kelas", "4")
        with col3:
            fase = st.selectbox("Fase", ["A", "B", "C", "D", "E", "F"])
        
        if st.button(f"✨ Generate Seluruh Administrasi {mapel}"):
            if model:
                with st.spinner("AI sedang bekerja..."):
                    # Logika JP sesuai Permen
                    is_special = any(x in mapel for x in ["PABP", "PJOK", "Inggris", "Jawa"])
                    jp = "1 pertemuan tuntas" if is_special else "dibagi per 2 JP per pertemuan"
                    
                    # Generate Prota
                    res_prota = model.generate_content(f"Buat Tabel Prota {mapel} Kelas {kelas} Fase {fase} Kurikulum Merdeka.")
                    st.session_state.prota = res_prota.text
                    
                    # Generate Modul Ajar
                    res_ma = model.generate_content(f"Buat Modul Ajar {mapel} Kelas {kelas}. Aturan JP: {jp}. Lengkap dengan Asesmen & Bahan Ajar.")
                    st.session_state.ma = res_ma.text
            else:
                st.error(f"Koneksi AI Gagal: {err}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Tabs Hasil
    tab_p, tab_m, tab_d = st.tabs(["📄 PROTA", "📘 MODUL AJAR", "📥 DOWNLOAD PDF"])
    
    with tab_p:
        if st.session_state.prota:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.write(st.session_state.prota)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.info("Belum ada data Prota.")

    with tab_m:
        if st.session_state.ma:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.write(st.session_state.ma)
            st.markdown('</div>', unsafe_allow_html=True)
        else: st.info("Belum ada data Modul Ajar.")

    with tab_d:
        if st.session_state.ma:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("<span class='status-tag'>✓ DOKUMEN SIAP</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📑 PROSES KE PDF SEKARANG"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, safe_text(sekolah.upper()), 0, 1, "C")
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 5, "ADMINISTRASI GURU TA 2025/2026", 0, 1, "C")
                pdf.line(10, 30, 200, 30)
                pdf.ln(10)
                
                # Isi Gabungan
                full_body = f"PROTA:\n{st.session_state.prota}\n\nMODUL AJAR:\n{st.session_state.ma}"
                pdf.multi_cell(0, 6, safe_text(full_body))
                
                # Tanda Tangan
                pdf.ln(20)
                pdf.cell(90, 5, "Mengetahui,", 0, 0, "C")
                pdf.cell(90, 5, "Semarang, ................. 2025", 0, 1, "C")
                pdf.cell(90, 5, "Kepala Sekolah,", 0, 0, "C")
                pdf.cell(90, 5, "Guru Mata Pelajaran,", 0, 1, "C")
                pdf.ln(20)
                pdf.set_font("Arial", "BU", 10)
                pdf.cell(90, 5, safe_text(kepsek), 0, 0, "C")
                pdf.cell(90, 5, safe_text(nama_guru), 0, 1, "C")
                
                pdf.output("Adm_Guru_2025.pdf")
                with open("Adm_Guru_2025.pdf", "rb") as f:
                    st.download_button("📥 KLIK UNTUK SIMPAN PDF", f, "Administrasi_Lengkap_2025.pdf")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Generate data dulu untuk mendownload PDF.")
else:
    st.info("Fitur Profil Sekolah sedang dalam pemeliharaan.")
