import numpy as np
import pickle
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing import image

def load_model_and_tokenizer(model_path, tokenizer_path):
    model = load_model(model_path)
    with open(tokenizer_path, "rb") as f:
        tokenizer = pickle.load(f)
    return model, tokenizer

def extract_features(img_path):
    model = VGG16(weights="imagenet", include_top=True)
    model = Model(inputs=model.input, outputs=model.get_layer("fc2").output)

    img = image.load_img(img_path, target_size=(224, 224))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)

    return model.predict(img)

def generate_caption(model, tokenizer, photo_feature, max_length=34):
    in_text = "startseq"
    for _ in range(max_length):
        sequence = tokenizer.texts_to_sequences([in_text])[0]
        sequence = pad_sequences([sequence], maxlen=max_length, padding="post")
        y_pred = model.predict([photo_feature, sequence], verbose=0)
        y_pred = np.argmax(y_pred)
        word = next((w for w, index in tokenizer.word_index.items() if index == y_pred), None)
        if word is None or word == "endseq":
            break
        in_text += " " + word
    return in_text.replace("startseq", "").replace("endseq", "").strip()
