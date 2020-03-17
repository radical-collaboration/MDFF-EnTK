#!/bin/sh


# Environment variables
export RP_SESSION_ID="re.session.two.hrlee.018334.0000"
export RP_PILOT_ID="pilot.0000"
export RP_AGENT_ID="agent.0"
export RP_SPAWNER_ID="agent_executing.0000"
export RP_UNIT_ID="unit.000007"
export RP_UNIT_NAME="task.0007,None,stage.0007,Calculating the root mean square deviation,pipeline.0000,simple-mdff"
export RP_GTOD="/pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/gtod"
export RP_TMP="None"
export RP_PILOT_STAGING="/pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/staging_area"
export RP_PROF="/pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/unit.000007//unit.000007.prof"

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
export OMP_NUM_THREADS="28"

prof cu_start

# Change to unit sandbox
cd /pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/unit.000007/
prof cu_cd_done

# Pre-exec commands
prof cu_pre_start
module load vmd/1.9.2 ||  (echo "pre_exec failed"; false) || exit
echo 'mol new 1ake-initial_autopsf.psf
mol addfile adk-step1.dcd waitfor all
mol new 4ake-target_autopsf.pdb
package require mdff
mdff check -rmsd -refpdb 4ake-target_autopsf.pdb
exit' > eighth_stage.tcl ||  (echo "pre_exec failed"; false) || exit
prof cu_pre_stop

# The command to run
prof cu_exec_start
vmd -dispdev text -e eighth_stage.tcl
RETVAL=$?
prof cu_exec_stop

# Exit the script with the return code from the command
prof cu_stop
exit $RETVAL
