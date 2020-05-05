package require mdff
mdff setup -o adk -psf 1ake-docked-noh_autopsf.psf -pdb 1ake-docked-noh_autopsf-docked.pdb -griddx 4ake-target_autopsf-grid.dx -gridpdb 1ake-docked-noh_autopsf-grid.pdb -extrab {1ake-extrabonds.txt 1ake-extrabonds-cispeptide.txt 1ake-extrabonds-chirality.txt} -gscale 0.3 -numsteps 50000
exit
