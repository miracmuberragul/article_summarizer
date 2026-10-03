"""
UI -> kullanıcının soru sorabileceği bir arayüz olacak. Kullanıcı sorusunu yazacak ve sistem cevap verecek.

"""
import streamlit as st
import requests

st.set_page_config(page_title="Gemma Article Chatbot", page_icon=":robot_face:")

st.title("Gemma Article Chatbot")
st.write("PDF yükleyin ve makale hakkında sorular sorun.")

uploaded_file = st.file_uploader("PDF dosyasını yükle", type="pdf")

if uploaded_file is not None:
    # PDF yüklendiğinde
    st.write("PDF yüklendi:", uploaded_file.name)

    # PDF içeriğini işlemek için bir buton ekleyelim
    if st.button("PDF'i İşle"):
        # PDF'i işlemek için FastAPI'ye istek gönder
        response = requests.post("http://localhost:8000/upload_pdf/", files={"file": uploaded_file})
        if response.status_code == 200:
            st.success("PDF başarıyla işlendi.")
        else:
            st.error("PDF işlenirken bir hata oluştu.")
            st.write("Hata mesajı:", response.text)
            st.stop()
        
else:
    st.write("Lütfen bir PDF dosyası yükleyin.")
    st.stop()

# soru sorma alanı
user_question = st.text_input("Sorunuzu yazınız:")

if st.button("Soruyu Gönder"):
    # Kullanıcı sorusunu gönderdiğinde
    response = requests.post("http://localhost:8000/chat/", json={"question": user_question})
    if response.status_code == 200:
        st.write("Cevap:", response.json().get("answer", "Cevap bulunamadı."))
    else:
        st.error("Soru sorulurken bir hata oluştu.")
        st.write("Hata mesajı:", response.text)

        st.stop()

