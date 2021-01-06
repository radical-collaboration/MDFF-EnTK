mol new 1ake-docked-noh_autopsf.psf
mol addfile adk-step1.dcd waitfor all
package require mdff
mdff check -ccc -map 4ake-target_autopsf.dx -res 3.0 waitfor -1 -cccfile all.cc.dat
exit
