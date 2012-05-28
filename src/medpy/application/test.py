#!/usr/bin/python

#
# COMPARISON OF LAPLACIAN OF GAUSSIANS
#

# build-in modules
import itk

# third-party modules

# path changes

# own modules

# code
def main():
    # set parameters
    #image = '00originals/o01.nii'
    #image = '00originals/s01.nii'
    #image = '01gradient/o01_gradient.nii'
    #image = '02watershed/o01_gradient_watershed_thr0.0_lvl0.0.nii'
    image = '05full/03.danimarkers.nii'
    
    loader = itk.NiftiImageIO.New()
    loader.SetFileName(image)
    loader.ReadImageInformation()
    pixel_type = loader.GetPixelTypeAsString(loader.GetPixelType())
    component_type = loader.GetComponentTypeAsString(loader.GetComponentType())
    dimensions = loader.GetNumberOfDimensions()
    components = loader.GetNumberOfComponents()
    
    print pixel_type, component_type, dimensions, components
    
    print "All done."
    
if __name__ == "__main__":
    main()  