#!/bin/bash

maptool=~/quietsvn/oslo/src/f90/maptool/maptool

sample=00015
version=v02
prefix=rc2_n256

comp="cmb ame1 ame1_nup ame2 ame2_nup co10 co10_100-ds2 co21 co21_217-2 co21_217-3 co21_217-4 co32 co32_353-1 dust dust_beta dust_Td ff ff_EM ff_T_e hcn hcn_100-ds2 hcn_W1 hcn_W2 hcn_W3 hcn_W4 synch synch_nup sz"
polcomp="synch_nup dust_beta dust_Td"

for i in $comp; do
    cp ${i}_c0001_k${sample}.fits ../init_${i}_${prefix}_${version}.fits
done

for i in $polcomp; do
    $maptool extract 3 ${i}_c0001_k${sample}.fits 1 1 1 ../init_${i}_${prefix}_${version}.fits
done

cp temp_amp_c0001_k$sample.dat ../md_init_${prefix}_$version.dat
cp gain_no0001.dat ../gain_init_${prefix}_$version.dat
cp bp_no0001.dat ../bp_init_${prefix}_$version.dat
