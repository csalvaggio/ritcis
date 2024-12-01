import argparse
import cv2
import numpy
import os
import os.path
import pdf2image
import shutil
import sys

import map_quad_to_quad
import Mouse

description = 'Extract tiles from handwritten letter data set development '
description += 'sheets'
parser = argparse.ArgumentParser(description=description)

help_message = 'starting sample ID number'
parser.add_argument('starting_sample',
                    type=int,
                    help=help_message)

help_message = 'file path of the PDF containing the scanned handwritten '
help_message += 'letter data set development sheets'
parser.add_argument('pdf_filename',
                    type=str,
                    help=help_message)

help_message = 'base directory for extracted letter tiles '
help_message += '[default is None]'
parser.add_argument('-d', '--tiles-base-directory',
                    dest='tiles_base_directory',
                    type=str,
                    default=None,
                    help=help_message)

help_message = 'the letters will be centered using its centroid value, '
help_message += 'otherwise the letter\'s bounding box center will be used '
help_message += '[default is False]'
parser.add_argument('-c', '--use-centroid',
                    dest='use_centroid',
                    action='store_true',
                    help=help_message)

help_message = 'the letters will retain their original dimensions, otherwise '
help_message += 'they will be size normalized while retaining their original '
help_message += 'aspect ratio '
help_message += '[default is False]'
parser.add_argument('-o', '--use-original-dimensions',
                    dest='use_original_dimensions',
                    action='store_true',
                    help=help_message)

help_message = 'create square tiles '
help_message += '[default is False]'
parser.add_argument('-s', '--square',
                    dest='use_square',
                    action='store_true',
                    help=help_message)

help_message = 'structuring element radius to use for character cleanup '
help_message += 'using morphological closings/openings '
help_message += '[default is 3]'
parser.add_argument('-r', '--radius',
                    dest='structuring_element_radius',
                    type=int,
                    default=3,
                    help=help_message)

help_message = 'absolute tolerance for determining if channel probability '
help_message += 'density functions are different '
help_message += '[default is 0.025]'
parser.add_argument('-t', '--tolerance',
                    dest='absolute_tolerance',
                    type=float,
                    default=0.025,
                    help=help_message)

# Parse the command line arguments and options
args = parser.parse_args()
starting_sample = args.starting_sample
pdf_filename = args.pdf_filename
if args.tiles_base_directory:
   tiles_base_directory = args.tiles_base_directory.rstrip(os.path.sep)
else:
   tiles_base_directory = None
use_centroid = args.use_centroid
use_original_dimensions = args.use_original_dimensions
use_square = args.use_square
structuring_element_radius = args.structuring_element_radius
absolute_tolerance = args.absolute_tolerance

# Set the resolution with which to convert each page in the provided PDF
# to an image for processing
dpi = 600

# Set up the geometry for the tiles to be extracted from the scanned input
# forms (pages)
start_row = 503
if use_square:
   start_row += 14
start_col = 765

tile_rows = 228
if use_square:
   tile_rows -= 28
tile_cols = 200

stride_rows = 221
stride_cols = 196

# Set the fill ratio (i.e. the percentage of the extracted image area that
# should be filled in the final extracted tiles)
fill_ratio = 0.7

# Create the circular structuring element to be used in the morphological
# clean up processing
structuring_element = numpy.zeros((structuring_element_radius*2 + 1,
                                   structuring_element_radius*2 + 1),
                                  numpy.uint8)
cv2.circle(structuring_element,
           (structuring_element_radius,
            structuring_element_radius),
           structuring_element_radius,
           255,
           -1)

# Convert the pages of the provided PDF file to images for processing
msg = '\nConverting pages of the provided PDF file to images at '
msg += '{0} dpi ...'.format(dpi)
print(msg)
pages = pdf2image.convert_from_path(pdf_filename, dpi=dpi)

