import numpy as np

def read_bin_as_floats(file_path):
    """Reads a binary file containing float32 values and returns them as a list."""
    with open(file_path, 'rb') as f:
        data = f.read()
    return list(np.frombuffer(data, dtype=np.float32))

def func_conv2d_optimized(input_data, weight, bias, stride=1, padding=1):
    """Optimized 2D convolution function."""
    # 获取输入和权重的形状
    batch_size, in_channels, in_height, in_width = input_data.shape
    out_channels, in_channels, kernel_height, kernel_width = weight.shape
    
    # 计算输出形状
    out_height = (in_height + 2 * padding - kernel_height) // stride + 1
    out_width = (in_width + 2 * padding - kernel_width) // stride + 1
    
    # 添加填充
    padded_input = np.pad(input_data, ((0, 0), (0, 0), (padding, padding), (padding, padding)), mode='constant')
    
    # 初始化输出
    output = np.zeros((batch_size, out_channels, out_height, out_width), dtype=np.float32)
    
    # 执行卷积操作
    for b in range(batch_size):
        for oc in range(out_channels):
            for oh in range(out_height):
                for ow in range(out_width):
                    # 计算当前位置的输入区域
                    h_start = oh * stride
                    h_end = h_start + kernel_height
                    w_start = ow * stride
                    w_end = w_start + kernel_width
                    
                    # 提取输入区域
                    input_region = padded_input[b, :, h_start:h_end, w_start:w_end]
                    
                    # 执行卷积计算
                    output[b, oc, oh, ow] = np.sum(input_region * weight[oc, :, :, :]) + bias[oc]
    
    return output

def func_batchnorm2d(input_data, weight, bias, running_mean, running_var, eps=1e-5):
    """Batch normalization function for 2D input."""
    # 获取输入形状
    batch_size, channels, height, width = input_data.shape
    
    # 初始化输出
    output = np.zeros_like(input_data, dtype=np.float32)
    
    # 对每个通道执行batch normalization
    for c in range(channels):
        # 标准化
        normalized = (input_data[:, c, :, :] - running_mean[c]) / np.sqrt(running_var[c] + eps)
        
        # 缩放和偏移
        output[:, c, :, :] = normalized * weight[c] + bias[c]
    
    return output

def func_relu(input_data):
    """ReLU activation function."""
    return np.maximum(0, input_data)

def func_max_pooling_optimized(input_data, win_size=2, stride=2):
    """Optimized max pooling function."""
    # 获取输入形状
    batch_size, channels, in_height, in_width = input_data.shape
    
    # 计算输出形状
    out_height = (in_height - win_size) // stride + 1
    out_width = (in_width - win_size) // stride + 1
    
    # 初始化输出
    output = np.zeros((batch_size, channels, out_height, out_width), dtype=np.float32)
    
    # 执行最大池化
    for b in range(batch_size):
        for c in range(channels):
            for oh in range(out_height):
                for ow in range(out_width):
                    # 计算当前位置的输入区域
                    h_start = oh * stride
                    h_end = h_start + win_size
                    w_start = ow * stride
                    w_end = w_start + win_size
                    
                    # 提取输入区域
                    input_region = input_data[b, c, h_start:h_end, w_start:w_end]
                    
                    # 计算最大值
                    output[b, c, oh, ow] = np.max(input_region)
    
    return output

def func_fc(input_data, weight, bias):
    """Fully connected layer function."""
    # 确保输入是2D形状 (batch_size, in_features)
    batch_size = input_data.shape[0]
    in_features = input_data.shape[1]
    
    # 执行矩阵乘法和偏置加法
    output = np.dot(input_data, weight.T) + bias
    
    return output