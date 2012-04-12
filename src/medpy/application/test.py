#!/usr/bin/python

#
# COMPARISON OF LAPLACIAN OF GAUSSIANS
#

# build-in modules
import itk

# third-party modules
import scipy
from nibabel.loadsave import load, save
from scipy.ndimage.filters import gaussian_laplace
import time
from medpy.utilities.nibabel import image_like

# path changes

# own modules

# code
def main():
    # set parameters
    sigma = 5.0
    original_image_n = '/home/omaier/Experiments/Regionsegmentation/Evaluation_Viscous/00originalvolumes/o09.nii'
    
    print "Load image for scipy..."
    original_image = load(original_image_n)
    original_image_d = scipy.squeeze(original_image.get_data())
    #original_image_d = original_image_d.astype(scipy.float32)
    
    print "Scipy LoG...",
    scp_log = scipy.zeros(original_image_d.shape, dtype=scipy.float32)
    t1 = time.time()
    gaussian_laplace(original_image_d, sigma, output=scp_log)
    t2 = time.time()
    print t2-t1, "seconds"
    
    print "Load image for ITK..."
    image_type = itk.Image[itk.F, 3]
    reader = itk.ImageFileReader[image_type].New()
    reader.SetFileName(original_image_n)
    reader.Update()
    
    print "To scipy array..."
    itk_orig = itk.PyBuffer[image_type].GetArrayFromImage(reader.GetOutput())
    itk_orig = itk_orig.swapaxes(0, 2) # correct axes
    
    print "Input images the same...",
    print (original_image_d == itk_orig).all()
    
    print "ITK LoG...",
    log_filter = itk.LaplacianRecursiveGaussianImageFilter[image_type, image_type].New()
    log_filter.SetInput(reader.GetOutput())
    log_filter.SetSigma(sigma)
    t1 = time.time()
    log_filter.Update()
    t2 = time.time()
    print t2-t1, "seconds"
    
    print "To scipy array..."
    itk_log = itk.PyBuffer[image_type].GetArrayFromImage(log_filter.GetOutput())
    itk_log = itk_log.swapaxes(0, 2) # correct axes
    
    print "Result shapes the same...",
    print itk_log.shape == scp_log.shape 
    
    print "Result dtypes the same...",
    print itk_log.dtype == scp_log.dtype
    
    print "Resulting inner values the same...",
    print (itk_log[50][50][45:50] == scp_log[50][50][45:50]).all()
     
    print scp_log[50][50][45:50]
    print itk_log[50][50][45:50]
    
    print "All values the same...",
    print (scp_log == itk_log).all()
    
    print "Saving results..."
    scp_img = image_like(scp_log, original_image)
    scp_img.get_header().set_data_dtype(scipy.float32)
    save(scp_img, 'scp_log.nii')
    
    itk_img = image_like(itk_log, original_image)
    itk_img.get_header().set_data_dtype(scipy.float32)
    save(itk_img, 'itk_log.nii')
    
    print "All done."
    
if __name__ == "__main__":
    main()  