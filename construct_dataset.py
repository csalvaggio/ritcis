import argparse
import cv2
import fnmatch
import numpy
import os
import os.path
import random
import struct

import gzip_file

def byte_swap(original_integer):
   # Convert the original integer to bytes using little-endian byte order
   original_bytes = struct.pack('<I', original_integer)

   # Swap the bytes
   byte_swapped_bytes = original_bytes[::-1]

   # Convert the swapped bytes back to an integer
   byte_swapped_integer = struct.unpack('<I', byte_swapped_bytes)[0]

   return byte_swapped_integer



description = 'Construct the RITCIS handwritten letters data file in the '
description += 'same fashion as the MNIST data set'

parser = argparse.ArgumentParser(description=description)

help_message = 'path to the directory containing the RITCIS data tiles '
help_message += 'to be included in the data set (i.e. the specific tile '
help_message += 'resolution directory)'
parser.add_argument('tiles_path',
                    type=str,
                    help=help_message)

help_message = 'path to the directory to contain the constructed data '
help_message += 'set'
parser.add_argument('dataset_path',
                    type=str,
                    help=help_message)

help_message = 'tile image extension '
help_message += '[default is "png"]'
parser.add_argument('-e', '--extension',
                    dest='tile_extension',
                    type=str,
                    default='png',
                    help=help_message)

args = parser.parse_args()

tiles_path = args.tiles_path
dataset_path = args.dataset_path
tile_extension = '.' + args.tile_extension

# Trim path if the last character is the OS-specific path separator
if tiles_path[-1] == os.path.sep:
   tiles_path = tiles_path[:-1]
if dataset_path[-1] == os.path.sep:
   dataset_path = dataset_path[:-1]

# Find all of the tile files in the tiles path directory tree
tile_files = []
for root, dirs, files in os.walk(tiles_path):
   for file in fnmatch.filter(files, '*.png'):
      tile_files.append(os.path.join(root, file))
tile_files.sort()

# Randomly shuffle the tile files
seed = 42
random.seed(seed)
random.shuffle(tile_files)

# Determine the training and test image ranges
training_percentage = 0.70
number_of_training_images = int(training_percentage * len(tile_files))
number_of_test_images = len(tile_files) - number_of_training_images
training_subrange = range(0, number_of_training_images)
test_subrange = range(number_of_training_images, len(tile_files))

# Separate the training and test tile files into two lists
training_files = [tile_files[idx] for idx in training_subrange]
test_files = [tile_files[idx] for idx in test_subrange]
msg = 'Separating randomized list of images into '
msg += '{} training and '.format(number_of_training_images)
msg += '{} test images'.format(number_of_test_images)
print(msg)

# If it does not exist, create the directory to hold the produced data sets
if not os.path.exists(dataset_path):
   os.makedirs(dataset_path)

# Determine/set the common metadata for the images
magic_number = numpy.int32(2051)
img = cv2.imread(tile_files[0])
number_of_rows, number_of_columns, number_of_channels = img.shape
number_of_rows = numpy.int32(number_of_rows)
number_of_columns = numpy.int32(number_of_columns)

# Build the training images file
filename = 'train-images-' + '{0:03d}'.format(number_of_rows) + '-ubyte'
file_path = os.path.join(dataset_path, filename)
with open(file_path, 'wb') as file:
   # Pack the byte-swapped integer metadata into binary data and write to file
   # (use '<I' for little-endian format, '>I' for big-endian format)
   binary_data = struct.pack('<I', byte_swap(magic_number))
   file.write(binary_data)
   binary_data = struct.pack('<I', byte_swap(number_of_training_images))
   file.write(binary_data)
   binary_data = struct.pack('<I', byte_swap(number_of_rows))
   file.write(binary_data)
   binary_data = struct.pack('<I', byte_swap(number_of_columns))
   file.write(binary_data)
   for tile_file in training_files:
      img = cv2.imread(tile_file)
      img[:, :, 0].tofile(file)
   file.close()
gzip_file.gzip_file(file_path, file_path + '.gz')

# Build the test images file
filename = 'test-images-' + '{0:03d}'.format(number_of_rows) + '-ubyte'
file_path = os.path.join(dataset_path, filename)
with open(file_path, 'wb') as file:
   # Pack the byte-swapped integer metadata into binary data and write to file
   # (use '<I' for little-endian format, '>I' for big-endian format)
   binary_data = struct.pack('<I', byte_swap(magic_number))
   file.write(binary_data)
   binary_data = struct.pack('<I', byte_swap(number_of_test_images))
   file.write(binary_data)
   binary_data = struct.pack('<I', byte_swap(number_of_rows))
   file.write(binary_data)
   binary_data = struct.pack('<I', byte_swap(number_of_columns))
   file.write(binary_data)
   for tile_file in test_files:
      img = cv2.imread(tile_file)
      img[:, :, 0].tofile(file)
   file.close()
gzip_file.gzip_file(file_path, file_path + '.gz')

# Modify the common metadata for the labels
magic_number = numpy.int32(2049)

# Build the training labels file
filename = 'train-labels-' + '{0:03d}'.format(number_of_rows) + '-ubyte'
file_path = os.path.join(dataset_path, filename)
with open(file_path, 'wb') as file:
   # Pack the byte-swapped integer metadata into binary data and write to file
   # (use '<I' for little-endian format, '>I' for big-endian format)
   binary_data = struct.pack('<I', byte_swap(magic_number))
   file.write(binary_data)
   binary_data = struct.pack('<I', byte_swap(number_of_training_images))
   file.write(binary_data)
   # Extract the current letter from the base filename, convert to it's
   # ASCII code, and subtract 65 to make a 0-based label system
   for tile_file in training_files:
      basename = os.path.basename(tile_file)
      current_letter = basename[11]
      label = numpy.uint8(ord(current_letter) - 65)
      file.write(label)
   file.close()
gzip_file.gzip_file(file_path, file_path + '.gz')

# Build the test labels file
filename = 'test-labels-' + '{0:03d}'.format(number_of_rows) + '-ubyte'
file_path = os.path.join(dataset_path, filename)
with open(file_path, 'wb') as file:
   # Pack the byte-swapped integer metadata into binary data and write to file
   # (use '<I' for little-endian format, '>I' for big-endian format)
   binary_data = struct.pack('<I', byte_swap(magic_number))
   file.write(binary_data)
   binary_data = struct.pack('<I', byte_swap(number_of_test_images))
   file.write(binary_data)
   # Extract the current letter from the base filename, convert to it's
   # ASCII code, and subtract 65 to make a 0-based label system
   for tile_file in test_files:
      basename = os.path.basename(tile_file)
      current_letter = basename[11]
      label = numpy.uint8(ord(current_letter) - 65)
      file.write(label)
   file.close()
gzip_file.gzip_file(file_path, file_path + '.gz')

