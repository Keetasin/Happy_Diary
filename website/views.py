from flask import Blueprint, render_template, flash, redirect, url_for, session, request, jsonify
from .image_caption import load_model_and_tokenizer, extract_features, generate_caption
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask_login import login_required, current_user
from deep_translator import GoogleTranslator
from .models import Diary, ChatHistory
from langdetect import detect
from datetime import datetime
from flask import current_app
from .forms import DiaryForm
import tensorflow as tf
import numpy as np
from . import db
import ollama
import pickle
import uuid
import pytz
import re
import os

views = Blueprint('views', __name__)

@views.route('/')
def welcome():
    return render_template('welcome.html', user=current_user)

@views.route('/level')
def level():
    return render_template('level.html', user=current_user)

@views.route('/tips')
def tips():
    return render_template('tips.html', user=current_user)

@views.route('/stress-relief')
def stress_relief():
    return render_template('stress-relief.html', user=current_user)

@views.route('/self-help')
def self_help():
    return render_template('self-help.html', user=current_user)

@views.route('/therapy')
def therapy():
    return render_template('therapy.html', user=current_user)

from collections import Counter

@views.route('/account')
@login_required
def account():
    user = current_user
    email = user.email
    first_name = user.first_name
    diary_entries = Diary.query.filter_by(user_id=user.id).order_by(Diary.date.desc()).all()
    # print ทั้งหมดเป็น dict
    for entry in diary_entries:
        print(entry.to_dict())

    current_date = datetime.now(pytz.timezone('Asia/Bangkok')).date()
    diary_entries_serializable = [entry.to_dict() for entry in diary_entries]

    # Count depression levels
    levels = [entry.level for entry in diary_entries]
    level_counts = Counter(levels)
    level_data = {
        'minimum': level_counts.get('minimum', 0),
        'mild': level_counts.get('mild', 0),
        'moderate': level_counts.get('moderate', 0),
        'severe': level_counts.get('severe', 0)
    }

    return render_template(
        'account.html', 
        user=user, 
        email=email, 
        first_name=first_name, 
        diary_entries=diary_entries, 
        current_date=current_date, 
        diary_entries_serializable=diary_entries_serializable,
        level_data=level_data
    )

@views.route('/delete-diary/<int:diary_id>', methods=['POST'])
@login_required
def delete_diary(diary_id):
    diary = Diary.query.get_or_404(diary_id)

    if diary.user_id != current_user.id:
        flash('You do not have permission to delete this entry.', category='error')
        return redirect(url_for('views.account'))
    
    if diary.image_filename:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], diary.image_filename)
        if os.path.exists(image_path):  
            os.remove(image_path)  

    db.session.delete(diary)
    db.session.commit()
    flash('Diary entry deleted successfully!', category='success')

    return redirect(url_for('views.account'))


IMAGE_CAPTION_MODEL_PATH = "model/image_caption/mymodel.keras"
IMAGE_CAPTION_TOKENIZER_PATH = "model/image_caption/tokenizer.pkl"
caption_model, caption_tokenizer = load_model_and_tokenizer(IMAGE_CAPTION_MODEL_PATH, IMAGE_CAPTION_TOKENIZER_PATH)

MODEL_PATH = 'model/depression/model.h5'
TOKENIZER_PATH = 'model/depression/tokenizer.pkl'

model = tf.keras.models.load_model(MODEL_PATH)

with open(TOKENIZER_PATH, 'rb') as handle:
    tokenizer = pickle.load(handle)

def predict_level(input_text):
    max_length = 32
    input_sequence = tokenizer.texts_to_sequences([input_text])
    padded_input_sequence = pad_sequences(input_sequence, maxlen=max_length, padding='post')
    prediction = model.predict(padded_input_sequence)
    level_labels = ['minimum', 'mild', 'moderate', 'severe']
    predicted_label_index = np.argmax(prediction)
    return level_labels[predicted_label_index]

