import torch
import torchvision
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from PIL import Image
import cv2
import numpy as np
import os

# Charger le modèle entraîné
model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=None)
in_features = model.roi_heads.box_predictor.cls_score.in_features
model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes=3)
model.load_state_dict(torch.load('faster_rcnn_plant.pth'))
model.eval()

# Chemin vers le dossier de test
test_images = 'dataset/test/images'

# Dictionnaire des classes
classnames = {1: 'Riz', 2: 'Maïs'}

# Fonction pour faire la détection
def detect(image_path):
    img = Image.open(image_path).convert("RGB")
    img_tensor = torchvision.transforms.ToTensor()(img)

    with torch.no_grad():
        prediction = model([img_tensor])

    boxes = prediction[0]['boxes'].cpu().numpy()
    labels = prediction[0]['labels'].cpu().numpy()
    scores = prediction[0]['scores'].cpu().numpy()

    # Charger l'image avec OpenCV pour afficher les boîtes
    img_cv2 = cv2.imread(image_path)
    for i in range(len(boxes)):
        if scores[i] > 0.7:  # Seuil de confiance
            xmin, ymin, xmax, ymax = boxes[i].astype(int)
            label = classnames.get(labels[i], 'Inconnu')  # Récupérer le nom de la classe
            
            # Ajuster la couleur et l'épaisseur de la boîte englobante
            box_color = (0, 255, 0)  # Couleur verte
            box_thickness = 3  # Épaisseur de la boîte
            cv2.rectangle(img_cv2, (xmin, ymin), (xmax, ymax), box_color, box_thickness)

            # Ajuster la taille, couleur et fond du texte pour meilleure lisibilité
            font_scale = 1.2
            font_thickness = 2
            text_color = (255, 255, 255)  # Couleur du texte blanc
            text_background_color = (0, 0, 0)  # Fond noir pour le texte

            # Déterminer la taille du texte
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            # Position du texte
            text_x = xmin
            text_y = ymin - 10 if ymin - 10 > 20 else ymin + 20

            # Ajouter un fond derrière le texte pour la lisibilité
            cv2.rectangle(img_cv2, (text_x, text_y - text_height - baseline), 
                          (text_x + text_width, text_y + baseline), text_background_color, cv2.FILLED)
            cv2.putText(img_cv2, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        font_scale, text_color, font_thickness, lineType=cv2.LINE_AA)

    # Sauvegarder l'image avec les détections
    output_image_path = image_path.replace("test/images", "test/results")
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    cv2.imwrite(output_image_path, img_cv2)
    print(f"Résultats sauvegardés sous {output_image_path}")

# Parcourir toutes les images de test
for img_file in os.listdir(test_images):
    detect(os.path.join(test_images, img_file))