mol new 1ake-docked-noh_autopsf.psf
mol addfile 1ake-docked-noh_autopsf.pdb
package require cispeptide
package require chirality
cispeptide restrain -o 1ake-extrabonds-cispeptide.txt
chirality restrain -o 1ake-extrabonds-chirality.txt
exit
