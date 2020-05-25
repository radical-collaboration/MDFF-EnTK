# Summary

Each directory contains the result of the workflow execution with tasks, and the task is named by `unit.` with indexed numbers. Each unit has the following files:

- STDOUT: standard output messages captured
- STDERR: standard error messages captured
- unit.*.sh: actual script executed for the task
- unit.*.sl and unit.*.rs: resource description file per task
- unit.*.prof: events recorded with unix timestamp for profiling purpose
- other files: copied/linked

## Summit

- [simple_mdff_1st](summit/simple_mdff_1st): failed at stage 6	
- [simple_mdff_2nd](summit/simple_mdff_2nd): finished but `target-density-5A.dx` isn't used at stage 10
- [simple_mdff_2nd_5_replica](summit/simple_mdff_2nd_5_replica): finished with 5 replica
- [simple_mdff_final](summit/simple_mdff_final): finished 1 iteration with `target-density-5A.dx`
- [simple_mdff_final_5_replica](summit/simple_mdff_final_5_replica): finished with 5 replica

## Bridges

- [simple_mdff_1st](bridges/simple_mdff_1st): first complete set of task executions