# Process each of the converted images sequentially
sample = starting_sample
for page in pages:
   # Reorder the channels of the converted image to OpenCV ordering (BGR)
   img = numpy.array(page)
   img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

   # Have the user select the alignment fiducials for the current image
   page_name = "Select fiducials for current page (CW)"
   cv2.imshow(page_name, img)

   msg = '\nSample: {0:03d}'.format(sample)
   msg += '\n--------------------------------------------------------------'
   msg += '\n  Select the fiducials, in clockwise (CW) order, beginning'
   msg += '\n  in the upper left-hand corner of the page'
   msg += '\n--------------------------------------------------------------'
   print(msg)
   mouse = Mouse.Mouse(page_name)
   imgX = []
   imgY = []
   while len(imgX) < 4:
      if mouse.left_down():
         p = mouse.coordinate()
         msg = '{0}'.format(p)
         print(msg)
         imgX.append(p[0])
         imgY.append(p[1])
         mouse.clear()
      k = cv2.waitKey(100)
      if k == 27:  # <Esc>
         break
      # If the user has pressed 'Q' or 'q', terminate the program
      if k == 81:  # Q
         sys.exit()
      if k == 113: # q
         sys.exit()
   cv2.destroyWindow(page_name)
   # If the user has pressed <Esc>, skip the current sample/page
   if k == 27:  # <Esc>
      sample += 1
      continue
   msg = ''
   print(msg)

   # Perform quad-to-quad mapping to align the current sample/page
   # to the reference grid
   mapX = [660, 4800, 4800, 660]
   mapY = [425, 425, 6300, 6300]

   img_size = (img.shape[0], img.shape[1])
   map_size = (img.shape[0], img.shape[1])
   map1, map2 = \
      map_quad_to_quad.map_quad_to_quad(img_size, map_size,
                                        imgX, imgY, mapX, mapY)
   img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR)

   # When square image tiles are desired, set the extraction sizes
   if use_square:
      sizes = [None, 28, 56, 112, 224]
   else:
      sizes = [None]

   # Perform the extraction for the current resolution
   for size in sizes:
      if size:
         size_string = '{0:03d}'.format(size, 3)
      else:
         size_string = 'full'

      if size:
         msg = 'Generating {0}x{1} tiles ...'.format(size, size)
         print(msg)

      # If extracted tiles are to be saved to disk, set the path to
      # the output directory and clean up any previous version of this
      # directory (creating a new version)
      if tiles_base_directory:
         current_tiles_path = os.path.join(tiles_base_directory,
                                           size_string,
                                           '{0:03d}'.format(sample, 3))
         if os.path.exists(current_tiles_path):
            shutil.rmtree(current_tiles_path)
         os.makedirs(current_tiles_path)

      # Stride through the current sample/page and extract individual
      # letter tiles
      for letter_idx in range(26):
         for replicate_idx in range(20):
            # Form the file basename for the current tile
            tile_name = 'ritcis_'
            tile_name += '{0:03d}_'.format(sample, 3)
            tile_name += '{0}_'.format(chr(letter_idx + 65))
            tile_name += '{0:02d}'.format(replicate_idx, 2)

            # Extract the next tile from the current sample/page
            tile_ul_row = start_row + letter_idx * stride_rows
            tile_ul_col = start_col + replicate_idx * stride_cols
            tile = img[tile_ul_row:tile_ul_row+tile_rows,
                       tile_ul_col:tile_ul_col+tile_cols, :]

            # Compute the 3-channel histogram for the current tile
            hist = []
            for channel in [0, 1, 2]:
               hist.append(cv2.calcHist([tile],
                                        [channel],
                                        None,
                                        [256],
                                        [0, 256]))
            hist = hist / (numpy.sum(hist) / 3)

            # ASSUMPTION: Sheets are filled out using black ink
            # If the individual channel histograms are not all equal (i.e
            # there is user physical color highlighting), then reject the
            # current tile and move on to the next
            if numpy.allclose(hist[0], hist[1], 0, absolute_tolerance) and \
               numpy.allclose(hist[1], hist[2], 0, absolute_tolerance) and \
               numpy.allclose(hist[2], hist[0], 0, absolute_tolerance):
               reject = False
            else:
               reject = True

            if reject:
               if size is None:
                  msg = 'Rejecting {0} '.format(tile_name)
                  msg += 'based on original sample highlighting'
                  print(msg)
               continue

            # Convert the current tile to grayscale for thresholding and
            # clean up
            gray_tile = 255 - cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)

            # Perform binary thresholding on the current tile
            ret, thresholded_tile = cv2.threshold(gray_tile, 127, 255, 0)

            # Clean up the current tile by removing small background features
            # (noise) using morphologial operations
            iterations = 2
            thresholded_tile = cv2.erode(thresholded_tile,
                                         structuring_element,
                                         iterations)
            thresholded_tile = cv2.dilate(thresholded_tile,
                                          structuring_element,
                                          iterations)
            thresholded_tile = cv2.dilate(thresholded_tile,
                                          structuring_element,
                                          iterations)
            thresholded_tile = cv2.erode(thresholded_tile,
                                         structuring_element,
                                         iterations)

            # Compute the center of mass of the current thresholded tile
            moments = cv2.moments(thresholded_tile)
            centroid_row = int(moments["m01"] / moments["m00"])
            centroid_col = int(moments["m10"] / moments["m00"])

            # Compute a bounding box for the letter on the current tile
            contours, _ = cv2.findContours(thresholded_tile,
                                           cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)
            max_area= 0
            for contour in contours:
               c, r, w, h = cv2.boundingRect(contour)
               area = w * h
               if area > max_area:
                  max_area = area
                  bb_ul_row = r
                  bb_height = h
                  bb_ul_col = c
                  bb_width = w

            # If the center of mass is to be used to center the letter, set
            # the vertical and horizontal translation factors for the affine
            # transformation matrix
            if use_centroid:
               translation_r = tile_rows // 2 - centroid_row
               translation_c = tile_cols // 2 - centroid_col
            else:
               translation_r = tile_rows // 2 - (bb_ul_row + bb_height // 2)
               translation_c = tile_cols // 2 - (bb_ul_col + bb_width // 2)

            # If the letters are to be size normalized, set the scale factor
            # for the affine matrix
            if use_original_dimensions:
               scale = 1
               scale = 1
            else:
               if bb_height >= bb_width:
                  scale = (fill_ratio * tile_rows) / bb_height
               else:
                  scale = (fill_ratio * tile_cols) / bb_width

            # If currently processing the full-sized tile, annotate a display
            # version of this tile with either the center of mass or the
            # bounding box
            if size is None:
               annotated_tile = tile.copy()
               if use_centroid:
                  cv2.circle(annotated_tile,
                             (centroid_col, centroid_row),
                             3,
                             (0, 0, 255),
                             -1)
               else:
                  cv2.rectangle(annotated_tile,
                               (bb_ul_col, bb_ul_row),
                               (bb_ul_col + bb_width, bb_ul_row + bb_height),
                               (0, 0, 255),
                               2)
               cv2.imshow("Tile (Annotated)", annotated_tile)

            # Center the letter in the current tile
            affine_matrix = numpy.float32([
               [1, 0, translation_c],
               [0, 1, translation_r]
            ])
            adjusted_thresholded_tile = \
               cv2.warpAffine(thresholded_tile,
                              affine_matrix,
                              (tile.shape[1],
                               tile.shape[0]))

            # Scale the image using the fill factor derived window size
            # about the center coordinate of the tile
            center = (tile_cols // 2, tile_rows // 2)
            affine_matrix = cv2.getRotationMatrix2D(center, 0, scale)
            adjusted_thresholded_tile = \
               cv2.warpAffine(adjusted_thresholded_tile,
                              affine_matrix,
                              (tile.shape[1],
                               tile.shape[0]))

            # Count the number of pixels that are on in the specified
            # buffer region
            buffer = 0.50
            image_sum = numpy.sum(adjusted_thresholded_tile, dtype=float) / 255
            buffer_r = int(buffer * int(tile_rows * (1 - fill_ratio) / 2))
            buffer_c = int(buffer * int(tile_cols * (1 - fill_ratio) / 2))
            ul_r = int(tile_rows * (1 - fill_ratio) / 2) - buffer_r
            ul_c = int(tile_cols * (1 - fill_ratio) / 2) - buffer_c
            lr_r = \
               int(tile_rows * (fill_ratio + (1 - fill_ratio) / 2)) + buffer_r
            lr_c = \
               int(tile_cols * (fill_ratio + (1 - fill_ratio) / 2)) + buffer_c
            subimage_sum = \
               numpy.sum(adjusted_thresholded_tile[ul_r:lr_r, ul_c:lr_c],
                         dtype=float) / 255

            # If there are any pixels "on" in the buffer region then reject
            # the current tile and move on to the next
            if abs(subimage_sum - image_sum) > 0:
               reject = True
            else:
               reject = False

            if reject:
               if size is None:
                  msg = 'Rejecting {0} '.format(tile_name)
                  msg += 'based on buffer-zone impingement by sample'
                  print(msg)
               continue

            # If the current tile has made it through the processing and
            # evaluation process, display the full resolution adjusted tile
            if size is None:
               cv2.imshow("Adjusted Thresholded Tile",
                          adjusted_thresholded_tile)

            # If extracted tiles are to be saved to disk, write the current
            # adjusted tile to disk (resizing if required)
            if tiles_base_directory:
               if size:
                  cv2.imwrite(os.path.join(current_tiles_path,
                                           tile_name + '.png'),
                              cv2.resize(adjusted_thresholded_tile,
                                         (size, size),
                                         interpolation=cv2.INTER_LINEAR))
               else:
                  cv2.imwrite(os.path.join(current_tiles_path,
                                           tile_name + '.png'),
                              adjusted_thresholded_tile)

            delay = 10
            k = cv2.waitKey(delay)
            if k == 27:  # <Esc>
               sys.exit()
            if k == 81:  # Q
               sys.exit()
            if k == 113: # q
               sys.exit()

   # Increment the sample number and move on to the next sample/page
   sample += 1

