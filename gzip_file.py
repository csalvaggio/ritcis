import gzip

def gzip_file(in_filename, out_filename):
   with open(in_filename, 'rb') as f_in, gzip.open(out_filename, 'wb') as f_out:
      f_out.writelines(f_in)
