import os
import numpy as np
from PIL import Image
import pandas as pd
import time

# Import the high-precision functions from the modified single validation script
from valid_python_single import (
    read_bin_as_floats,
    func_conv2d_optimized,
    func_max_pooling_optimized,
    func_relu,
    func_fc,
    func_batchnorm2d
)

def normalize_np(image_np, mean, std):
    """Performs NumPy-based image normalization."""
    image_np = image_np / 255.0
    image_np = (image_np - np.array(mean, dtype=np.float32).reshape(-1, 1, 1)) / \
               (np.array(std, dtype=np.float32).reshape(-1, 1, 1))
    return image_np.astype(np.float32)

def run_numpy_inference(numpy_input, params):
    """Runs the full SmallCNN forward pass using NumPy functions."""
    # Block 1
    np_out = func_conv2d_optimized(numpy_input, params['conv1_weight'], params['conv1_bias'], stride=1, padding=1)
    np_out = func_batchnorm2d(np_out, params['bn1_weight'], params['bn1_bias'], params['bn1_running_mean'], params['bn1_running_var'])
    np_out = func_relu(np_out)
    np_out = func_max_pooling_optimized(np_out, win_size=2, stride=2)

    # Block 2
    np_out = func_conv2d_optimized(np_out, params['conv2_weight'], params['conv2_bias'], stride=1, padding=1)
    np_out = func_batchnorm2d(np_out, params['bn2_weight'], params['bn2_bias'], params['bn2_running_mean'], params['bn2_running_var'])
    np_out = func_relu(np_out)
    np_out = func_max_pooling_optimized(np_out, win_size=2, stride=2)

    # Block 3
    np_out = func_conv2d_optimized(np_out, params['conv3_weight'], params['conv3_bias'], stride=1, padding=1)
    np_out = func_batchnorm2d(np_out, params['bn3_weight'], params['bn3_bias'], params['bn3_running_mean'], params['bn3_running_var'])
    np_out = func_relu(np_out)
    np_out = func_max_pooling_optimized(np_out, win_size=2, stride=2)

    # Flatten and Classifier
    np_out = np_out.reshape(1, -1)
    np_out = func_fc(np_out, params['fc1_weight'], params['fc1_bias'])
    np_out = func_relu(np_out)
    logits_numpy = func_fc(np_out, params['fc2_weight'], params['fc2_bias'])
    
    return logits_numpy

if __name__ == '__main__':
    # --- Load All NumPy Parameters ---
    print("--- Loading NumPy parameters... ---")
    params = {}
    param_defs = {
        'conv1_weight': (32, 3, 3, 3), 'conv1_bias': (32,), 'bn1_weight': (32,), 'bn1_bias': (32,),
        'bn1_running_mean': (32,), 'bn1_running_var': (32,),
        'conv2_weight': (64, 32, 3, 3), 'conv2_bias': (64,), 'bn2_weight': (64,), 'bn2_bias': (64,),
        'bn2_running_mean': (64,), 'bn2_running_var': (64,),
        'conv3_weight': (128, 64, 3, 3), 'conv3_bias': (128,), 'bn3_weight': (128,), 'bn3_bias': (128,),
        'bn3_running_mean': (128,), 'bn3_running_var': (128,),
        'fc1_weight': (256, 128 * 5 * 5), 'fc1_bias': (256,),
        'fc2_weight': (7, 256), 'fc2_bias': (7,)
    }
    for name, shape in param_defs.items():
        data = read_bin_as_floats(f'./params/{name}.bin')
        params[name] = np.array(data, dtype=np.float32).reshape(shape)

    # --- Data Loading for Batch Inference ---
    img_dir = 'E:/test_data/images'
    label_path = 'E:/test_data/labels.txt'
    
    all_labels = pd.read_csv(label_path, sep=' ', header=None, names=['filename', 'label'])
    test_labels = all_labels[all_labels['filename'].str.startswith('test_')]

    N = 200
    if len(test_labels) < N:
        print(f"Warning: Only {len(test_labels)} test images available. Running on {len(test_labels)} images.")
        N = len(test_labels)

    predictions, targets = [], []
    mean_val, std_val = [0.5, 0.5, 0.5], [0.5, 0.5, 0.5]

    print(f"\n--- Starting batch inference on {N} test images... ---")
    start_time = time.time()

    for i in range(N):
        img_name = test_labels.iloc[i, 0]
        label = test_labels.iloc[i, 1] - 1

        # Image preprocessing
        img_pil = Image.open(os.path.join(img_dir, img_name)).convert('RGB')
        img_resized = img_pil.resize((40, 40), Image.Resampling.LANCZOS)
        img_np = np.array(img_resized).transpose(2, 0, 1).astype(np.float32)
        img_normalized = normalize_np(img_np, mean=mean_val, std=std_val)
        
        # Run NumPy inference
        logits = run_numpy_inference(img_normalized, params)
        
        predictions.append(np.argmax(logits, 1).item())
        targets.append(label)
        
        # Progress indicator
        print(f"Processed image {i + 1}/{N}", end='\r')

    end_time = time.time()
    print(f"\n\nTotal processing time for {N} images: {end_time - start_time:.4f} seconds.")

    # --- Calculate and Print Accuracy ---
    correct_predictions = sum(1 for p, t in zip(predictions, targets) if p == t)
    accuracy = (correct_predictions / N) * 100 if N > 0 else 0
    
    print(f"\nFinal Accuracy: {accuracy:.2f}% ({correct_predictions}/{N})")
    print('Finished.')