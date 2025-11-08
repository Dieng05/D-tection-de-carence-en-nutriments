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

# Liste pour stocker les images après détection
detected_images = []

# Taille fixe pour redimensionner les images (par exemple, 400x400 pixels)
fixed_size = (400, 400)

# Fonction pour assembler les images en une grille 3x3
def assemble_images_grid(images, grid_size=(3, 3), output_path='dataset/test/results/combined_result.jpg'):
    rows, cols = grid_size
    img_height, img_width = images[0].shape[:2]  # Taille d'une image (hauteur, largeur)
    
    # Créer une image vide pour la grille
    grid_image = np.zeros((rows * img_height, cols * img_width, 3), dtype=np.uint8)
    
    # Remplir la grille avec les images
    for idx, img in enumerate(images):
        row = idx // cols
        col = idx % cols
        grid_image[row * img_height:(row + 1) * img_height, col * img_width:(col + 1) * img_width] = img
    
    # Sauvegarder l'image assemblée
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, grid_image)
    print(f"Image combinée sauvegardée sous {output_path}")

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

    # Redimensionner l'image à une taille fixe
    img_cv2_resized = cv2.resize(img_cv2, fixed_size)

    # Ajouter l'image détectée à la liste
    detected_images.append(img_cv2_resized)

    # Si on a 9 images, on les assemble et les sauvegarde
    if len(detected_images) == 9:
        assemble_images_grid(detected_images)
        detected_images.clear()  # Réinitialiser la liste pour le prochain groupe de 9 images

# Parcourir toutes les images de test
for img_file in os.listdir(test_images):
    detect(os.path.join(test_images, img_file))

# Si le nombre d'images n'est pas un multiple de 9, on assemble les restantes
if detected_images:
    assemble_images_grid(detected_images, grid_size=(3, 3))
