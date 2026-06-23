import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- KONFIGURASI AMAN ---
# Mengambil API Key dari Secrets (bukan diketik langsung di kode)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "KOSONG"

if API_KEY != "KOSONG":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
else:
    st.error("API Key belum dikonfigurasi di Secrets!")

# --- STYLE PDF CUSTOM UNTUK ADMINISTRASI ---
class AdminPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'ADMINISTRASI PERENCANAAN PEMBELAJARAN', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Sesuai Permendikdasmen No. 13 Tahun 2025', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C')

# --- LOGIKA JP (JAM PELAJARAN) ---
def get_subject_logic(mapel):
    # Mapel yang langsung 1 kali pertemuan tuntas
    special = ["PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"]
    if mapel in special:
        return "Disusun untuk 1 kali pertemuan tuntas (Blok Jam Pelajaran)."
    # Mapel umum dibagi per 2 JP
    return "Materi dibagi rapi per 2 Jam Pelajaran (JP) per pertemuan (Deep Learning)."

# --- ANTARMUKA APLIKASI (UI) ---
st.set_page_config(page_title="Gen-Admin Guru 2025", layout="wide")
st.title("🚀 Auto-Admin Guru 2025 (Permen No. 13)")
st.write("Sistem otomatis Prota, Promes, ATP, dan Modul Ajar (MA)")

# Sidebar Identitas
with st.sidebar:
    st.header("📋 Identitas Sekolah & Guru")
    nama_sekolah = st.text_input("Nama Sekolah", "SD Negeri ...")
    nama_guru = st.text_input("Nama Guru", "Nama Anda, S.Pd.")
    nip = st.text_input("NIP/NUPTK", "19xxxxxx")
    kepsek = st.text_input("Kepala Sekolah", "Nama Kepsek, M.Pd.")
    
    st.divider()
    st.header("📚 Setting Mapel")
    mapel = st.selectbox("Mata Pelajaran", ["Bahasa Indonesia", "Matematika", "IPAS", "PABP", "PJOK", "Bahasa Inggris", "Bahasa Jawa"])
    kelas = st.text_input("Kelas", "4")
    fase = st.text_input("Fase", "B")
    
    st.info(f"Logika JP: {get_subject_logic(mapel)}")

# Penyimpanan data antar tahapan
if 'data_generate' not in st.session_state:
    st.session_state.data_generate = {}

# --- FUNGSI GENERATE AI ---
def generate_ai_content(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- TAB PROSES ---
tab1, tab2, tab3, tab4 = st.tabs(["1. PROTA", "2. PROMES", "3. CP/TP/ATP", "4. MODUL AJAR"])

# TAB 1: PROTA
with tab1:
    if st.button("Generate PROTA"):
        prompt = f"Buatlah Tabel Program Tahunan (PROTA) {mapel} Kelas {kelas} Fase {fase} Kurikulum Merdeka sesuai Permendikdasmen 13/2025. Acuan buku: https://buku.kemendikdasmen.go.id/katalog. Berikan alokasi JP setahun."
        with st.spinner("Sedang membuat Prota..."):
            st.session_state.data_generate['prota'] = generate_ai_content(prompt)
    
    if 'prota' in st.session_state.data_generate:
        st.markdown(st.session_state.data_generate['prota'])

# TAB 2: PROMES
with tab2:
    if 'prota' not in st.session_state.data_generate:
        st.warning("Buat PROTA dulu!")
    else:
        if st.button("Generate PROMES"):
            prompt = f"Berdasarkan Prota ini: {st.session_state.data_generate['prota']}, buatkan Program Semester (PROMES) ganjil dan genap dalam format tabel mingguan."
            with st.spinner("Sedang membuat Promes..."):
                st.session_state.data_generate['promes'] = generate_ai_content(prompt)
        
        if 'promes' in st.session_state.data_generate:
            st.markdown(st.session_state.data_generate['promes'])

# TAB 3: CP, TP, ATP
with tab3:
    if 'promes' not in st.session_state.data_generate:
        st.warning("Buat PROMES dulu!")
    else:
        if st.button("Generate CP, TP & ATP"):
            prompt = f"Buatlah breakdown Capaian Pembelajaran (CP), Tujuan Pembelajaran (TP), dan Alur Tujuan Pembelajaran (ATP) untuk {mapel} Kelas {kelas}. Pastikan tujuan pembelajaran terukur."
            with st.spinner("Menganalisis Kompetensi..."):
                st.session_state.data_generate['atp'] = generate_ai_content(prompt)
        
        if 'atp' in st.session_state.data_generate:
            st.markdown(st.session_state.data_generate['atp'])

# TAB 4: MODUL AJAR
with tab4:
    if 'atp' not in st.session_state.data_generate:
        st.warning("Buat ATP dulu!")
    else:
        if st.button("Generate Modul Ajar Lengkap"):
            logic_jp = get_subject_logic(mapel)
            prompt = f"""Buatlah Modul Ajar (MA) Lengkap untuk {mapel} Kelas {kelas}. 
            Aturan Pembagian Waktu: {logic_jp}.
            Wajib mencakup:
            1. Identitas, Profil Pelajar (8 Dimensi Permen 13/2025).
            2. Langkah Pembelajaran detail per pertemuan.
            3. Bahan Ajar Materi.
            4. Asesmen Formatif & Sumatif.
            5. Referensi Buku: https://buku.kemendikdasmen.go.id/katalog.
            Format rapi, spasi rata, bahasa formal."""
            
            with st.spinner("Membuat Modul Ajar..."):
                st.session_state.data_generate['modul'] = generate_ai_content(prompt)
        
        if 'modul' in st.session_state.data_generate:
            st.markdown(st.session_state.data_generate['modul'])
            
            # FITUR PDF
            if st.button("📥 Unduh PDF Siap Cetak"):
                pdf = AdminPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                
                # Identitas di dalam kertas
                pdf.cell(0, 7, f"Mata Pelajaran: {mapel}", 0, 1)
                pdf.cell(0, 7, f"Satuan Pendidikan: {nama_sekolah}", 0, 1)
                pdf.cell(0, 7, f"Guru: {nama_guru}", 0, 1)
                pdf.ln(10)
                
                # Menggabungkan konten
                full_content = f"--- PROTA ---\n{st.session_state.data_generate['prota']}\n\n--- MODUL AJAR ---\n{st.session_state.data_generate['modul']}"
                
                # Proses cetak teks panjang
                pdf.multi_cell(0, 5, full_content.encode('latin-1', 'replace').decode('latin-1'))
                
                # Tanda Tangan
                pdf.ln(20)
                pdf.cell(90, 7, "Mengetahui,", 0, 0, 'C')
                pdf.cell(90, 7, "Guru Mata Pelajaran,", 0, 1, 'C')
                pdf.cell(90, 7, "Kepala Sekolah", 0, 0, 'C')
                pdf.ln(20)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(90, 7, kepsek, 0, 0, 'C')
                pdf.cell(90, 7, nama_guru, 0, 1, 'C')
                
                pdf_output = "Administrasi_Lengkap_2025.pdf"
                pdf.output(pdf_output)
                with open(pdf_output, "rb") as f:
                    st.download_button("Klik untuk Simpan PDF", f, file_name=pdf_output)
