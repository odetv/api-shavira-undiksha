import requests
from bs4 import BeautifulSoup
import time

def scrape_with_beautifulsoup(url):
    # Kirim permintaan HTTP ke halaman web
    response = requests.get(url)

    # Periksa apakah permintaan berhasil (status code 200)

    # Parsing halaman HTML menggunakan BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ambil judul halaman
    title = soup.title.string

    # Ambil contoh elemen lain, misalnya semua paragraf <p>
    paragraphs = soup.find_all('p')

    # Cetak judul halaman
    print(f"Title: {title}")

    # Cetak semua paragraf (atau bisa diproses lebih lanjut)
    for i, p in enumerate(paragraphs, 1):
        print(f"Paragraph {i}: {p.get_text()}")


# Penggunaan fungsi
url = "https://ojs.unud.ac.id/index.php/EEB"  # Ganti dengan URL yang ingin di-scrape
scrape_with_beautifulsoup(url)
