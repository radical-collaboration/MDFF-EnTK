mol new 1ake-docked-noh_autopsf.psf
mol addfile adk-step1.dcd waitfor all
package require mdff
set selall [atomselect 0 "all"]
$selall frame 0
mdff ccc $selall -i target-density-5A.dx -res 5
$selall frame last
mdff ccc $selall -i target-density-5A.dx -res 5
exit
