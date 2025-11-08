from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import torch
import tensorflow as tf

app = FastAPI()

origins = [
    "http://192.168.43.231",
    "http://192.168.43.231:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement du modèle YOLOv5 personnalisé
YOLO_MODEL = torch.hub.load('ultralytics/yolov5', 'custom', path='yolo/yolov5/runs/train/exp19/weights/best.pt')

# Classes pour YOLOv5 (ajustez selon vos besoins)
YOLO_CLASSES = ['Riz', 'Mais']  # Remplacez par les noms réels de vos classes

@app.get("/ping")
async def ping():
    return {"message": "Bonjour, c'est Bamba, développeur"}

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image

@app.post("/Identification")
async def detect(file: UploadFile = File(...)):
    # Lire l'image téléchargée
    image = read_file_as_image(await file.read())
    
    # Convertir l'image en un format compatible avec le modèle YOLOv5
    img = Image.fromarray(image)
    
    # Effectuer la détection avec YOLOv5
    results = YOLO_MODEL(img)
    
    # Traiter les résultats avec un seuil de confiance ajusté
    detections = results.pandas().xyxy[0]
    detections = detections[detections['confidence'] > 0.1].to_dict(orient="records")
    
    # Extraire les informations pertinentes des détections
    output = []
    for detection in detections:
        output.append({
            'class': detection['name'],
            'confidence': float(detection['confidence']),
            'box': {
                'xmin': int(detection['xmin']),
                'ymin': int(detection['ymin']),
                'xmax': int(detection['xmax']),
                'ymax': int(detection['ymax']),
            }
        })
    
    return {'detections': output}

model = tf.keras.models.load_model('model/model.h5')
# Endpoint pour la détection des carences en Azote
@app.post("/All")
async def predict_all_nutrients(file: UploadFile = File(...)):
    # Définir les dimensions d'image attendues par le modèle
    img_height, img_width = 224, 224  # Remplacez ces valeurs par les dimensions correctes pour votre modèle
    
    # Liste des noms de nutriments
    nutrient_names = [
        'Azote', 'Bore', 'Calcium', 'Chlore', 'Cuivre', 'Fer', 'Manganèse',
        'Magnésium', 'Molybdène', 'Phosphore', 'Potassium', 'Soufre', 'Zinc'
    ]
    
    # Lire l'image téléchargée
    image = read_file_as_image(await file.read())
    
    # Préparer l'image pour le modèle
    img = Image.fromarray(image).resize((img_height, img_width))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Créer un batch de taille 1
    
    # Faire des prédictions
    predictions = model.predict(img_array)
    
    # Définir les niveaux de carence
    deficiency_levels = ['absent', 'legere', 'severe']  # Correspond aux classes utilisées dans votre modèle

    # Préparer les résultats
    results = {}

    # Obtenir le niveau de carence avec le pourcentage le plus élevé pour chaque nutriment
    for i, prediction in enumerate(predictions):
        highest_index = np.argmax(prediction[0])
        results[nutrient_names[i]] = {
            'level': deficiency_levels[highest_index],
            'percentage': prediction[0][highest_index] * 100
        }

    return results

# Endpoint pour la détection des carences en Azote
@app.post("/Azote")
async def predict_azote(file: UploadFile = File(...)):
    # Définir les dimensions d'image attendues par le modèle
    img_height, img_width = 224, 224  # Remplacez ces valeurs par les dimensions correctes pour votre modèle
    
    # Définir les niveaux de carence
    deficiency_levels = ["absent", "léger", "sévère"]  # Assurez-vous que ces niveaux correspondent à ceux utilisés dans votre modèle
    
    # Lire l'image téléchargée
    image = read_file_as_image(await file.read())
    
    # Préparer l'image pour le modèle
    img = Image.fromarray(image).resize((img_height, img_width))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Créer un batch de taille 1
    
    # Faire des prédictions
    predictions = model.predict(img_array)
    
    # Obtenir le niveau de carence avec le pourcentage le plus élevé pour l'Azote
    azote_prediction = predictions[0][0]  # Assurez-vous que cela correspond à l'ordre des nutriments dans votre modèle
    highest_index = np.argmax(azote_prediction)
    
    result = {
        'nutrient': 'Azote',
        'level': deficiency_levels[highest_index],
        'percentage': azote_prediction[highest_index] * 100
    }
    
    return result
@app.post("/Bore")
async def predict_bore(file: UploadFile = File(...)):
    # Définir les dimensions d'image attendues par le modèle
    img_height, img_width = 224, 224  # Remplacez ces valeurs par les dimensions correctes pour votre modèle
    
    # Définir les niveaux de carence
    deficiency_levels = ["absent", "léger", "sévère"]  # Assurez-vous que ces niveaux correspondent à ceux utilisés dans votre modèle
    
    # Lire l'image téléchargée
    image = read_file_as_image(await file.read())
    
    # Préparer l'image pour le modèle
    img = Image.fromarray(image).resize((img_height, img_width))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Créer un batch de taille 1
    
    # Faire des prédictions
    predictions = model.predict(img_array)
    
    # Obtenir le niveau de carence avec le pourcentage le plus élevé pour l'Azote
    bore_prediction = predictions[0][0]  # Assurez-vous que cela correspond à l'ordre des nutriments dans votre modèle
    highest_index = np.argmax(azote_prediction)
    
    result = {
        'nutrient': 'Bore',
        'level': deficiency_levels[highest_index],
        'percentage': _prediction[highest_index] * 100
    }
    
    return result

if __name__ == "__main__":
    uvicorn.run(app, host='192.168.43.231', port=8000)
