import os
import sys
from utils.prediction_utils import GarbageClassifier

def test_model_loading():
    # Test if all models can be loaded successfully
    print("Testing model loading...")
    
    try:
        classifier = GarbageClassifier()
        print(f"Successfully loaded {len(classifier.models)} models:")
        
        for name in classifier.model_names:
            if name in classifier.models:
                print(f"  {name.upper()}: Loaded successfully")
            else:
                print(f"  {name.upper()}: Failed to load")
        
        return len(classifier.models) > 0
        
    except Exception as e:
        print(f"Error loading models: {e}")
        return False

def test_prediction_utils():
    # Test the prediction utilities module
    print("\nTesting prediction utilities...")
    
    try:
        from utils.prediction_utils import CLASS_NAMES, pytorch_normalize
        
        print(f"CLASS_NAMES loaded: {len(CLASS_NAMES)} classes")
        print(f"  Classes: {CLASS_NAMES}")
        
        # Test normalization function
        import numpy as np
        test_img = np.random.rand(224, 224, 3)
        normalized = pytorch_normalize(test_img)
        print(f"Normalization function works: {normalized.shape}")
        
        return True
        
    except Exception as e:
        print(f"Error testing utilities: {e}")
        return False

def main():
    # Main test function
    print("=== Garbage Classification Model Test ===\n")
    
    # Test utilities
    utils_ok = test_prediction_utils()
    
    # Test model loading
    models_ok = test_model_loading()
    
    print("\n=== Test Results ===")
    print(f"Utilities: {'PASS' if utils_ok else 'FAIL'}")
    print(f"Models: {'PASS' if models_ok else 'FAIL'}")
    
    if utils_ok and models_ok:
        print("\nAll tests passed! The prediction system is ready to use.")
        return 0
    else:
        print("\nSome tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 