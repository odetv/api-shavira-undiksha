import ast

def str_to_list(string_value):
    # Menghapus karakter newline dan spasi yang tidak perlu
    cleaned_string = string_value.strip()

    # Mengubah string menjadi list menggunakan ast.literal_eval
    converted_list = ast.literal_eval(cleaned_string)

    # Menampilkan hasil
    # print(converted_list)
    # print(type(converted_list))  # Menunjukkan bahwa ini adalah list

    return converted_list
