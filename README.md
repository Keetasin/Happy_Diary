# 241-202 MACHINE LEARNING II - 2/67

## Mini Project: Depression Level Analysis from Diary Entries

### 📖 Project Overview
This project is a **web-based diary application** designed to generate **image captions** and analyze them alongside diary entries to assess **depression levels**.  
The system classifies depression into four stages:

- **Minimum** 😊  
- **Mild** 😐  
- **Moderate** 😕  
- **Severe** 😢  

In addition, the system provides **recommendations based on the depression level** and includes **a chatbot (LLaMA)** to offer preliminary advice that supports users' mental well-being. **A dashboard** is also available to track and analyze depression trends over time.

---

### 🔧 Features  
- **User Authentication** – login and registration system  
- **Image Captioning** – Automatically generate captions for uploaded images  
- **Depression Level Prediction** – Analyze depression levels from images and diary text  
- **Personalized Recommendations** – Provide suggestions based on depression levels 
- **Chatbot (LLaMA)** – Ask any question via LLaMA-powered chatbot 
- **Text-to-Speech (TTS)** – Clickable icon to hear chatbot replies aloud
- **Diary Management** – Add, delete, and manage diary entries with images  
- **User Dashboard** – Track and analyze depression trends over time

---

### 🧠 Deep Learning Models

- **Depression Level Prediction Model**
   - Uses **LSTM** 
   - **Accuracy**: **0.80**  
   - Loaded from: model/depression/model.h5  

- **Image Captioning Model**
   - Uses **VGG16** and **LSTM**  
   - **BLEU Scores**:  
      - BLEU-1: **0.555093**  
      - BLEU-2: **0.326121**  
   - Loaded from: model/image_caption/mymodel.keras

- **Chatbot Response Model**  
   - Architecture: Meta's LLaMA 3  
   - Usage: Used for interactive chatbot responses  
   - Access: Called via API (`ollama.chat(model='llama3')`)

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
4. Install and set up Meta's LLaMA 3 locally using [Ollama](https://ollama.com/):
 - Download and install Ollama: For Windows/macOS/Linux: https://ollama.com/download
 - Pull the LLaMA 3 model: 
    ```bash
   ollama pull llama3
   ```
 - Run the model server: ollama run llama3
   ```bash
   ollama run llama3
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