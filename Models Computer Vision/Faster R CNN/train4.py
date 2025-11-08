# Main code
import os
import torch
import json
import glob
import time
import torchvision
from PIL import Image
from torch.utils.data import DataLoader
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np

# Paths to your dataset
train_img_dir = 'dataset/train/images'
train_label_dir = 'dataset/train/labels'
test_img_dir = 'dataset/test/images'
test_label_dir = 'dataset/test/labels'
val_img_dir = 'dataset/val/images'
val_label_dir = 'dataset/val/labels'

# Helper function to convert YOLO format to COCO
def yolo_to_coco(label_file, img_width, img_height):
    boxes = []
    with open(label_file, 'r') as f:
        for line in f:
            class_id, x_center, y_center, width, height = map(float, line.split())
            xmin = (x_center - width / 2) * img_width
            ymin = (y_center - height / 2) * img_height
            xmax = (x_center + width / 2) * img_width
            ymax = (y_center + height / 2) * img_height
            boxes.append({
                'bbox': [xmin, ymin, xmax, ymax],
                'category_id': int(class_id) + 1  # Class ID + 1 (Faster R-CNN classes start at 1)
            })
    return boxes

# Custom Dataset for your images and annotations
class PlantDataset(torch.utils.data.Dataset):
    def __init__(self, img_dir, label_dir, transforms=None):
        self.img_dir = img_dir
        self.label_dir = label_dir
        self.transforms = transforms
        self.img_files = glob.glob(os.path.join(img_dir, '*.jpg'))  # All image files

    def __len__(self):
        return len(self.img_files)

    def __getitem__(self, idx):
        img_path = self.img_files[idx]
        img_name = os.path.basename(img_path)
        label_path = os.path.join(self.label_dir, img_name.replace('.jpg', '.txt'))

        # Load the image
        img = Image.open(img_path).convert('RGB')
        img_width, img_height = img.size

        # Convert YOLO annotations to COCO format
        boxes = []
        if os.path.exists(label_path):
            boxes = yolo_to_coco(label_path, img_width, img_height)

        if len(boxes) == 0:
            # If there are no annotations, set default empty tensors for boxes and labels
            boxes_tensor = torch.zeros((0, 4), dtype=torch.float32)
            labels_tensor = torch.zeros((0,), dtype=torch.int64)
        else:
            boxes_tensor = torch.as_tensor([b['bbox'] for b in boxes], dtype=torch.float32)
            labels_tensor = torch.as_tensor([b['category_id'] for b in boxes], dtype=torch.int64)

        target = {
            'boxes': boxes_tensor,
            'labels': labels_tensor,
            'image_id': torch.tensor([idx])
        }

        if self.transforms:
            img = self.transforms(img)

        return img, target

# Collate function to handle batches
def collate_fn(batch):
    return tuple(zip(*batch))

# Function to get Faster R-CNN model
def get_model(num_classes):
    model = torchvision.models.detection.fasterrcnn_mobilenet_v3_large_fpn(weights='DEFAULT')

    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model

# Function to calculate IoU
def compute_iou(box1, box2):
    """
    Compute the Intersection over Union (IoU) between two bounding boxes.
    Box format: [xmin, ymin, xmax, ymax]
    """
    box1_x1, box1_y1, box1_x2, box1_y2 = box1
    box2_x1, box2_y1, box2_x2, box2_y2 = box2

    # Calculate the intersection
    inter_x1 = max(box1_x1, box2_x1)
    inter_y1 = max(box1_y1, box2_y1)
    inter_x2 = min(box1_x2, box2_x2)
    inter_y2 = min(box1_y2, box2_y2)

    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

    # Calculate the areas of the boxes
    box1_area = (box1_x2 - box1_x1) * (box1_y2 - box1_y1)
    box2_area = (box2_x2 - box2_x1) * (box2_y2 - box2_y1)

    # Calculate union
    union_area = box1_area + box2_area - inter_area

    # Compute IoU
    iou = inter_area / union_area if union_area > 0 else 0
    return iou

