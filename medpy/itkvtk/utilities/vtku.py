# Copyright (C) 2013 Oskar Maier
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Oskar Maier
# version r0.1.1
# since 2011-11-25
# status Release

# build-in modules

# third-party modules
import itk
import vtk

# path changes

# own modules

# code
def getInformation(image): #tested
    """
    Returns an information string about a VTK image in a compressed way.
    
    Parameters
    ----------
    image : vtk.vtkImageData
        An VTK image as used by WrapITK.
        
    Returns
    -------
    information : string
        Pretty-formatted string with image metadata.
        
    Notes
    -----
    Performs UpdateOutputInformation() on the image, therefore triggering pipeline processing if necessary
    """
    assert isinstance(image, vtk.vtkImageData)
    
    # refresh information
    image.Update()
    image.UpdateInformation()
    
    # request information and format string
    s = 'vtkImageData info:\n'
    s += '\tscalar-type: ' + image.GetScalarTypeAsString() + ' (' + str(image.GetScalarType()) + ')\n'
    s += '\tscalar-range: ' + str(image.GetScalarRange()) + ' of range (' + str(image.GetScalarTypeMin()) + ', ' + str(image.GetScalarTypeMax()) + ')\n'
    s += '\tdimensions: ' + str(image.GetDimensions()) + '\n'
    s += '\tbounds: ' + str(image.GetBounds()) + '\n'
    s += '\tspacing: ' + str(image.GetSpacing()) + '\n'
    s += '\tdata dim.: ' + str(image.GetDataDimension())
    
    return s

def getImageTypeFromVtk(image): # tested
    """
    Returns the image type of the supplied image as itk.Image template.
    
    Parameters
    ----------
    image : vtk.vtkImageData
        An VTK image as used by WrapITK.
    
    Returns
    -------
    image_type : itk.Image (template)
        An itk image type.
    
    Notes
    -----
    Performs Update() and UpdateInformation() on the image, therefore
    triggering pipeline processing if necessary
    """
    assert isinstance(image, vtk.vtkImageData)
    
    # refresh information
    image.Update()
    image.UpdateInformation()    
    
    # Mapping informations taken from vtkSetGet.h
    mapping = {1: itk.B,
               2: itk.SC,
               3: itk.UC,
               4: itk.SS,
               5: itk.UC,
               6: itk.SI,
               7: itk.UI,
               8: itk.SL,
               9: itk.UL,
               10: itk.F,
               11: itk.D}
    
    return itk.Image[mapping[image.GetScalarType()],
                     image.GetDataDimension()]

def saveImageMetaIO(image, file_name): #tested
    """
    Saves the image data into a file as MetaIO format.
    
    Parameters
    ----------
    image : vtk.vtkImageData
        An VTL image as used by WrapITK.
    file_name : string
        Path and file name (without suffix) where to save the image.
    
    Notes
    -----
    A write operation will trigger the image pipeline to be processed.
    """
    assert isinstance(image, vtk.vtkImageData)
    
    writer = vtk.vtkMetaImageWriter()
    writer.SetFileName(file_name + '.mhd')
    writer.SetInput(image)
    writer.Write()
    
# This definitions are taken from vtkSetGet.h
#define     VTK_LARGE_FLOAT   1.0e+38F
#define     VTK_LARGE_ID   2147483647
#define     VTK_LARGE_INTEGER   2147483647
#define     VTK_VOID   0
#define     VTK_BIT   1
#define     VTK_CHAR   2
#define     VTK_UNSIGNED_CHAR   3
#define     VTK_SHORT   4
#define     VTK_UNSIGNED_SHORT   5
#define     VTK_INT   6
#define     VTK_UNSIGNED_INT   7
#define     VTK_LONG   8
#define     VTK_UNSIGNED_LONG   9
#define     VTK_FLOAT   10
#define     VTK_DOUBLE   11
#define     VTK_ID_TYPE   12
#define     VTK_BIT_MIN   0
#define     VTK_BIT_MAX   1
#define     VTK_CHAR_MIN   -128
#define     VTK_CHAR_MAX   127
#define     VTK_UNSIGNED_CHAR_MIN   0
#define     VTK_UNSIGNED_CHAR_MAX   255
#define     VTK_SHORT_MIN   -32768
#define     VTK_SHORT_MAX   32767
#define     VTK_UNSIGNED_SHORT_MIN   0
#define     VTK_UNSIGNED_SHORT_MAX   65535
#define     VTK_INT_MIN   (-VTK_LARGE_INTEGER-1)
#define     VTK_INT_MAX   VTK_LARGE_INTEGER
#define     VTK_UNSIGNED_INT_MIN   0
#define     VTK_UNSIGNED_INT_MAX   4294967295UL
#define     VTK_LONG_MIN   (-VTK_LARGE_INTEGER-1)
#define     VTK_LONG_MAX   VTK_LARGE_INTEGER
#define     VTK_UNSIGNED_LONG_MIN   0
#define     VTK_UNSIGNED_LONG_MAX   4294967295UL
#define     VTK_FLOAT_MIN   -VTK_LARGE_FLOAT
#define     VTK_FLOAT_MAX   VTK_LARGE_FLOAT
#define     VTK_DOUBLE_MIN   -1.0e+99L
#define     VTK_DOUBLE_MAX   1.0e+99L
#define     VTK_POLY_DATA   0
#define     VTK_STRUCTURED_POINTS   1
#define     VTK_STRUCTURED_GRID   2
#define     VTK_RECTILINEAR_GRID   3
#define     VTK_UNSTRUCTURED_GRID   4
#define     VTK_PIECEWISE_FUNCTION   5
#define     VTK_IMAGE_DATA   6
#define     VTK_DATA_OBJECT   7
#define     VTK_DATA_SET   8

# A number of vtkImageData methods with example outputs and comments
#    .getDimensions() -> the official image dimensions
#    (511, 511, 182)
#    .GetBounds() -> the actual bounds (as I use for display)
#    (0.0, 379.25909173488617, 0.0, 379.25909173488617, 0.0, 273.0)
#    .GetCenter() # the half of the bounds
#    (189.62954586744308, 189.62954586744308, 136.5)
#    .GetDataObjectType() # one of VTK_STRUCTURED_GRID, VTK_STRUCTURED_POINTS, VTK_UNSTRUCTURED_GRID, VTK_POLY_DATA, or VTK_RECTILINEAR_GRID
#    6 # VTK_IMAGE_DATA
#    img.GetExtent()
#    (0, 511, 0, 511, 0, 182)
#    .GetExtentType() #VTK_PIECES_EXTENT or VTK_3D_EXTENT
#    1
#    .GetInformation() # try to print this once
#    vtk.Information object
#    .GetLength() # no idea
#    601.8337954345383
#    .GetNumberOfPoints() # 511*511*182
#    47972352L
#    img.GetNumberOfScalarComponents()
#    1
#    .getScalarRange() # range of gray values in this case!
#    (-1024.0, 1680.0)
#    .getScALARtYPE()
#    4
#    .getScalarTypeAsString()
#    'short'
#    .getScalarTypeMax() # max possible value
#    32767.0
#    .getScalarTypeMin() # min possible value
#    -32768.0