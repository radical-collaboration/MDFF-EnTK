package require ssrestraints
mol new 1ake-docked-noh_autopsf.psf
mol addfile 1ake-docked-noh_autopsf.pdb
ssrestraints -psf 1ake-docked-noh_autopsf.psf -pdb 1ake-docked-noh_autopsf.pdb -o 1ake-extrabonds.txt -hbonds
exit
