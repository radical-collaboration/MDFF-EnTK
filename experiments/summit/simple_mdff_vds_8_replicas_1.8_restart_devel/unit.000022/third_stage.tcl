mol new 1ake-docked-noh.pdb
package require autopsf
autopsf 1ake-docked-noh.pdb
package require mdff
mdff gridpdb -psf 1ake-docked-noh_autopsf.psf -pdb 1ake-docked-noh_autopsf.pdb -o 1ake-docked-noh_autopsf-grid.pdb
exit