# Evaluation function
def evaluate_model(model, loader, device, iou_threshold=0.5, score_threshold=0.5):
    model.eval()
    all_true_labels = []
    all_pred_labels = []
    with torch.no_grad():
        for imgs, targets in loader:
            imgs = [img.to(device) for img in imgs]
            outputs = model(imgs)

            for i, output in enumerate(outputs):
                true_labels = targets[i]['labels'].cpu().numpy()
                pred_labels = output['labels'].cpu().numpy()
                pred_boxes = output['boxes'].cpu().numpy()
                scores = output['scores'].cpu().numpy()

                high_conf_indices = np.where(scores > score_threshold)[0]
                pred_labels = pred_labels[high_conf_indices]
                pred_boxes = pred_boxes[high_conf_indices]

                matched_pred_labels = []
                matched_true_labels = []

                for k, true_box in enumerate(targets[i]['boxes'].cpu().numpy()):
                    iou_scores = [compute_iou(true_box, pred_box) for pred_box in pred_boxes]
                    best_iou_idx = np.argmax(iou_scores) if len(iou_scores) > 0 else -1
                    if best_iou_idx != -1 and iou_scores[best_iou_idx] >= iou_threshold:
                        matched_pred_labels.append(pred_labels[best_iou_idx])
                        matched_true_labels.append(true_labels[k])

                all_pred_labels.extend(matched_pred_labels)
                all_true_labels.extend(matched_true_labels)

    precision = precision_score(all_true_labels, all_pred_labels, average='weighted', zero_division=0)
    recall = recall_score(all_true_labels, all_pred_labels, average='weighted')
    f1 = f1_score(all_true_labels, all_pred_labels, average='weighted')

    return precision, recall, f1

# Function to save the model
def save_model(model, path):
    torch.save(model.state_dict(), path)
    print(f"Model saved to {path}")

# Function to load the model
def load_model(path, num_classes, device):
    model = get_model(num_classes=num_classes)
    model.load_state_dict(torch.load(path, map_location=device))
    model.to(device)
    model.eval()  # Set the model to evaluation mode
    print(f"Model loaded from {path}")
    return model

# Modify the training loop to save the model after training
def train_model(model, train_loader, test_loader, optimizer, device, num_epochs=1, save_path=None):
    model.to(device)
    for epoch in range(num_epochs):
        print(f"Epoch {epoch+1}/{num_epochs}")
        model.train()
        running_loss = 0.0
        epoch_start = time.time()

        for imgs, targets in train_loader:
            imgs = [img.to(device) for img in imgs]
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

            loss_dict = model(imgs, targets)
            losses = sum(loss for loss in loss_dict.values())
            running_loss += losses.item()

            optimizer.zero_grad()
            losses.backward()
            optimizer.step()

        avg_loss = running_loss / len(train_loader)
        precision, recall, f1 = evaluate_model(model, test_loader, device)

        epoch_time = time.time() - epoch_start
        print(f"Loss: {avg_loss:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1-Score: {f1:.4f}")
        print(f"Time per epoch: {epoch_time:.2f} seconds")

    if save_path:
        save_model(model, save_path)  # Save the model after training

if __name__ == '__main__':
    transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor()])
    
    train_dataset = PlantDataset(train_img_dir, train_label_dir, transforms=transform)
    test_dataset = PlantDataset(test_img_dir, test_label_dir, transforms=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, collate_fn=collate_fn, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False, collate_fn=collate_fn, num_workers=0)
    
    model = get_model(num_classes=3)  # 2 classes + background
    optimizer = torch.optim.SGD([p for p in model.parameters() if p.requires_grad], lr=0.001, momentum=0.9, weight_decay=0.0005)
    
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    
    # Train the model and save it to 'fasterrcnn_plant_detection.pth'
    train_model(model, train_loader, test_loader, optimizer, device, num_epochs=10, save_path='fasterrcnn_plant_detection.pth')


