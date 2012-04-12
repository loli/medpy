#!/usr/bin/python
 
"""@file Holds a number of utility function to process ITK images."""

# build-in modules

# third-party modules
import itk
import vtk

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "r0.3, 2011-11-25"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release" # tested functions marked with tested keyword
__description__ = "ITK image utility functions."

# code
def getInformation(image): # tested
    """
    Returns an information string about a ITK image in a compressed way.
    Note: Performs UpdateOutputInformation() on the image, therefore
          triggering pipeline processing if necessary
    Note: Only works on 3D images.
    @param image: an instance of itk.Image
    @return: formatted information string
    """
    # refresh information
    image.UpdateOutputInformation()
    
    # request information and format string
    s = 'itkImageData info:\n'
    s += '\tscalar-type: ' + str(itk.template(image)[1][0]) + '\n'
    rs = image.GetLargestPossibleRegion().GetSize()
    s += '\tdimensions: ' + str(rs.GetElement(0)) + ', ' + str(rs.GetElement(1)) +  ', ' + str(rs.GetElement(2)) + '\n'
    sp = image.GetSpacing()
    s += '\tspacing: ' + str(sp.GetElement(0)) + ', ' + str(sp.GetElement(1)) +  ', ' + str(sp.GetElement(2)) + '\n'
    o = image.GetOrigin() 
    s += '\torigin: ' + str(o.GetElement(0)) + ', ' + str(o.GetElement(1)) +  ', ' + str(o.GetElement(2)) + '\n'
    #s += '\tdata dim.:' + str(image.GetImageDimension()) # fails sometimes due to unknown reasons
    s += '\tdata dim.: ' + str(itk.template(image)[1][1]) # alternative impl. for when GetImageDimension() fails 
    
    return s

def getInformationWithScalarRange(image): # tested
    """
    Behaves like getInformation() but also computes the intensity range,
    which is computationally expensive.
    Note: Performs Update() on the image, therefore
          triggering pipeline processing if necessary
    """
    s = getInformation(image)
    
    # refresh data
    image.Update()
    
    # initiate max/min intensity value computer
    calc = itk.MinimumMaximumImageCalculator[getImageType(image)].New()
    calc.SetImage(image)
    calc.Compute()
    
    s += '\n'
    s += '\tscalar-range: (' + str(calc.GetMinimum()) + ', ' + str(calc.GetMaximum()) + ')\n'
    
    return s

def saveImageMetaIO(image, file_name): # tested
    """
    Saves the image data into a file as MetaIO format.
    Note: A write operation will trigger the image pipeline to be processed.
    @param image: an instance of itk.Image
    @param file_name: path to the save file as string, \wo file-suffix
    """
    saveImage(image, file_name + '.mhd')
    
def saveImage(image, file_name): # tested
    """
    Saves the image data into a file in the format specified by the file name suffix.
    Note: A write operation will trigger the image pipeline to be processed.
    @param image: an instance of itk.Image
    @param file_name: path to the save file as string, \w file-suffix
    """
    # retrieve image type
    image_type = getImageType(image)
    
    writer = itk.ImageFileWriter[image_type].New()
    writer.SetInput(image)
    writer.SetFileName(file_name)
    writer.Write()
    
def getImageType(image): # tested
    """
    Returns the image type of the supplied image as itk.Image template.
    @param image: an instance of itk.Image
    """
    try:
        return itk.Image[itk.template(image)[1][0],
                         itk.template(image)[1][1]]
    except IndexError as e:
        raise NotImplementedError, 'The python wrappers of ITK define no template class for this data type.'
    
def getImageTypeFromVtk(image): # tested
    """
    Returns the image type of the supplied image as itk.Image template.
    Note: Performs Update() and UpdateInformation() on the image, therefore
          triggering pipeline processing if necessary
    @param image: an instance of vtk.vtkImageData
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
    