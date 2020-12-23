#!/bin/sh


# Environment variables
export RADICAL_BASE="/gpfs/alpine/bip115/scratch/hrlee/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000"
export RP_SESSION_ID="re.session.login5.hrlee.018617.0020"
export RP_PILOT_ID="pilot.0000"
export RP_AGENT_ID="agent.0"
export RP_SPAWNER_ID="agent_executing.0000"
export RP_UNIT_ID="unit.000158"
export RP_UNIT_NAME="task.0092,task5,stage.0092,Running the MDFF simulation with NAMD,pipeline.0003,simple-mdff-replica-3"
export RP_GTOD="/gpfs/alpine/bip115/scratch/hrlee/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000/gtod"
export RP_TMP="None"
export RP_PILOT_SANDBOX="/gpfs/alpine/bip115/scratch/hrlee/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000"
export RP_PILOT_STAGING="/gpfs/alpine/bip115/scratch/hrlee/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000/staging_area"
export RP_PROF="/gpfs/alpine/scratch/hrlee/bip115/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000/unit.000158//unit.000158.prof"

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

prof cu_start

# Change to unit sandbox
cd /gpfs/alpine/scratch/hrlee/bip115/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000/unit.000158/

# Pre-exec commands
prof cu_pre_start
echo 'package require mdff
mdff setup -o adk -psf 1ake-docked-noh_autopsf.psf -pdb 1ake-docked-noh_autopsf.pdb -griddx 4ake-target_autopsf-grid.dx -gridpdb 1ake-docked-noh_autopsf-grid.pdb -extrab {1ake-extrabonds.txt 1ake-extrabonds-cispeptide.txt 1ake-extrabonds-chirality.txt} -gscale 0.3 -minsteps 1000 -numsteps 100000
exit' > fifth_stage.tcl ||  (echo "pre_exec failed"; false) || exit
prof cu_pre_stop

# The command to run
prof cu_exec_start
/opt/ibm/spectrum_mpi/jsm_pmix/bin/jsrun --erf_input /gpfs/alpine/scratch/hrlee/bip115/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000/unit.000158//unit.000158.rs   /gpfs/alpine/world-shared/bip115/VMD_binaries/VMD-1.9.3-xlc-build-2019-Dec-12/bin/vmd -dispdev text -e fifth_stage.tcl
RETVAL=$?
prof cu_exec_stop

# Exit the script with the return code from the command
prof cu_stop
exit $RETVAL
