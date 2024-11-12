from datetime import datetime
import os

from admin_chatbot.models import FileUpload, WhatsAppContact

def get_current_greeting(name):
    # Mendapatkan waktu saat ini
    current_time = datetime.now().time()
    
    kalimat_pembuka = ("Selamat datang di layanan informasi desa Bangsri kab. Brebes! 🤖\n"
                        "Saya siap membantu Anda mendapatkan informasi yang Anda butuhkan. \n\n"
                        # "Berikut beberapa topik yang bisa Anda tanyakan:\n\n"
                        # "\t1. \t💵\n"
                        # "\t2. \t🎓\n"
                        # "\t3. \t🌐\n"
                        # "\t4. \t♾️\n\n"
                        "Untuk mengetahui topik yang bisa ditanyakan ketik */info* !\n")
    
    # Rentang waktu untuk sapaan
    time_ranges = {
        "morning": (("00:00", "10:00"), f"Sugeng enjing, {name}! \n{kalimat_pembuka}"),
        "noon": (("10:01", "14:00"), f"Sugeng siang, {name}! \n{kalimat_pembuka}"),
        "afternoon": (("14:01", "18:00"), f"Sugeng sonten, {name}! \n{kalimat_pembuka}"),
        "evening": (("18:01", "23:59"), f"Sugeng dalu, {name}! \n{kalimat_pembuka}")
    }

    # Loop melalui rentang waktu untuk mencari sapaan yang sesuai
    for period, (time_range, greeting) in time_ranges.items():
        start_time, end_time = [datetime.strptime(t, "%H:%M").time() for t in time_range]
        if start_time <= current_time <= end_time:
            return greeting

def info():
    top_5_file = FileUpload.objects.order_by('-count_retrieved')[:10]
    
    answer =  "Kamu bisa bertanya tentang informasi mengenai Desa Bangsri.\n"
    
    if top_5_file != []:
        answer += "Berikut merupakan beberapa contoh hal yang paling sering ditanyakan.\n\n"
        
        for file in top_5_file:
            file_name = remove_extension(file.file_name)
            answer += f"- {file_name}\n"
            
    return answer

def save_whatsapp_contact(name, phone_number):
    
    # Menyimpan atau memperbarui data kontak di database
    WhatsAppContact.objects.update_or_create(
        wa_id=phone_number,
        defaults={
            "name": name,
            "phone_number": phone_number,
        }
    )


def remove_extension(file_name):
    return os.path.splitext(file_name)[0]