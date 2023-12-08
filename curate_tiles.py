import argparse
import cv2
import fnmatch
import os
import os.path

description = 'Curate the tiles (remove bad instances) that have been '
description += 'extracted from the RITCIS handwritten letters forms'

parser = argparse.ArgumentParser(description=description)

help_message = 'sample ID number to curate'
parser.add_argument('sample_to_curate',
                    type=int,
                    help=help_message)

help_message = 'path to the directory containing the RITCIS data tiles '
help_message += '(the directory containing the "full" resolution folder '
help_message += 'should be selected '
help_message += '[default is "samples/tiles"]'
parser.add_argument('-t', '--tiles-path',
                    dest='tiles_path',
                    type=str,
                    default='samples/tiles',
                    help=help_message)

help_message = 'tile image extension '
help_message += '[default is "png"]'
parser.add_argument('-e', '--extension',
                    dest='tile_extension',
                    type=str,
                    default='png',
                    help=help_message)

args = parser.parse_args()

sample_to_curate = args.sample_to_curate
tiles_path = args.tiles_path
tile_extension = '.' + args.tile_extension

# Trim path if the last character is the OS-specific path separator
if tiles_path[-1] == os.path.sep:
   tiles_path = tiles_path[:-1]

# Find all of the tile files in the "full" folder located in the tiles
# path directory tree for the sample ID specified
sample_directory = '{:03d}'.format(sample_to_curate)
tile_files = []
for root, dirs, files in os.walk(os.path.join(tiles_path,
                                              'full',
                                              sample_directory)):
   for file in fnmatch.filter(files, '*.png'):
      tile_files.append(os.path.join(root, file))
tile_files.sort()

# Describe the action keys to the user
msg = ''
print(msg)
msg = 'Sample: {:03d}'.format(sample_to_curate)
print(msg)
msg = ''
print(msg)
msg = 'AVAILABLE ACTIONS'
print(msg)
msg = 'k | n          -->  will (k)eep the current sample and move on to '
msg += 'the (n)ext'
print(msg)
msg = 'r | d          -->  will (r)emove / (d)elete the current sample'
print(msg)
msg = 'b | p          -->  will (b)ack up to the (p)revious sample'
print(msg)
msg = '<Esc> | q | Q  -->  will (q)uit the program'
print(msg)
msg = ''
print(msg)

# Display each tile
idx = 0
while idx < len(tile_files):
   src = cv2.imread(tile_files[idx], cv2.IMREAD_UNCHANGED)
   cv2.imshow('Tile to Examine', src)

   # Pause for the desired action
   while True:
      k = cv2.waitKey(0)

      # Exit program
      if k == 27 or k == 113 or k == 81:  # <Esc> or 'q' or 'Q'
         msg = 'Exiting ...'
         print(msg)
         exit()

      # Keep current tile and move on to the next sample
      if k == 107 or k == 110:  # 'k' or 'n'
         msg = 'Keeping ' + os.path.basename(tile_files[idx])
         print(msg)
         break

      # Remove all versions of the current tile and move on to the next sample
      if k == 114 or k == 100:  # 'r' or 'd'
         msg = 'Removing all versions/resolutions of '
         msg += '{}'.format(os.path.basename(tile_files[idx]))
         print(msg)
         msg = '... {}'.format(tile_files[idx])
         print(msg)
         os.remove(tile_files[idx])
         sizes = [28, 56, 112, 224]             
         for size in sizes:
            path_to_remove = tile_files[idx].replace('full',
                                                     '{:03d}'.format(size))
            msg = '... {}'.format(path_to_remove)
            print(msg)
            os.remove(path_to_remove)
         tile_files.pop(idx)
         idx -= 1
         break

      # Back up one tile file in the list to re-examine
      if k == 98 or k == 112:  # 'b' or 'p'
         if idx == 0:
            idx = -1
         else:
            idx -= 2
         msg = 'Backing up to '
         msg += '{}'.format(os.path.basename(tile_files[idx+1]))
         print(msg)
         break

   idx += 1
