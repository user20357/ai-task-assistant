# Training YOLO for Custom UI Element Detection

This guide explains how to train a custom YOLO model to detect specific UI elements like Chrome icons, close buttons, etc.

## Prerequisites

- Python 3.8+
- PyTorch
- Ultralytics YOLOv8
- Labeled dataset of UI elements

## Step 1: Install Required Libraries

```bash
pip install ultralytics
pip install roboflow
```

## Step 2: Collect Training Data

1. **Take screenshots** of UI elements you want to detect:
   - Chrome, Firefox, Edge icons
   - Close, minimize, maximize buttons
   - Common UI elements (buttons, text fields)

2. **Organize screenshots** in a folder structure

## Step 3: Label Your Data

1. **Use a labeling tool** like [Roboflow](https://roboflow.com/) or [LabelImg](https://github.com/tzutalin/labelImg)

2. **Create bounding boxes** around UI elements with these classes:
   - chrome_icon
   - firefox_icon
   - close_button
   - minimize_button
   - maximize_button
   - button
   - text_field
   - link

3. **Export annotations** in YOLO format

## Step 4: Prepare Dataset

1. **Split data** into train/validation/test sets (70%/20%/10%)

2. **Create dataset.yaml** file:

```yaml
path: /path/to/dataset
train: train/images
val: valid/images
test: test/images

nc: 8  # number of classes
names: ['chrome_icon', 'firefox_icon', 'close_button', 'minimize_button', 'maximize_button', 'button', 'text_field', 'link']
```

## Step 5: Train YOLO Model

```python
from ultralytics import YOLO

# Load a pretrained YOLOv8 model
model = YOLO('yolov8n.pt')

# Train the model on your custom dataset
results = model.train(
    data='dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    name='ui_elements_detector'
)
```

## Step 6: Evaluate Model

```python
# Evaluate on validation set
results = model.val()
```

## Step 7: Use Trained Model

```python
# Load your trained model
model = YOLO('runs/detect/ui_elements_detector/weights/best.pt')

# Run inference
results = model(screenshot)
```

## Tips for Better Performance

1. **Collect diverse data** - different themes, resolutions, and UI states
2. **Augment training data** - brightness, contrast, rotation variations
3. **Start with a smaller model** like YOLOv8n for faster training
4. **Fine-tune hyperparameters** for your specific use case
5. **Use transfer learning** from a pre-trained model

## Integrating with the App

Replace the model path in `src/core/yolo_detector.py`:

```python
self.model = YOLO('path/to/your/trained/model.pt')
```