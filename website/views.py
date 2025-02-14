from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from flask_login import login_required, current_user
from datetime import datetime
from . import db
from .models import Diary
from .forms import DiaryForm
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pickle


# Create a Blueprint named 'views'
views = Blueprint('views', __name__)


# Define the welcome function for the homepage route
@views.route('/')
def welcome():
    return render_template('welcome.html', user=current_user)

# Define routes for other pages such as Categories, normal, obese, overweight, underweight
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
    # Get the user's data
    user = current_user
    email = user.email
    first_name = user.first_name
     
    # Query diary entries for the current user
    diary_entries = Diary.query.filter_by(user_id=user.id).order_by(Diary.date.desc()).all()
    
    # Get current date
    current_date = datetime.utcnow().date()

    diary_entries_serializable = [entry.to_dict() for entry in diary_entries]

    return render_template('account.html', user=user, email=email, first_name=first_name, diary_entries=diary_entries, current_date=current_date, diary_entries_serializable=diary_entries_serializable)



@views.route('/delete-diary/<int:diary_id>', methods=['POST'])
@login_required
def delete_diary(diary_id):
    diary = Diary.query.get_or_404(diary_id)

    # ตรวจสอบว่าไดอารี่เป็นของผู้ใช้ที่ล็อกอินอยู่หรือไม่
    if diary.user_id != current_user.id:
        flash('You do not have permission to delete this entry.', category='error')
        return redirect(url_for('views.account'))

    db.session.delete(diary)
    db.session.commit()
    flash('Diary entry deleted successfully!', category='success')

    return redirect(url_for('views.account'))



# โหลดโมเดลและ Tokenizer
MODEL_PATH = 'model.h5'
TOKENIZER_PATH = 'tokenizer.pkl'

model = tf.keras.models.load_model(MODEL_PATH)

with open(TOKENIZER_PATH, 'rb') as handle:
    tokenizer = pickle.load(handle)

# ฟังก์ชันทำนาย level
def predict_level(input_text):
    max_length = 32
    input_sequence = tokenizer.texts_to_sequences([input_text])
    padded_input_sequence = pad_sequences(input_sequence, maxlen=max_length, padding='post')
    prediction = model.predict(padded_input_sequence)
    level_labels = ['minimum', 'mild', 'moderate', 'severe']
    predicted_label_index = np.argmax(prediction)
    return level_labels[predicted_label_index]


# อัปเดต route สำหรับหน้า diary
@views.route('/diary', methods=['GET', 'POST'])
@login_required
def diary():
    form = DiaryForm()
    predicted_level = None  
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        date = datetime.utcnow().date()

        # ทำนาย level
        predicted_level = predict_level(content) 

        # บันทึก level ลงใน session
        session['predicted_level'] = predicted_level

        # บันทึกลง Database
        new_entry = Diary(
            title=title, 
            content=content, 
            date=date, 
            level=predicted_level, 
            user_id=current_user.id
        )
        db.session.add(new_entry)
        db.session.commit()

        return redirect(url_for('views.diary'))

    today = datetime.utcnow().date()
    predicted_level = session.pop('predicted_level', None)
    
    return render_template(
        'diary.html', 
        user=current_user, 
        form=form, 
        today=today, 
        predicted_level=predicted_level
    )
