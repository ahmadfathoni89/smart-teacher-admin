import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- SISTEM AUTO-DETECT MODEL (FIX 404 & 401) ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = None

@st.cache_resource
def get_working_model(api_key):
    if not api_key:
        return None
    try:
        # Gunakan transport REST agar cocok dengan kunci AQ
        genai.configure(api_key=api_key, transport="rest")
        
        # Cari model yang aktif di akun Bapak/Ibu
        available_models = [m.name for m in genai.list_models() 
                            if 'generateContent' in m.supported_generation_methods]
        
        # Urutan prioritas model
        for target in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if target in available_models:
                test_model = genai.GenerativeModel(target)
                # Tes koneksi singkat
                test_model.generate_content("test", generation_config={"max_output_tokens": 1})
                return test_model
        
        # Jika tidak ada yang cocok, ambil yang pertama tersedia
        if available_models:
            return genai.GenerativeModel(available_models[0])
    except Exception as e:
        st.error(f"Koneksi Gagal: {str(e)}")
        return None

# Inisialisasi Model
model = get_working_model(API_KEY)

# --- IDENTITAS & LOGIKA ---
st.set_page_config(page_title="Gen-Guru AI 2025", layout="wide")
st.title("📝 Auto-Admin Guru TA 2025/2026")
st.caption("Sesuai Permendikdasmen No. 13 Tahun 2025")

with st.sidebar:
    st.header("📋 Data Administrasi")
    sekolah = st.text_input("Nama Sekolah", "SD Negeri ...")
    guru = st.text_input("Nama Guru", "Nama Guru, S.Pd.")
    nip = st.text_input("NIP", "19xxxx")
    kepsek = st.text_input("Kepala Sekolah", "Nama Kepsek, M.Pd.")
    st.divider()
    mapel = st.selectbox("Mata Pelajaran", ["Bahasa Indonesia", "Matematika", "IPAS", "PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"])
    kelas = st.text_input("Kelas", "4")
    fase = st.text_input("Fase", "B")

if 'data' not in st.session_state:
    st.session_state.data = {}

def generate_ai(prompt):
    if not model:
        return "❌ Model AI belum siap. Tunggu 5-10 menit setelah klik ENABLE di Google Cloud."
    try:
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"Gagal generate: {str(e)}"

# --- TAB SEKUENSIAL ---
t1, t2, t3, t4 = st.tabs(["1. PROTA", "2. PROMES", "3. CP/ATP", "4. MODUL AJAR"])

with t1:
    if st.button("Buat PROTA"):
        with st.spinner("AI sedang menyusun Prota..."):
            p = f"Buatlah Tabel Prota {mapel} Kelas {kelas} sesuai Permendikdasmen 13/2025."
            st.session_state.data['prota'] = generate_ai(p)
    if 'prota' in st.session_state.data:
        st.markdown(st.session_state.data['prota'])

with t2:
    if 'prota' not in st.session_state.data:
        st.warning("Buat Prota dulu di Tab 1")
    else:
        if st.button("Buat PROMES"):
            with st.spinner("Menyusun Promes..."):
                p = f"Buat Promes berdasarkan Prota ini: {st.session_state.data['prota']}"
                st.session_state.data['promes'] = generate_ai(p)
        if 'promes' in st.session_state.data:
            st.markdown(st.session_state.data['promes'])

with t4:
    if 'prota' in st.session_state.data:
        # Logika pembagian JP sesuai permintaan
        logic = "1 kali pertemuan tuntas" if mapel in ["PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"] else "Dibagi per 2 Jam Pelajaran (JP) per pertemuan"
        
        if st.button("Buat MODUL AJAR LENGKAP"):
            with st.spinner("Menyusun Modul..."):
                p = f"Buat Modul Ajar {mapel} Kelas {kelas}. Aturan JP: {logic}. Lengkap dengan Bahan Ajar & Asesmen."
                st.session_state.data['ma'] = generate_ai(p)
        if 'ma' in st.session_state.data:
            st.markdown(st.session_state.data['ma'])
            
            # FITUR CETAK PDF
            if st.button("📥 Download PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                txt = f"ADMINISTRASI GURU\nSekolah: {sekolah}\nGuru: {guru}\n\n{st.session_state.data['ma']}"
                pdf.multi_cell(0, 5, txt.encode('latin-1', 'replace').decode('latin-1'))
                pdf.output("Modul_Ajar.pdf")
                with open("Modul_Ajar.pdf", "rb") as f:
                    st.download_button("Simpan ke Komputer", f, "Modul_Ajar.pdf")
