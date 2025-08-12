import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model # pyright: ignore[reportMissingImports]
from tensorflow.keras.preprocessing.image import img_to_array, load_img # pyright: ignore[reportMissingImports]
from PIL import Image
import io

# Set TensorFlow logging level to reduce warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['ABSL_LOG_LEVEL'] = 'FATAL'

# Class names for garbage classification
CLASS_NAMES = [
    'battery', 'biological', 'cardboard', 'clothes', 'glass',
    'metal', 'paper', 'plastic', 'shoes', 'trash'
]

# Normalization values used by pre-trained models
MEAN = np.array([0.485, 0.456, 0.406])
STD = np.array([0.229, 0.224, 0.225])

def pytorch_normalize(img):
    """Normalize image using PyTorch pre-trained model normalization"""
    img = img / 255.0
    return (img - MEAN) / STD

class GarbageClassifier:
    def __init__(self):
        """Initialize the garbage classifier with three models"""
        self.models = {}
        self.model_names = ['resnet50', 'custom_cnn', 'mobilenetv2']
        self.load_models()
    
    def load_models(self):
        """Load the three best models"""
        model_paths = {
            'resnet50': 'models/saved_models/best_resnet50.keras',
            'custom_cnn': 'models/saved_models/best_custom_cnn.keras',
            'mobilenetv2': 'models/saved_models/best_mobilenetv2.keras'
        }
        
        for name, path in model_paths.items():
            try:
                # Check if path exists relative to streamlit-ui directory
                if os.path.exists(path):
                    self.models[name] = load_model(path)
                else:
                    # Try relative to parent directory
                    parent_path = f"../{path}"
                    if os.path.exists(parent_path):
                        self.models[name] = load_model(parent_path)
                    else:
                        print(f"Warning: Could not load model {name} from {path}")
            except Exception as e:
                print(f"Error loading model {name}: {e}")
    
    def preprocess_image(self, image_file):
        """Preprocess uploaded image for prediction"""
        try:
            # Load and resize image
            img = load_img(image_file, target_size=(224, 224))
            img_array = img_to_array(img)
            
            # Normalize image
            img_normalized = pytorch_normalize(img_array)
            
            # Add batch dimension
            img_batch = np.expand_dims(img_normalized, axis=0)
            
            return img_batch
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def predict_single(self, image_file):
        """Make prediction using all three models and return ensemble result"""
        # Preprocess image
        img_batch = self.preprocess_image(image_file)
        if img_batch is None:
            return None
        
        predictions = {}
        ensemble_predictions = np.zeros(len(CLASS_NAMES))
        
        # Get predictions from each model
        for name, model in self.models.items():
            try:
                pred = model.predict(img_batch, verbose=0)
                predictions[name] = pred[0]
                ensemble_predictions += pred[0]
            except Exception as e:
                print(f"Error predicting with {name}: {e}")
        
        # Average ensemble predictions
        if len(predictions) > 0:
            ensemble_predictions /= len(predictions)
        
        # Get final prediction
        predicted_class_idx = np.argmax(ensemble_predictions)
        predicted_class = CLASS_NAMES[predicted_class_idx]
        confidence = ensemble_predictions[predicted_class_idx]
        
        # Get top 3 predictions
        top_indices = np.argsort(ensemble_predictions)[::-1][:3]
        top_predictions = [(CLASS_NAMES[i], ensemble_predictions[i]) for i in top_indices]
        
        return {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'top_predictions': top_predictions,
            'individual_predictions': predictions,
            'all_probabilities': ensemble_predictions
        }
    
    def get_recycling_info(self, predicted_class):
        """Get recycling information for the predicted class"""
        recycling_info = {
            'battery': {
                'category': 'Hazardous Waste',
                'instructions': 'Do not throw in regular trash. Take to battery recycling centers or electronics stores.',
                'impact': 'High (contains toxic chemicals)',
                'color': 'red'
            },
            'biological': {
                'category': 'Organic Waste',
                'instructions': 'Compost if possible, or dispose in green waste bin.',
                'impact': 'Low (biodegradable)',
                'color': 'green'
            },
            'cardboard': {
                'category': 'Recyclable',
                'instructions': 'Flatten and place in blue recycling bin.',
                'impact': 'Low (easily recyclable)',
                'color': 'blue'
            },
            'clothes': {
                'category': 'Textile Waste',
                'instructions': 'Donate if in good condition, otherwise take to textile recycling centers.',
                'impact': 'Medium (can be recycled)',
                'color': 'yellow'
            },
            'glass': {
                'category': 'Recyclable',
                'instructions': 'Rinse and place in glass recycling bin.',
                'impact': 'Low (infinitely recyclable)',
                'color': 'blue'
            },
            'metal': {
                'category': 'Recyclable',
                'instructions': 'Rinse and place in metal recycling bin.',
                'impact': 'Low (highly recyclable)',
                'color': 'blue'
            },
            'paper': {
                'category': 'Recyclable',
                'instructions': 'Place in paper recycling bin. Keep dry and clean.',
                'impact': 'Low (easily recyclable)',
                'color': 'blue'
            },
            'plastic': {
                'category': 'Recyclable',
                'instructions': 'Check recycling number. Rinse and place in appropriate recycling bin.',
                'impact': 'Medium (depends on type)',
                'color': 'blue'
            },
            'shoes': {
                'category': 'Textile Waste',
                'instructions': 'Donate if wearable, otherwise take to shoe recycling programs.',
                'impact': 'Medium (can be recycled)',
                'color': 'yellow'
            },
            'trash': {
                'category': 'General Waste',
                'instructions': 'Place in general waste bin. Consider if items can be recycled.',
                'impact': 'High (goes to landfill)',
                'color': 'red'
            }
        }
        
        return recycling_info.get(predicted_class, {
            'category': 'Unknown',
            'instructions': 'Please check local recycling guidelines.',
            'impact': 'Unknown',
            'color': 'gray'
        }) 