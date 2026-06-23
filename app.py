import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- KONFIGURASI AMAN & FIX ERROR 401 ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = None

if API_KEY:
    # PAKSA MENGGUNAKAN TRANSPORT REST UNTUK KUNCI AQ
    genai.configure(api_key=API_KEY, transport="rest")
    # Gunakan Flash karena lebih stabil untuk autentikasi baru
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ API Key tidak ditemukan di Secrets!")

# --- LOGIKA JP ---
def get_subject_logic(mapel):
    special = ["PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"]
    if mapel in special:
        return "Disusun untuk 1 kali pertemuan tuntas (Blok JP)."
    return "Materi dibagi rapi per 2 Jam Pelajaran (JP) per pertemuan."

# --- UI APLIKASI ---
st.set_page_config(page_title="Gen-Guru AI 2025", layout="wide")
st.title("🚀 Auto-Admin Guru 2025 (Fix 401)")

with st.sidebar:
    st.header("📋 Identitas")
    sekolah = st.text_input("Nama Sekolah", "SD Negeri ...")
    guru = st.text_input("Nama Guru", "Nama Anda, S.Pd.")
    nip = st.text_input("NIP", "19xxxx")
    kepsek = st.text_input("Kepala Sekolah", "Nama Kepsek, M.Pd.")
    st.divider()
    mapel = st.selectbox("Mata Pelajaran", ["Bahasa Indonesia", "Matematika", "IPAS", "PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"])
    kelas = st.text_input("Kelas", "4")
    fase = st.text_input("Fase", "B")

if 'data' not in st.session_state:
    st.session_state.data = {}

def generate_konten(prompt):
    if not API_KEY:
        return "Error: API Key belum diatur."
    try:
        # Generate dengan instruksi eksplisit
        response = model.generate_content(prompt)
        if response:
            return response.text
        else:
            return "AI tidak memberikan respon."
    except Exception as e:
        return f"Gagal: {str(e)}"

# --- TAB PROSES ---
t1, t2, t3, t4 = st.tabs(["PROTA", "PROMES", "ATP", "MODUL AJAR"])

with t1:
    if st.button("Generate PROTA Sekarang"):
        with st.spinner("AI sedang menyusun Prota..."):
            p = f"Buatlah Tabel Program Tahunan (PROTA) {mapel} Kelas {kelas} sesuai Permendikdasmen 13/2025. Referensi buku Kemendikdasmen."
            st.session_state.data['prota'] = generate_konten(p)
    if 'prota' in st.session_state.data:
        st.markdown(st.session_state.data['prota'])

# ... (Tab lainnya tetap sama seperti sebelumnya) ...
# Tab Promes, ATP, dan MA akan muncul jika Prota sudah ada
with t4:
    if 'prota' in st.session_state.data:
        if st.button("Generate MODUL AJAR"):
            with st.spinner("Menyusun Modul..."):
                logic = get_subject_logic(mapel)
                p = f"Buat Modul Ajar {mapel} Kelas {kelas}. Aturan JP: {logic}. Sesuai Permendikdasmen 13/2025."
                st.session_state.data['ma'] = generate_konten(p)
        if 'ma' in st.session_state.data:
            st.markdown(st.session_state.data['ma'])
