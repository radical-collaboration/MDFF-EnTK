package require ssrestraints
mol new 1ake-initial_autopsf.psf
mol addfile 1ake-initial_autopsf.pdb
ssrestraints -psf 1ake-initial_autopsf.psf -pdb 1ake-initial_autopsf.pdb -o 1ake-extrabonds.txt -hbonds
exit
