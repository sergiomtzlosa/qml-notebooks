from PIL import Image
import cv2
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt

def show_image(img_array):
    
    plt.imshow(img_array, cmap=plt.cm.gray, interpolation="nearest")
    plt.show()
    
def save_image_to_jpg(image, file_name):
    image.save(file_name)
    
def invert_data(data):
    return np.invert(data);

def save_image_file(filename, data):
    
    return plt.imsave(filename, np.invert(data), cmap='binary')
    
def convert_to_bw(image_path):
    
    img_grey = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # define a threshold, 128 is the middle of black and white in grey scale
    thresh = 128

    # threshold the image
    img_binary = cv2.threshold(img_grey, thresh, 255, cv2.THRESH_BINARY)[1]
    
    return img_binary

def resize_array(image, size=(128,128)):
    
    resized = cv2.resize(image, size, cv2.INTER_LINEAR)
    
    return resized

def image_from_array(array_data):

    image = Image.fromarray(array_data, mode='L')
    
    return image

def binary_encode(array):
    
    encoded_array = np.array(array / int(255), dtype='uint8')
    
    return encoded_array

def rebuild_binary_array(array_binary):
    
    rebuild_array = array_binary*255
    
    return rebuild_array

def scale_binary_image(array_data, factor_scale):
    
    rescaled = scipy.ndimage.zoom(array_data, zoom = factor_scale, order=0)
    
    return rescaled

def save_bin_array_to_csv(file_path, array_binary):
    return np.savetxt(file_path, array_binary, delimiter=',', fmt='%d')

def load_bin_array_from_csv(file_path):
    return np.loadtxt(file_path, delimiter=',', dtype='uint8')