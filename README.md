# 241-202 MACHINE LEARNING II - 2/67

## Mini Project: Depression Level Analysis from Diary Entries

### 📖 Project Overview
This project is a **web-based diary application** designed to generate **image captions** and analyze them alongside diary entries to assess **depression levels**.  
The system classifies depression into four stages:

- **Minimum** 😊  
- **Mild** 😐  
- **Moderate** 😕  
- **Severe** 😢  

Additionally, the system provides **recommendations based on depression levels** to support users' mental well-being.

---

### 🔧 Features  
- **User Authentication** – login and registration system  
- **Image Captioning** – Automatically generate captions for uploaded images  
- **Depression Level Prediction** – Analyze depression levels from images and diary text  
- **Personalized Recommendations** – Provide suggestions based on depression levels  
- **Diary Management** – Add, delete, and manage diary entries with images  
- **User Dashboard** – Track and analyze depression trends over time


---

### 🧠 Deep Learning Models

- Depression Level Prediction Model
   -  Uses **LSTM** to analyze diary text  
   - Loaded from: model/depression/model.h5  

- Image Captioning Model
   - Uses **VGG16** and **LSTM**  
   - Loaded from: model/image_caption/mymodel.keras

---

### 📌 Setup & Installation
Ensure that you have Python installed on your system before proceeding.

1. Clone the repository:
   ```bash
   git clone <repo-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd <project-folder>
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### 🚀 Running and Viewing the Application

1. Ensure you are inside the project directory.
2. Run the application:
   ```bash
   python main.py
   ```
3. Open your browser and go to:
   ```
   http://127.0.0.1:5000
   ```
