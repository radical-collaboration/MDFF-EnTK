#!/bin/sh


# Environment variables
export RP_SESSION_ID="re.session.login4.hrlee.018389.0000"
export RP_PILOT_ID="pilot.0000"
export RP_AGENT_ID="agent.0"
export RP_SPAWNER_ID="agent_executing.0000"
export RP_UNIT_ID="unit.000032"
export RP_UNIT_NAME="task.0032,Starting to load the initial structure,stage.0032,Preparing the initial structure,pipeline.0000,simple-mdff"
export RP_GTOD="/gpfs/alpine/csc393/scratch/hrlee/radical.pilot.sandbox/re.session.login4.hrlee.018389.0000/pilot.0000/gtod"
export RP_TMP="None"
export RP_PILOT_STAGING="/gpfs/alpine/csc393/scratch/hrlee/radical.pilot.sandbox/re.session.login4.hrlee.018389.0000/pilot.0000/staging_area"
export RP_PROF="/gpfs/alpine/scratch/hrlee/csc393/radical.pilot.sandbox/re.session.login4.hrlee.018389.0000/pilot.0000/unit.000032//unit.000032.prof"

prof(){
    if test -z "$RP_PROF"
    then
        return
    fi
    event=$1
    msg=$2
    now=$($RP_GTOD)
    echo "$now,$event,unit_script,MainThread,$RP_UNIT_ID,AGENT_EXECUTING,$msg" >> $RP_PROF
}
export OMP_NUM_THREADS="4"
export "CUDA_VISIBLE_DEVICES="

prof cu_start

# Change to unit sandbox
cd /gpfs/alpine/scratch/hrlee/csc393/radical.pilot.sandbox/re.session.login4.hrlee.018389.0000/pilot.0000/unit.000032/
prof cu_cd_done

# Pre-exec commands
prof cu_pre_start
echo 'mol new 1ake-docked-noh.pdb
package require autopsf
autopsf 1ake-docked-noh.pdb
package require mdff
mdff gridpdb -psf 1ake-docked-noh_autopsf.psf -pdb 1ake-docked-noh_autopsf.pdb -o 1ake-docked-noh_autopsf-grid.pdb
exit' > third_stage.tcl ||  (echo "pre_exec failed"; false) || exit
prof cu_pre_stop

# The command to run
prof cu_exec_start
/opt/ibm/spectrum_mpi/jsm_pmix/bin/jsrun --erf_input /gpfs/alpine/scratch/hrlee/csc393/radical.pilot.sandbox/re.session.login4.hrlee.018389.0000/pilot.0000/unit.000032//unit.000032.rs   /gpfs/alpine/world-shared/bip115/VMD_binaries/VMD-1.9.3-xlc-build-2019-Dec-12/bin/vmd -dispdev text -e third_stage.tcl
RETVAL=$?
prof cu_exec_stop

# Exit the script with the return code from the command
prof cu_stop
exit $RETVAL
