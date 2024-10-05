# Deklarasi variabel global
counter = 0

def increment_counter():
    """Fungsi untuk menambah nilai counter."""
    global counter  # Menggunakan kata kunci global
    counter += 1
    print(f"Counter setelah penambahan: {counter}")

def reset_counter():
    """Fungsi untuk mereset nilai counter ke nol."""
    global counter  # Menggunakan kata kunci global
    counter = 0
    print("Counter telah direset ke nol.")

# Menggunakan fungsi
increment_counter()  # Menambah counter
increment_counter()  # Menambah counter
reset_counter()      # Mereset counter
increment_counter()  # Menambah counter setelah reset
