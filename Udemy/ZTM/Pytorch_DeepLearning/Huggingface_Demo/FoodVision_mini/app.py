"""
FoodVision Mini - Gradio App

This script sets up a Gradio interface for a Vision Transformer (ViT) model
trained to classify food images into 8 categories:
['cheesecake', 'chocolate_mousse', 'greek_salad', 'hot_dog',
 'macarons', 'onion_rings', 'spaghetti_bolognese', 'sushi'].

Workflow:
- Load the pretrained ViT model architecture and transforms.
- Load trained weights from a .pth file.
- Define a prediction function that takes an image and outputs:
    * Class probabilities
    * Top predicted class
    * Inference time
- Launch a Gradio interface with examples, title, description, and article link.
"""

import gradio as gr
import os
import sys
from PIL import Image
from pathlib import Path
import torch
import time  # using time instead of 'timer' for clarity
from typing import List, Tuple, Dict

# Add project root to sys.path for imports
sys.path.append(r"D:\Learning\IITKML\Self_learning\Udemy\ZTM\Pytorch_DeepLearning\Huggingface_Demo")

# Import model creation function from FoodVision_mini
from FoodVision_mini import model

# Define the class names for classification
class_names = [
    'cheesecake', 'chocolate_mousse', 'greek_salad', 'hot_dog',
    'macarons', 'onion_rings', 'spaghetti_bolognese', 'sushi'
]

# Create the ViT model and associated preprocessing transform
Vit_model, Vit_transform = model.create_Vit_model(num_classes=len(class_names))

# Path to the trained model weights (.pth file)
Vit_model_path = r"D:\Learning\IITKML\Self_learning\Udemy\ZTM\Pytorch_DeepLearning\Huggingface_Demo\FoodVision_mini\deployment_vit_model.pth"

# Load the trained weights into the model
Vit_model.load_state_dict(torch.load(Vit_model_path, map_location=torch.device('cpu')))
print("✅ Model loaded successfully")

# example_list = [["Examples/" + example] for example in os.listdir("Example")]

def predict(img) -> Tuple[Dict[str, float], str, float]:
    """
    Run inference on a single image.

    Args:
        img (PIL.Image): Input image.

    Returns:
        Tuple containing:
            - Dictionary of class probabilities
            - Top predicted class (string)
            - Prediction time in seconds (float)
    """
    if img is None:
        return {"error": "No image provided"}, "", 0.0

    # Preprocess image into tensor
    img_tensor = Vit_transform(img).unsqueeze(0)

    # Record start time
    start_time = time.time()

    # Set model to evaluation mode
    Vit_model.eval()
    with torch.inference_mode():
        outputs = Vit_model(img_tensor)
        pred_prob = torch.softmax(outputs, dim=1)

        # Map class names to probabilities
        pred_labels_and_prob = {
            class_names[i]: pred_prob[0][i].item() for i in range(len(class_names))
        }

        # Get top predicted class
        pred_label_idx = torch.argmax(pred_prob, dim=1).item()
        pred_class = class_names[pred_label_idx]

    # Record end time and compute inference duration
    end_time = time.time()
    pred_time = round(end_time - start_time, 4)

    return


example_list = [["Examples/" + example] for example in os.listdir("Example")]


title = "FOODVision Mini"
description = "A model to classify images of food from 8 different classes usin ViT model Classes cheesecake','chocolate_mousse', 'greek_salad', 'hot_dog', 'macarons', 'onion_rings', 'spaghetti_bolognese', 'sushi'."
article = "<p style='text-align: center'><a href='https://www.learnpytorch.io/'>Learn PyTorch</a> - A place to learn PyTorch for deep learning.</p>"

demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=[
        gr.Label(num_top_classes=8, label="Predictions"),   # full distribution
        gr.Textbox(label="Top Class"),                      # single best class
        gr.Number(label="Prediction time (s)")              # inference time
    ],
    examples=example_list,
    title=title,
    description=description,
    article=article,
)

demo.launch(debug=True, share=True)
