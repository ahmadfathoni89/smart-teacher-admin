import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import re

# --- CONFIG HALAMAN ---
st.set_page_config(page_title="AdminGuru Pro AI", layout="wide", page_icon="🎓")

# --- CSS CUSTOM UNTUK MENIRU DASHBOARD PROFESIONAL ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp { background-color: #0a0e14; color: #ffffff; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
        min-width: 300px !important;
    }
    
    /* Card Styling */
    .content-card {
        background-color: #161b22;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    
    /* Header Section */
    .header-title {
        color: #9333ea; /* Purple Accent */
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Status Tag */
    .status-tag {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10b981;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        border: 1px solid #10b981;
    }

    /* Custom Button */
    .stButton>button {
        background-color: #1f2937;
        color: white;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px 20px;
        width: 100%;
        text-align: left;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #9333ea;
        border-color: #9333ea;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stSelectbox>div>div {
        background-color: #0d1117 !important;
        color: white !important;
        border: 1px solid #30363d !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AI SETUP ---
def init_ai():
    try:
        if "GEMINI_API_KEY" not in st.secrets: return None, "Key Missing"
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"], transport="rest")
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        return genai.GenerativeModel(target), None
    except Exception as e: return None, str(e)

model, err = init_ai()

# --- FUNGSI PDF (SAFE UNICODE) ---
def safe_text(text):
    text = re.sub(r'[*#|_]', '', text)
    replacements = {'\u2013':'-', '\u2014':'-', '\u2018':"'", '\u2019':"'", '\u201c':'"', '\u201d':'"', '\u2022':'*'}
    for k, v in replacements.items(): text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <img src='https://upload.wikimedia.org/wikipedia/commons/9/9c/Logo_Kemdikbud.png' width='50'>
            <h3 style='margin-top:10px;'>SD NEGERI 1 PRO</h3>
            <p style='font-size:12px; color: #8b949e;'>ADMINISTRASI SISTEM AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color:#8b949e; font-size:11px; font-weight:bold; margin-left:10px;'>MENU UTAMA</p>", unsafe_allow_html=True)
    
    menu = st.radio("Navigasi", ["Dashboard", "Identitas Sekolah", "Penjadwalan JP", "Monitoring Dokumen"], label_visibility="collapsed")
    
    st.markdown("<br><p style='color:#8b949e; font-size:11px; font-weight:bold; margin-left:10px;'>SUPERVISI GURU</p>", unsafe_allow_html=True)
    
    # Tombol Identitas (Simulasi Sidebar image)
    with st.expander("👤 Profil Pengampu"):
        nama_guru = st.text_input("Nama Guru", "AHMAD FATHONI, S.Pd.")
        nip = st.text_input("NIP", "1990xxxx")
        sekolah = st.text_input("Satuan Pendidikan", "SD NEGERI 1")
        kepsek = st.text_input("Kepala Sekolah", "DRA. SURYANI, M.Pd.")

# --- MAIN CONTENT ---
if menu == "Dashboard":
    st.markdown('<div class="header-title"><span>📋</span> Kelayakan Administrasi Pembelajaran</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e;'>Evaluasi dan generate dokumen kurikulum berdasarkan Permendikdasmen No. 13 Tahun 2025.</p>", unsafe_allow_html=True)

    # Search Bar (Simulasi Image)
    st.text_input("🔍 Cari dokumen atau mata pelajaran...", placeholder="Contoh: Modul Ajar Matematika Kelas 4")

    # Layout Grid untuk Tombol Aksi
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📊 PROTA"): st.session_state.target = "prota"
    with c2:
        if st.button("📅 PROMES"): st.session_state.target = "promes"
    with c3:
        if st.button("🎯 ATP / TP"): st.session_state.target = "atp"
    with c4:
        if st.button("📘 MODUL AJAR"): st.session_state.target = "ma"

    # Area Kerja Utama
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Card Input Konfigurasi
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            mapel = st.selectbox("Mata Pelajaran", ["Pendidikan Pancasila (PKN)", "Bahasa Indonesia", "Matematika", "IPAS", "PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"])
        with col_b:
            kelas = st.text_input("Kelas", "4")
        with col_c:
            fase = st.selectbox("Fase", ["A", "B", "C", "D", "E", "F"])
        
        # Tombol Generate Utama
        if st.button(f"✨ Generate Dokumen {mapel}"):
            with st.spinner("AI sedang menyusun administrasi..."):
                # Logika JP Khusus
                is_special = any(x in mapel for x in ["PABP", "PJOK", "Inggris", "Jawa"])
                jp_logic = "1 pertemuan tuntas" if is_special else "bagi per 2 JP per pertemuan"
                
                prompt = f"Buatlah Modul Ajar Lengkap {mapel} Kelas {kelas} Fase {fase}. Aturan JP: {jp_logic}. Berikan tabel jika perlu. Referensi: buku.kemendikdasmen.go.id/katalog."
                try:
                    res = model.generate_content(prompt)
                    st.session_state.last_result = res.text
                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Hasil Dokument (Tabel Style)
    if 'last_result' in st.session_state:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.markdown(f"**DOKUMEN TERBENTUK:** Modul Ajar - {mapel}")
        with col_h2:
            st.markdown("<span class="status-tag">✓ SIAP CETAK</span>", unsafe_allow_html=True)
        
        st.divider()
        st.write(st.session_state.last_result)
        
        # Download PDF
        if st.button("📥 EXPORT KE PDF DINAS"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, safe_text(sekolah.upper()), 0, 1, "C")
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 5, "TAHUN AJARAN 2025/2026", 0, 1, "C")
            pdf.line(10, 30, 200, 30)
            pdf.ln(10)
            pdf.multi_cell(0, 6, safe_text(st.session_state.last_result))
            
            # Signature Area
            pdf.ln(20)
            pdf.cell(90, 5, "Kepala Sekolah,", 0, 0, "C")
            pdf.cell(90, 5, "Guru Mata Pelajaran,", 0, 1, "C")
            pdf.ln(20)
            pdf.cell(90, 5, safe_text(kepsek), 0, 0, "C")
            pdf.cell(90, 5, safe_text(nama_guru), 0, 1, "C")
            
            pdf.output("Adm_Guru_Pro.pdf")
            with open("Adm_Guru_Pro.pdf", "rb") as f:
                st.download_button("📂 Klik untuk Simpan PDF", f, "Administrasi_Guru_Pro.pdf")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Menu ini masih dalam pengembangan untuk fitur monitoring.")
