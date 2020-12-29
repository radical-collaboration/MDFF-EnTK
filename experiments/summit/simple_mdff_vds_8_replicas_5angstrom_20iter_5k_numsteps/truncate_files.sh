
base_path="simple-mdff*"
find $base_path/ -name *.dx -exec truncate --size 0 {} \;
find $base_path/ -name *pdb -exec truncate --size 0 {} \;
find $base_path/ -name *dcd -exec truncate --size 0 {} \;
find $base_path/ -name *psf -exec truncate --size 0 {} \;
find $base_path/ -name *prm -exec truncate --size 0 {} \;

