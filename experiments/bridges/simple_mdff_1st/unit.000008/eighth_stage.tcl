mol new 1ake-initial_autopsf.psf
mol addfile adk-step1.dcd waitfor all
mol new 4ake-target_autopsf.pdb
package require mdff
mdff check -rmsd -refpdb 4ake-target_autopsf.pdb
exit
