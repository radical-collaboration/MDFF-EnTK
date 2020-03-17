#!/bin/sh


# Environment variables
export RP_SESSION_ID="re.session.two.hrlee.018334.0000"
export RP_PILOT_ID="pilot.0000"
export RP_AGENT_ID="agent.0"
export RP_SPAWNER_ID="agent_executing.0000"
export RP_UNIT_ID="unit.000006"
export RP_UNIT_NAME="task.0006,None,stage.0006,NAMD simulation,pipeline.0000,simple-mdff"
export RP_GTOD="/pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/gtod"
export RP_TMP="None"
export RP_PILOT_STAGING="/pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/staging_area"
export RP_PROF="/pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/unit.000006//unit.000006.prof"

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
cd /pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/unit.000006/
prof cu_cd_done

# Pre-exec commands
prof cu_pre_start
module load namd/2.12_cpu ||  (echo "pre_exec failed"; false) || exit
prof cu_pre_stop

# The command to run
prof cu_exec_start
namd2 "+ppn" "28" "adk-step1.namd" 
RETVAL=$?
prof cu_exec_stop

# Exit the script with the return code from the command
prof cu_stop
exit $RETVAL
