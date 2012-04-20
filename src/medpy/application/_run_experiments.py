#!/usr/bin/python

import subprocess
from medpy.core import Logger
import logging

def main():
    # prepare logger
    logger = Logger.getInstance()
    logger.setLevel(logging.INFO)
    
    processors = 2 # img 8, 11 + 19 (just barley) require 2 processors only (memory problem); 2,3,6 + 14 can run with 4
    
    exp_sigmas = range(10,31,1) # 1-30,2 # 1-10,2 + 10-30,1 + 30-40,2 + 40-100,5
    pow_sigmas = [i/10. for i in range(5, 16)] # 0.5-1.5,0.1 # ROI: 0.5-1.5,0.1 + 2-10,1
    div_sigmas = [i/10. for i in range(1, 11)] + range(2, 11) # ROI: 0.1-1,0.1 + 1-10
    
    # split into sublists of size processors
    #exp_sigmas = [exp_sigmas[i:i+processors] for i in range(0, len(exp_sigmas), processors)]
    #pow_sigmas = [pow_sigmas[i:i+processors] for i in range(0, len(pow_sigmas), processors)]
    #div_sigmas = [div_sigmas[i:i+processors] for i in range(0, len(div_sigmas), processors)]
    
    execute('exp', exp_sigmas, logger)
    #execute('pow', pow_sigmas, logger)
    #execute('div', div_sigmas, logger)
    
def execute(bterm, sigmas, logger):
    logger.info('Running for boundary term {}'.format(bterm))
    for image_id in range(1, 21): # iterate over images
        
        # taking into account image memory requirements
        if image_id in [5,8,11,19]: processors = 2
        elif image_id in [2,3,6,14]: processors = 4
        else: processors = 2
        
        if image_id < 10: image_id = '0{}'.format(image_id)
        else: image_id = '{}'.format(image_id)
        
        logger.info('Processing image {} with {} sigmas in parallel...'.format(image_id, processors))
        
        left = 0 
        while left < len(sigmas):
            processes = []
            
            # cut
            for sigma in sigmas[left:left + processors]: 
                cmd = '/usr/bin/time -f "%E;%M;%W" --output tmp_time_{} ./graphcut_voxel.py {} 00originals/o{}.nii 03danimarkers/{}.fg.nii 03danimarkers/{}.bg.nii tmp_result_{}.nii --boundary=diff_{} -vd >> cut_log 2>> cut_err'.format(
                            sigma, sigma, image_id, image_id, image_id, sigma, bterm)
                logger.info('Running: {}'.format(cmd))
                processes.append([sigma, image_id, subprocess.Popen(cmd, shell=True)])
                
            # increase counter
            left = left + processors
                
            # wait for all cuts to terminate
            logger.info('Waiting for cuts to terminate...')
            for process in processes: process[2].wait()
            
            # evaluate & parse results
            logger.info('Evaluate, parse and delete...')
            for process in processes:
                cmd = './evaluate.py tmp_evaluate_{} 00originals/s{}.nii tmp_result_{}.nii -v >> eval_log 2>> eval_err'.format(
                            process[0], process[1], process[0])
                logger.info('Running: {}'.format(cmd))
                subprocess.call(cmd, shell=True) # evaluate
                cmd = './_parse_results.py {} {} {} tmp_time_{} tmp_evaluate_{}.csv result_exp_detailed.csv'.format(process[1],
                                                                  bterm,
                                                                  process[0],
                                                                  process[0],
                                                                  process[0])
                logger.info('Running: {}'.format(cmd))
                subprocess.call(cmd, shell=True) # parse
                # clean files
                subprocess.call('rm tmp_time_{}'.format(process[0]), shell=True)
                subprocess.call('rm tmp_evaluate_{}.csv'.format(process[0]), shell=True)
                subprocess.call('rm tmp_result_{}.nii'.format(process[0]), shell=True)        
        
#        for sigmas in sigmas_grouped:
#            logger.info('Processing sigma group {}'.format(sigmas))
#            processes = []
#            # cut
#            for sigma in sigmas:
#                cmd = '/usr/bin/time -f "%E;%M;%W" --output tmp_time_{} ./graphcut_voxel.py {} 00originals/o{}.nii 03danimarkers/{}.fg.nii 03danimarkers/{}.bg.nii tmp_result_{}.nii --boundary=diff_{} -vd >> cut_log 2>> cut_err'.format(
#                            sigma, sigma, image_id, image_id, image_id, sigma, bterm)
#                logger.info('Running: {}'.format(cmd))
#                processes.append([sigma, image_id, subprocess.Popen(cmd, shell=True)])
#                
#            # wait for all cuts to terminate
#            logger.info('Waiting for cuts to terminate...')
#            for process in processes: process[2].wait()
#            
#            # evaluate & parse results
#            logger.info('Evaluate, parse and delete...')
#            for process in processes:
#                cmd = './evaluate.py tmp_evaluate_{} 00originals/s{}.nii tmp_result_{}.nii -v >> eval_log 2>> eval_err'.format(
#                            process[0], process[1], process[0])
#                logger.info('Running: {}'.format(cmd))
#                subprocess.call(cmd, shell=True) # evaluate
#                cmd = './_parse_results.py {} {} {} tmp_time_{} tmp_evaluate_{}.csv result.csv'.format(process[1],
#                                                                  bterm,
#                                                                  process[0],
#                                                                  process[0],
#                                                                  process[0])
#                logger.info('Running: {}'.format(cmd))
#                subprocess.call(cmd, shell=True) # parse
#                # clean files
#                subprocess.call('rm tmp_time_{}'.format(process[0]), shell=True)
#                subprocess.call('rm tmp_evaluate_{}.csv'.format(process[0]), shell=True)
#                subprocess.call('rm tmp_result_{}.nii'.format(process[0]), shell=True)

if __name__ == "__main__":
    main()
