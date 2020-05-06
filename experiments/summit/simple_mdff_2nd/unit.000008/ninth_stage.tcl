mol new 1ake-docked-noh_autopsf.psf
mol addfile adk-step1.dcd waitfor all
mol new 4ake-target_autopsf.pdb
package require mdff
set selbb [atomselect 0 "backbone"]
set selbbref [atomselect 1 "backbone"]
$selbb frame 0
measure rmsd $selbb $selbbref
$selbb frame last
measure rmsd $selbb $selbbref
exit
