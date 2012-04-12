"""
@package medpy.graphcut.cut
Prepares, compiles and executed graph-cut implementations using the graphs created by
the graph module of this package.

Note that the functionality provided by this module depends highly on the platform, the
availability of 3rd party tools and executes foreign code. It should only be used when
completely understood. Otherwise manual execution of this step is preferable.

All functions in this module are highly depend on the actual implementation of the
graph-cut algorithm they are intended to be used for. They require a minimal version
number and it can not be ensured, that they will work with other versions.

See the package description for a list of the supported graph-cut implementations.

Functions:
    - def bk_mfmc_cut(source_file, gpp_location = False): Execute a graph cut using Boyov and
                                                          Kolmogorovs max-flow/min-cut algorithm.

@author Oskar Maier
@version d0.1.0
@since 2012-01-18
@status Development
"""

# build-in modules
import os
import tempfile
import subprocess
import warnings

# third-party modules

# own modules
from ..core.Logger import Logger
from ..core.exceptions import SubprocessError
from .generate import __bk_mfmc_get_library


#####
# BK_MFMC: Boyov and Kolmogorovs (1) C++ max-flow/min-cut implementation (a)
#####

def bk_mfmc_cut(source_file, gpp_location = False, keep = False):
    """
    Execute a graph cut using the supplied source file of Boyov and Kolmogorovs
    max-flow/min-cut algorithm.
    
    The source-file is written to a temporary directory, compiled and the executed. The
    created output is caught and returned.
    
    @note: This function assumes g++ - GNU project C++ compiler to be installed
    on the host machine. Alternatively the path to g++ can be provided.
    
    @warning: If not handled with care, this function can be used to compile and execute
    arbitrary code on the host machine. Ensure that the input of this function can not
    be generated or modified by the user and always comes from @link: bk_mfmc_generate().
    
    @param source_file: The C++ source file as returned by @link: bk_mfmc_generate().
    @type source_file: str
    @param gpp_location: The location of g++ - the GNU project C++ compiler.
    @type gpp_location: str
    @param keep: Set this to true to keep the temporary directory after execution.
                 This parameter is intended for debugging purposes only.
    @type keep: bool
    @return: The results as a string to be parsed by @link: bk_mfmc_parse().
    @rtype: str
    
    @raise SubprocessError: When the one step of the compiling or execution can not be
                            assured to have terminated succesfully.
    """
    # prepare logger
    logger = Logger.getInstance()
    
    logger.info('Creating temporary file structure...')
    
    # get the algorithms library
    library = __bk_mfmc_get_library()
    
    # prepare temporary file structure and library links
    try:
        tmp_dir = tempfile.mkdtemp()
    except Exception as e:
        raise SubprocessError('Failed to reate a temporary directory, reason {}.'.format(e.message), e)
    executable = tmp_dir + '/compute'
    mygraph_file = tmp_dir + '/mygraph.cpp'
    
    logger.debug('Temporary files can be found in {} (set keep=True to keep)'.format(tmp_dir))

    # generate cpp file with the graph encoded
    with open(mygraph_file, 'w') as f:
        f.write(source_file)
    
    # compile the application
    logger.info('Compiling...')
    if not gpp_location: gpp_location = 'g++'
    cmd = [gpp_location, '-o', executable, mygraph_file, library['graph_file'], library['maxflow_file']]
    logger.debug('Command: ' + ' '.join(cmd))
    try:
        fnull = open(os.devnull, 'w')
        subprocess.check_call(cmd, stdout=fnull, stderr=fnull)
    except subprocess.CalledProcessError as e:
        if not keep: __bk_mfmc_clean_tmp(tmp_dir, mygraph_file)
        raise SubprocessError('Compiling the application failed with exit code {} and message {}.'.format(e.returncode, e.output))
        
    # execute the binary and collect the output
    logger.info('Executing...')
    try:
        result = subprocess.check_output(executable)
    except subprocess.CalledProcessError as e:
        if not keep: __bk_mfmc_clean_tmp(tmp_dir, mygraph_file, executable)
        raise SubprocessError('Executing the binary returned an exit code {} with message {} ({}).'.format(e.returncode, e.output, e.message))
    except Exception as e:
        if not keep: __bk_mfmc_clean_tmp(tmp_dir, mygraph_file, executable)
        raise SubprocessError('Executing the binary failed due to reason {}.'.format(e.message))    
    
    if not keep:
        try:
            os.remove(mygraph_file)
            os.remove(executable)
            os.rmdir(tmp_dir)
        except Exception as e:
            warnings.warn('Could not clean up all of the temporary files, reason {}. They can be found in {} for manually cleaning, but that should not be necessary.'.format(e.message, tmp_dir))
    
    return result

def __bk_mfmc_clean_tmp(directory, file1 = False, file2 = False):
    """
    Convenient temp file cleaning.
    """
    try:
        if file1: os.remove(file1)
        if file2: os.remove(file2)
        os.rmdir(directory)
    except Exception as e:
        warnings.warn('Could not clean up all of the temporary files, reason {}. They can be found in {} for manually cleaning, but that should not be necessary.'.format(e.message, directory))

