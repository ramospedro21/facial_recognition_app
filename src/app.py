from flask import Flask, render_template, request, jsonify
import cv2
import face_recognition
import numpy as np
import os
from PIL import Image
import io

app = Flask(__name__)

# Carregar faces autorizadas
authorized_faces = {}
authorized_faces_dir = "data/authorized_faces"

for filename in os.listdir(authorized_faces_dir):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        name = os.path.splitext(filename)[0]
        image_path = os.path.join(authorized_faces_dir, filename)
        face_image = face_recognition.load_image_file(image_path)
        face_encoding = face_recognition.face_encodings(face_image)[0]
        
        # Definir nível de acesso baseado no nome do arquivo
        if "pedro" in name.lower():
            access_level = 3
        elif "diretor" in name.lower():
            access_level = 2
        else:
            access_level = 1
        
        authorized_faces[name] = {
            "encoding": face_encoding,
            "access_level": access_level
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    img = Image.open(file.stream)
    img_array = np.array(img)
    
    # Converter para RGB (face_recognition usa RGB)
    rgb_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    
    # Localizar faces na imagem
    face_locations = face_recognition.face_locations(rgb_img)
    face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
    
    results = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces([data["encoding"] for data in authorized_faces.values()], face_encoding)
        name = "Desconhecido"
        access_level = 0
        
        if True in matches:
            matched_indexes = [i for i, match in enumerate(matches) if match]
            names = list(authorized_faces.keys())
            
            for idx in matched_indexes:
                name = names[idx]
                access_level = authorized_faces[name]["access_level"]
                break  # Pega o primeiro match
        
        results.append({
            "name": name,
            "access_level": access_level
        })
    
    return jsonify({
        "recognized": len(results) > 0,
        "results": results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)