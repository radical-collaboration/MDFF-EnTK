mol new 1ake-initial.pdb
package require autopsf
autopsf 1ake-initial.pdb
package require mdff
mdff gridpdb -psf 1ake-initial_autopsf.psf -pdb 1ake-initial_autopsf.pdb -o 1ake-initial_autopsf-grid.pdb
exit
