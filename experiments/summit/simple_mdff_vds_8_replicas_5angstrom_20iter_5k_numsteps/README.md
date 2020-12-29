# Readable directory name

unit.xxxxxx directory has been renamed to stage name per replica (pipeline)

## Helper scripts

`make_readable_dir.sh` renames unit directory to stage names per pipeline, for example,

- simple-mdff-replica-0  (last digit indicates index of the replica)
  - 0.Calculating_the_cross-correlation_coefficient (first digit indicates an index of iteration)
  - 0.Calculating_the_cross-correlation_coefficient_of_full_trajectory
  - 0.Converting_the_density_map_to_an_MDFF_potential 
  - 0.Defining_secondary_structure_restraints 
  - 0.Generating_a_simulated_density_map 
  - 0.NAMD_simulation
  - 0.Preparing_the_initial_structure
  - 0.Running_the_MDFF_simulation_with_NAMD 

`truncate_file.sh` removes contents of the files in order to reduce git commit size
  - .dcd
  - .psf
  - .dx
  - .pdb
  - .prm
