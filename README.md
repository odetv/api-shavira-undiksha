# SHAVIRA (GANESHA VIRTUAL ASSISTANT)

## Ringkasan

Ganesha Virtual Assistant (Shavira) adalah virtual assistant berbasis teknologi Retrieval-Augmented Generation (RAG) yang dirancang untuk membantu civitas akademika Universitas Pendidikan Ganesha (Undiksha). Shavira memiliki kemampuan untuk memberikan informasi umum terkait Undiksha. Selain itu, asisten ini juga membantu mahasiswa dalam mengakses informasi terkait perkuliahan, layanan mahasiswa, penyelesaian permasalahan akun Undiksha, dan mengikuti berita terbaru yang terjadi di lingkungan kampus. Shavira dikembangkan dengan teknologi AI canggih berbasis Web Application. Hanya dengan satu platform, civitas akademika dapat memperoleh solusi cepat dan efisien dalam memenuhi kebutuhan informasi akademik dan non-akademik di lingkungan Undiksha.

## Apa itu RAG?

![image](https://gradientflow.com/wp-content/uploads/2023/10/newsletter87-RAG-simple.png)
Retrieval-Augmented Generation (RAG) adalah teknik yang dirancang untuk meningkatkan kinerja Large Language Model (LLM) dengan mengakses informasi dari sumber eksternal. Dengan RAG, chatbot dapat memberikan jawaban yang lebih akurat dan relevan, serta mengurangi kemungkinan halusinasi terhadap suatu informasi.

## Alur Kerja RAG

#### 1. Retrieve (Kumpulkan):

- Kueri dari pengguna digunakan untuk mencari konteks relevan dari sumber pengetahuan eksternal.
- Kuery diubah menjadi vektor dan dicocokkan dengan vektor dalam database (sumber pengetahuan juga telah melewati fase ini), sehingga mendapatkan objek data relevan (k untuk objek paling relevan).

#### 2. Augment (Tambahkan):

- Konteks diambil dan digabungkan dengan kueri pengguna menggunakan template prompt.

#### 3. Generate (Hasilkan Respon):

- Prompt yang sudah dimodifikasi struktur datanya dimasukkan ke dalam LLM untuk menghasilkan respons akhir.

## Contoh Implementasi

![image](https://miro.medium.com/v2/resize:fit:828/format:webp/1*h5SO9Hqu1YVYQVEIsWGZBg.png)
Pertanyaan Pengguna (Kueri) "Apa syarat untuk mendaftar sebagai mahasiswa baru di Undiksha?"

#### 1. Retrieve

Konteks relevan diambil dari database vektor.
Konteks: "Untuk mendaftar sebagai mahasiswa baru di Undiksha, calon mahasiswa harus memiliki ijazah SMA atau sederajat, melengkapi formulir pendaftaran, dan mengikuti ujian masuk."

#### 2. Augment

Gabungkan kuery pengguna dengan konteks yang diambil menggunakan template prompt.
Prompt: "Syarat-syarat pendaftaran mahasiswa baru di UndikshaSyarat-syarat pendaftaran mahasiswa baru di Undiksha adalah sebagai berikut: sebagai berikut: {context}"

#### 3. Generate

LLM memproses prompt tersebut untuk menghasilkan respons lengkap.
Respons Akhir: "Syarat-syarat pendaftaran mahasiswa baru di Undiksha adalah sebagai berikut: Untuk mendaftar sebagai mahasiswa baru di Undiksha, calon mahasiswa harus memiliki ijazah SMA atau sederajat, melengkapi formulir pendaftaran, dan mengikuti ujian masuk."

## Referensi

- [From Basics to Advanced: Exploring LangGraph](https://towardsdatascience.com/from-basics-to-advanced-exploring-langgraph-e8c1cf4db787)
- [Build a Reliable RAG Agent using LangGraph](https://medium.com/the-ai-forum/build-a-reliable-rag-agent-using-langgraph-2694d55995cd)

Developed By [DiarCode11](https://github.com/DiarCode11) & [odetv](https://github.com/odetv)
