from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_required, current_user
from datetime import datetime
from . import db
from .models import Diary
from .forms import DiaryForm
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pickle
import os
from flask import current_app
from .image_caption import load_model_and_tokenizer, extract_features, generate_caption
import uuid


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

@views.route('/account')
@login_required
def account():
    user = current_user
    email = user.email
    first_name = user.first_name
    diary_entries = Diary.query.filter_by(user_id=user.id).order_by(Diary.date.desc()).all()
    current_date = datetime.utcnow().date()
    diary_entries_serializable = [entry.to_dict() for entry in diary_entries]

    return render_template('account.html', user=user, email=email, first_name=first_name, diary_entries=diary_entries, current_date=current_date, diary_entries_serializable=diary_entries_serializable)

@views.route('/delete-diary/<int:diary_id>', methods=['POST'])
@login_required
def delete_diary(diary_id):
    diary = Diary.query.get_or_404(diary_id)

    if diary.user_id != current_user.id:
        flash('You do not have permission to delete this entry.', category='error')
        return redirect(url_for('views.account'))

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
        date = datetime.utcnow().date()

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

        predicted_level = predict_level(content + " " + (image_caption if image_caption is not None else ""))
        print(f"content: {content}, image_caption: {image_caption}")

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

    today = datetime.utcnow().date()
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
