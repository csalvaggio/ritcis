import numpy

def map_quad_to_quad(imgSize, mapSize, imgX, imgY, mapX, mapY):
   """
   title::
      map_quad_to_quad

   description::
      This method will create a set of coordinate maps to allow a 
      quadrilateral-to-quadrilateral projective remapping to occur.  
      The mapping transformation is defined using the provided 
      quadrilateral vertices defined in a clockwise order beginning at 
      the upper left-hand corner.  The provided image coordinates are 
      targeted to fall at the provided map coordinates.

   attributes::
      imgSize
         A 2-element list containing the dimensions of the source
         image with the form [rows, columns].
      mapSize
         A 2-element list containing the dimensions of the targeted
         map with the form [rows, columns].
      imgX
         An 4-element list containing the x'-component of the vertices 
         of the quadrilateral enclosing the region on the image to be 
         transformed.  The list must have the form [xUL, xUR, xLR, xLL].
      imgY
         An 4-element list containing the y'-component of the vertices 
         of the quadrilateral enclosing the region on the image to be 
         transformed.  The list must have the form [yUL, yUR, yLR, yLL].
      mapX
         An 4-element list containing the x-component of the vertices 
         of the quadrilateral enclosing the region on the map to be 
         targeted.  The list must have the form [xUL, xUR, xLR, xLL].
      mapY
         An 4-element list containing the y-component of the vertices 
         of the quadrilateral enclosing the region on the map to be 
         targeted.  The list must have the form [yUL, yUR, yLR, yLL].

   author::
      Carl Salvaggio

   copyright::
      Copyright (C) 2023, Rochester Institute of Technology

   license::
      GPL

   version::
      1.0.0

   disclaimer::
      This source code is provided "as is" and without warranties as to 
      performance or merchantability. The author and/or distributors of 
      this source code may have made statements about this source code. 
      Any such statements do not constitute warranties and shall not be 
      relied on by the user in deciding whether to use this source code.
      
      This source code is provided without any express or implied warranties 
      whatsoever. Because of the diversity of conditions and hardware under 
      which this source code may be used, no warranty of fitness for a 
      particular purpose is offered. The user is advised to test the source 
      code thoroughly before relying on it. The user must assume the entire 
      risk of using the source code.
   """

   # Based on the provided parameters, set the number of rows in the
   # image and the map
   imgRows, imgColumns = imgSize
   mapRows, mapColumns = mapSize

   # Based on the provided quadrilateral vertices for the image and the
   # targeted image, compute the projective mapping matrix.
   x = imgX
   y = imgY
   u = mapX
   v = mapY
   mappingVector = \
      numpy.asmatrix(
         [[u[0], v[0], 1, 0,    0,    0, -u[0]*x[0], -v[0]*x[0]],
          [u[1], v[1], 1, 0,    0,    0, -u[1]*x[1], -v[1]*x[1]],
          [u[2], v[2], 1, 0,    0,    0, -u[2]*x[2], -v[2]*x[2]],
          [u[3], v[3], 1, 0,    0,    0, -u[3]*x[3], -v[3]*x[3]],
          [0,    0,    0, u[0], v[0], 1, -u[0]*y[0], -v[0]*y[0]],
          [0,    0,    0, u[1], v[1], 1, -u[1]*y[1], -v[1]*y[1]],
          [0,    0,    0, u[2], v[2], 1, -u[2]*y[2], -v[2]*y[2]],
          [0,    0,    0, u[3], v[3], 1, -u[3]*y[3], -v[3]*y[3]]]).I * \
      numpy.asmatrix([x[0], x[1], x[2], x[3], y[0], y[1], y[2], y[3]]).T
   one = numpy.asmatrix([1])
   mappingVector = numpy.concatenate((mappingVector, one))
   mappingMatrix = numpy.reshape(mappingVector, (3,3))

   # Form a matrix of map coordinates to which the image data should be 
   # targeted (the matrix will contain the homogenous coordinates in the 
   # columns)
   rows = numpy.zeros([mapRows, mapColumns])
   rows[:,:] = numpy.arange(mapRows).reshape([mapRows, 1])
   rows = numpy.asmatrix(rows.flatten(), dtype=numpy.float64)
   columns = numpy.zeros([mapRows, mapColumns])
   columns[:,:] = numpy.arange(mapColumns)
   columns = numpy.asmatrix(columns.flatten(), dtype=numpy.float64)
   ones = numpy.asmatrix(numpy.ones(mapRows*mapColumns), dtype=numpy.float64)
   mapCoordinates = numpy.concatenate((columns, rows, ones))

   # Transform the map coordinates to image coordinate space to establish 
   # where the image data should be resampled
   srcMap = mappingMatrix * mapCoordinates

   # Normalize the transformed homogenous coordinates
   srcMap /= srcMap[2,:]
   srcMap /= srcMap[2,:]

   # Reshape the column and row vectors to x and y coordinate maps having
   # the same dimensions as the targeted (map) image
   srcMapX = srcMap[0,:].reshape([mapRows, mapColumns]).astype('float32')
   srcMapY = srcMap[1,:].reshape([mapRows, mapColumns]).astype('float32') 

   # Return the coordinate maps
   return srcMapX, srcMapY
