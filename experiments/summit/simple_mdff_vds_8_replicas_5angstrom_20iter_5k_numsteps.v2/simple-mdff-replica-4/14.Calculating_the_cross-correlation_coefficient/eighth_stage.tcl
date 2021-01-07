mol new 1ake-docked-noh_autopsf.psf
mol addfile adk-step1.dcd waitfor all
set outfilename cc.dat
package require mdff
set selall [atomselect 0 "all"]
$selall frame 0
set lcc [mdff ccc $selall -i 4ake-target_autopsf.dx -res 5.0]
$selall frame last
set fcc [mdff ccc $selall -i 4ake-target_autopsf.dx -res 5.0]
lappend cc $lcc $fcc
set outfile [open $outfilename w]
puts $outfile "$cc"
exit
