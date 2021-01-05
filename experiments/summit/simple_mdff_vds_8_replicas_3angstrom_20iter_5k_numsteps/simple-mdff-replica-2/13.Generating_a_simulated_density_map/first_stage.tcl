mol new 4ake-target.pdb
package require autopsf
autopsf 4ake-target.pdb
set sel [atomselect top all]
package require mdff
mdff sim $sel -res 3.0 -o 4ake-target_autopsf.dx
exit
