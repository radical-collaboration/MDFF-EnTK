package require ssrestraints
mol new 1ake-docked-noh_autopsf.psf
mol addfile 1ake-docked-noh_autopsf.pdb
ssrestraints -psf 1ake-docked-noh_autopsf.psf -pdb 1ake-docked-noh_autopsf.pdb -o 1ake-extrabonds.txt -hbonds
package require cispeptide
package require chirality
cispeptide restrain -o 1ake-extrabonds-cispeptide.txt
chirality restrain -o 1ake-extrabonds-chirality.txt
exit
