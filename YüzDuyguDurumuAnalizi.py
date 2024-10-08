#başarım oranını ölçen asıl kodum

import cv2
from deepface import DeepFace
import matplotlib.pyplot as plt
from tkinter import Tk, Button, Label, filedialog
from PIL import Image, ImageTk
from sklearn.metrics import accuracy_score, classification_report
import os

# Yüz tespiti için Haarcascade yükledim
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# Duygu analizi fonksiyonu
def analyze_emotion(image_path):
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    analysis = DeepFace.analyze(img_rgb, actions=['emotion'], enforce_detection=False)

    if isinstance(analysis, list):
        analysis = analysis[0]

    dominant_emotion = analysis['dominant_emotion']
    print("Duygu Analizi Sonuçları:", dominant_emotion)

    plt.imshow(img_rgb)
    plt.title(f"Duygu: {dominant_emotion}")
    plt.axis('off')
    plt.show()


# Dosya açma fonksiyonu
def open_file():
    file_path = filedialog.askopenfilename(title="Bir resim seçin", filetypes=[("Image files", "*.jpg *.jpeg *.png")])

    if file_path:
        img = Image.open(file_path)
        img.thumbnail((250, 250))
        img = ImageTk.PhotoImage(img)
        preview_label.config(image=img)
        preview_label.image = img
        analyze_emotion(file_path)


# Canlı kamera duygu analizi fonksiyonu
def analyze_emotion_live():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kamera açılmadı")
            break

        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        for (x, y, w, h) in faces:
            face_roi = img_rgb[y:y + h, x:x + w]  # Yüz bölgesini kırp

            try:
                analysis = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)

                if isinstance(analysis, list):
                    analysis = analysis[0]

                dominant_emotion = analysis['dominant_emotion']

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f'Duygu: {dominant_emotion}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                            (0, 255, 0), 2)
            except Exception as e:
                print("Analiz hatası:", e)

        cv2.imshow('Kamera - Duygu Durumu Analizi', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Test veri kümesi ile başarı ölçümü
def measure_performance(test_folder):
    true_labels = []  # Gerçek etiketler
    predicted_labels = []  # Tahmin edilen etiketler

    for image_file in os.listdir("C:/Users/utku/Desktop/test_images"):
        if image_file.endswith(('jpg', 'jpeg', 'png')):
            image_path = os.path.join(test_folder, image_file)

            # Gerçek etiketi belirleyin (örneğin, dosya adında olabilir)
            # Örnek: 'happy_image1.jpg' dosya adından 'happy' etiketini çıkarıyoruz
            true_label = image_file.split('_')[0]  # Dosya adından etiketi çıkarma örneği
            true_labels.append(true_label)

            # DeepFace ile duygu analizi yapın
            try:
                img = cv2.imread(image_path)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                analysis = DeepFace.analyze(img_rgb, actions=['emotion'], enforce_detection=False)

                if isinstance(analysis, list):
                    analysis = analysis[0]

                predicted_emotion = analysis['dominant_emotion']
                predicted_labels.append(predicted_emotion)

            except Exception as e:
                print(f"Analiz hatası {image_file}: {e}")

    # Başarım oranı ölçme (Doğruluk, sınıflandırma raporu)
    accuracy = accuracy_score(true_labels, predicted_labels)
    report = classification_report(true_labels, predicted_labels)

    print(f"Doğruluk Oranı: {accuracy}")
    print("Sınıflandırma Raporu:\n", report)


# GUI Arayüzü
root = Tk()
root.title("Duygu Durumu Analizi")
root.geometry("400x400")

select_button = Button(root, text="Fotoğraf Seç", command=open_file)
select_button.pack(pady=20)

camera_button = Button(root, text="Kamera ile Anlık Analiz", command=analyze_emotion_live)
camera_button.pack(pady=20)

# Performans ölçüm butonu
performance_button = Button(root, text="Test Veri Kümesi ile Başarı Ölç", command=lambda: measure_performance('C:/Users/utku/Desktop/test_images'))

performance_button.pack(pady=20)

preview_label = Label(root)
preview_label.pack()

root.mainloop()