def clean_text(text):
    text = text.lower()  
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^\u0E00-\u0E7Fa-z\s]', '', text)  
    return text


def detect_language(text):
    try:
        # ตรวจสอบภาษา
        return detect(text)
    except Exception as e:
        print(f"Error in language detection: {e}")
        return None

def translate_to_english(text):
    try:
        # แปลข้อความเป็นภาษาอังกฤษ
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except Exception as e:
        print(f"Error in translation: {e}")
        return text

    
@views.route('/diary', methods=['GET', 'POST'])
@login_required
def diary():
    form = DiaryForm()
    predicted_level = None  
    image_filename = None
    image_caption = None
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        date = datetime.now(pytz.timezone('Asia/Bangkok')).date()

        if form.image.data:
            image_file = form.image.data
            if image_file.filename != '':  
                file_extension = os.path.splitext(image_file.filename)[1]  
                unique_filename = f"{uuid.uuid4().hex}{file_extension}"  
                
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                while os.path.exists(image_path):  
                    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                
                image_file.save(image_path)  

                photo_feature = extract_features(image_path).reshape((1, -1))
                image_caption = generate_caption(caption_model, caption_tokenizer, photo_feature)
                
                image_filename = unique_filename  


        language = detect_language(content)
        if language != 'en':  
            content_en = translate_to_english(content)  
        else: 
            content_en = content

        combined_text = content_en + " " + (image_caption if image_caption is not None else "")
        cleaned_text = clean_text(combined_text)
        predicted_level = predict_level(cleaned_text)

        new_entry = Diary(
            title=title, 
            content=content, 
            date=date, 
            level=predicted_level,
            image_filename=image_filename,
            image_caption=image_caption, 
            user_id=current_user.id
        )
        db.session.add(new_entry)
        db.session.commit()

        session['latest_diary'] = {
            'title': new_entry.title,
            'content': new_entry.content,
            'level': new_entry.level,
            'image_filename': new_entry.image_filename,
            'image_caption': new_entry.image_caption,
        }

        return redirect(url_for('views.diary'))

    today = datetime.now(pytz.timezone('Asia/Bangkok')).date()
    predicted_level = session.pop('predicted_level', None)
    
    latest_diary = session.pop('latest_diary', None)
    
    return render_template(
        'diary.html', 
        user=current_user, 
        form=form, 
        today=today, 
        predicted_level=predicted_level,
        latest_diary=latest_diary
    )



@views.route('/ask-llama', methods=['POST'])
@login_required
def ask_llama():
    try:
        input_data = request.get_json()
        if not input_data or "question" not in input_data:
            return jsonify({"error": "Invalid input. Please provide a question."}), 400

        question = input_data["question"]
        
        # บันทึกคำถามของผู้ใช้ลงใน Database
        user_id = current_user.id
        user_message = ChatHistory(user_id=user_id, message=question, role='user')
        db.session.add(user_message)
        db.session.commit()
        
        # ส่งคำถามไปให้โมเดล LLaMA
        response = ollama.chat(model='llama3', messages=[{"role": "user", "content": question}])
        bot_response = response['message']['content']

        # บันทึกคำตอบของบอทลงใน Database
        bot_message = ChatHistory(user_id=user_id, message=bot_response, role='bot')
        db.session.add(bot_message)
        db.session.commit()
        
        return jsonify({"response": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@views.route('/chatbot')
@login_required  
def chatbot_page():
    chat_history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.asc()).all()
    
    # จัดกลุ่มข้อมูลตามวัน
    chat_data = []
    current_date = None
    for chat in chat_history:
        chat_date = chat.timestamp.strftime('%d %B %Y') 
        if chat_date != current_date:
            chat_data.append({"date": chat_date, "messages": []})
            current_date = chat_date
        chat_data[-1]["messages"].append({"message": chat.message, "role": chat.role, "timestamp": chat.timestamp})
    
    return render_template('chat.html', user=current_user, chat_data=chat_data)


