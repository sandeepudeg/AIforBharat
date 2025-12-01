
import torch
import torchvision

def create_Vit_model(num_classes: int = 8, seed: int = 42):
    """
    Create a Vision Transformer (ViT) model for image classification.

    This function initializes a pretrained ViT-B/32 model from torchvision,
    freezes its backbone weights to prevent training, and replaces the 
    classification head with a new linear layer suitable for the specified 
    number of output classes. It also sets a manual random seed for 
    reproducibility.

    Args:
        num_classes (int, optional): Number of output classes for the classifier. 
                                     Default is 8.
        seed (int, optional): Random seed for reproducibility. Default is 42.

    Returns:
        tuple:
            - ViT_model (torch.nn.Module): The Vision Transformer model ready for training.
            - ViT_transform (callable): The preprocessing transform associated with the pretrained weights.
    """

    # Load default pretrained weights for ViT-B/32
    ViT_weights = torchvision.models.ViT_B_32_Weights.DEFAULT

    # Get the preprocessing transforms (resize, normalize, etc.) tied to these weights
    ViT_transform = ViT_weights.transforms()

    # Initialize the pretrained ViT-B/32 model
    ViT_model = torchvision.models.vit_b_32(weights=ViT_weights)

    # Freeze all parameters so the backbone does not get updated during training
    for param in ViT_model.parameters():
        param.requires_grad = False

    # Set manual seed for reproducibility of weight initialization
    torch.manual_seed(seed)

    # Replace the classification head with a new linear layer for `num_classes`
    ViT_model.heads = torch.nn.Linear(in_features=768, out_features=num_classes)

    # Return both the model and the associated transform
    return ViT_model, ViT_transform

