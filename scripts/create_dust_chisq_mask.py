import healpy
import numpy as np

target_percentage = 0.75
path = '/home/eirik/data/processing_mask_data/'

currmask_512 = healpy.read_map(path + 'mask_30ghz_1deg_1000uK_chisq.fits')
currmask_1024 = healpy.read_map(path + 'mask_30ghz_1deg_1000uK_chisq_n1024.fits')
dust_1024 = healpy.read_map(path + 'dust_c0001_k000008.fits')
dust_512 = healpy.ud_grade(dust_1024, 512)
chisq = healpy.read_map(path + 'chisq_c0001_k000008.fits')
chisq_512 = healpy.ud_grade(chisq, 512)
chisq_1024 = healpy.ud_grade(chisq, 1024)

start_percentile = 0.95

newmask_512 = np.ones(12 * 512 ** 2)
newmask_1024 = np.ones(12 * 1024 ** 2)

newmask_512[currmask_512 == 0] = 0
newmask_1024[currmask_1024 == 0] = 0

curr_percentage = 1.0
curr_percentile = start_percentile
while curr_percentage > target_percentage:
    target_dust_1024 = np.quantile(dust_1024, curr_percentile)
    target_dust_512 = np.quantile(dust_512, curr_percentile)
    target_chisq_1024 = np.quantile(chisq_1024, curr_percentile)
    target_chisq_512 = np.quantile(chisq_512, curr_percentile)
    newmask_1024[dust_1024 > target_dust_1024] = 0
    newmask_1024[chisq_1024 > target_chisq_1024] = 0
    newmask_512[dust_512 > target_dust_512] = 0
    newmask_512[chisq_512 > target_chisq_512] = 0
    curr_percentage = max(np.sum(newmask_1024)/len(newmask_1024), np.sum(newmask_512)/len(newmask_512))
    curr_percentile -= 0.01

healpy.write_map('processing_mask_{}_512.fits'.format(target_percentage), [newmask_512]*3)
healpy.write_map('processing_mask_{}_1024.fits'.format(target_percentage), [newmask_1024]*3)
