# Bridge Failure Simulator

## 1. Project Overview

Bridge Failure Simulator merupakan aplikasi simulasi berbasis Python yang digunakan untuk menganalisis pengaruh penutupan jembatan atau ruas jalan terhadap konektivitas jaringan jalan.

Proyek ini menggunakan teori graf untuk merepresentasikan jaringan jalan, dengan lokasi atau persimpangan sebagai simpul (*node*) dan ruas jalan sebagai sisi (*edge*). Melalui simulasi penutupan ruas jalan, pengguna dapat mengamati perubahan keterhubungan jaringan.

Aplikasi dikembangkan menggunakan Python, NetworkX, dan Streamlit serta dilengkapi visualisasi interaktif untuk membandingkan kondisi jaringan sebelum dan sesudah penutupan.

## 2. Background and Objectives

Jaringan jalan memiliki peran penting dalam menghubungkan berbagai lokasi. Penutupan jembatan atau ruas jalan tertentu dapat menyebabkan perubahan konektivitas, bahkan memisahkan jaringan menjadi beberapa bagian yang tidak lagi saling terhubung.

Oleh karena itu, proyek ini dibuat untuk memodelkan dan menyimulasikan dampak penutupan ruas jalan menggunakan pendekatan teori graf.

Tujuan proyek:
- Merepresentasikan jaringan jalan dalam bentuk graf.
- Mengidentifikasi ruas jalan yang berperan sebagai *bridge* dalam teori graf.
- Mengetahui perubahan jumlah komponen terhubung akibat penutupan ruas jalan.
- Menyediakan aplikasi interaktif untuk mengamati hasil simulasi.

## 3. Dataset and Data Source

Dataset jaringan jalan diperoleh dari **OpenStreetMap (OSM)** dan diambil menggunakan pustaka OSMnx.

Lokasi penelitian berada di sekitar Richmond Bridge, Richmond, London, Inggris.

Pengambilan data menggunakan tipe jaringan `drive`, yaitu jaringan jalan yang dapat dilalui kendaraan.

Karakteristik data:
- Jumlah simpul pada graf awal: 555 node.
- Jumlah sisi pada graf awal: 1.187 directed edges.
- Jumlah sisi dengan atribut jembatan: 10 directed edges.
- Jumlah simpul pada graf sampel: 15 node.
- Jumlah sisi pada graf sampel: 26 directed edges.

Graf sampel dipilih dari jaringan jalan yang diperoleh melalui OpenStreetMap dan digunakan untuk menjalankan simulasi.

## 4. Graph Modeling

Jaringan jalan dimodelkan sebagai graf menggunakan pustaka NetworkX.

Representasi graf:
- **Node:** lokasi atau persimpangan jalan.
- **Edge:** hubungan antar lokasi melalui ruas jalan.
- **Graf awal:** jaringan jalan hasil pemilihan 15 simpul.
- **Graf analisis:** graf tidak berarah yang digunakan untuk menganalisis konektivitas.

Graf yang digunakan untuk analisis konektivitas dibentuk melalui konversi menggunakan `nx.Graph()`.

## 5. Algorithms

Proyek ini menggunakan dua algoritma utama:

### 5.1 Connected Components

Algoritma Connected Components digunakan untuk mengetahui kelompok simpul yang masih saling terhubung dalam jaringan.

Algoritma ini digunakan untuk membandingkan jumlah komponen terhubung sebelum dan sesudah penutupan ruas jalan.

### 5.2 Bridge Detection

Algoritma Bridge Detection digunakan untuk mengidentifikasi sisi yang apabila dihapus akan menambah jumlah komponen terhubung pada graf tidak berarah.

Algoritma ini membantu menentukan ruas jalan yang memiliki pengaruh terhadap konektivitas jaringan.

## 6. Application Features

Aplikasi Bridge Failure Simulator memiliki beberapa fitur:
- Memilih skenario penutupan ruas jalan.
- Menampilkan visualisasi jaringan sebelum penutupan.
- Menampilkan visualisasi jaringan setelah penutupan.
- Memperlihatkan komponen terhubung dengan warna berbeda.
- Menampilkan jumlah node dan komponen terhubung.
- Membandingkan hasil dari dua skenario simulasi.

## 7. Testing Scenarios

Pengujian dilakukan menggunakan dua skenario penutupan ruas jalan.

### Scenario 1: Richmond Bridge Closure

Pada skenario pertama, sisi yang merepresentasikan Richmond Bridge dihapus dari graf.

Hasil:
- Jumlah komponen sebelum penutupan: 1.
- Jumlah komponen setelah penutupan: 2.
- Ukuran komponen yang terbentuk: 10 dan 5 node.

Hasil tersebut menunjukkan bahwa penutupan Richmond Bridge menyebabkan jaringan sampel terpisah menjadi dua komponen terhubung.

### Scenario 2: Alternative Road Closure

Pada skenario kedua, dilakukan penutupan terhadap ruas jalan alternatif yang terdeteksi sebagai *bridge* dalam teori graf.

Hasil:
- Jumlah komponen sebelum penutupan: 1.
- Jumlah komponen setelah penutupan: 2.
- Ukuran komponen yang terbentuk: 14 dan 1 node.

Hasil tersebut menunjukkan bahwa penutupan ruas jalan alternatif menyebabkan satu simpul terpisah dari bagian jaringan lainnya.

## 8. Results and Analysis

Berdasarkan kedua skenario, penutupan ruas jalan dapat menyebabkan perubahan konektivitas jaringan.

Pada skenario pertama, penutupan Richmond Bridge menghasilkan dua komponen dengan ukuran 10 dan 5 node. Sementara itu, pada skenario kedua, penutupan ruas jalan alternatif menghasilkan dua komponen dengan ukuran 14 dan 1 node.

Perbedaan hasil tersebut menunjukkan bahwa setiap ruas jalan dapat memberikan dampak yang berbeda terhadap keterhubungan jaringan.

## 9. Limitations

Proyek ini memiliki beberapa keterbatasan:
- Analisis menggunakan graf sampel yang terdiri dari 15 node.
- Data yang digunakan berfokus pada struktur dan konektivitas jaringan jalan.
- Simulasi belum mempertimbangkan volume kendaraan, kapasitas jalan, waktu tempuh, dan tingkat kemacetan.
- Hasil simulasi menggambarkan perubahan konektivitas secara struktural, bukan kondisi lalu lintas secara langsung.

## 10. Project Structure

File utama dalam proyek ini:

- `app.py` — kode aplikasi Streamlit.
- `data_bridge.pkl` — data graf yang digunakan oleh aplikasi.
- `requirements.txt` — daftar pustaka yang diperlukan.
- `README.md` — dokumentasi proyek.

## 11. How to Run

### Run Online

Aplikasi dapat diakses melalui tautan berikut:

**[Bridge Failure Simulator](https://bridge-failure-simulator-k27awwcdk6esipw26nw2y9.streamlit.app)**

### Run Locally

1. Clone repository:

   ```bash
   git clone https://github.com/barorotulkaromah75-hue/bridge-failure-simulator.git
   ```

2. Masuk ke folder proyek:

   ```bash
   cd bridge-failure-simulator
   ```

3. Install pustaka yang diperlukan:

   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan aplikasi:

   ```bash
   streamlit run app.py
   ```

## 12. Technologies Used

- Python
- NetworkX
- OSMnx
- Pandas
- Plotly
- Streamlit
- OpenStreetMap

---

**Project:** Bridge Failure Simulator  
**Course:** Komputasi Graf  
**Data Source:** OpenStreetMap (OSM)
