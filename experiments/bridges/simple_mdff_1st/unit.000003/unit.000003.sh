#!/bin/sh


# Environment variables
export RP_SESSION_ID="re.session.two.hrlee.018334.0000"
export RP_PILOT_ID="pilot.0000"
export RP_AGENT_ID="agent.0"
export RP_SPAWNER_ID="agent_executing.0000"
export RP_UNIT_ID="unit.000003"
export RP_UNIT_NAME="task.0003,None,stage.0003,Defining secondary structure restraints,pipeline.0000,simple-mdff"
export RP_GTOD="/pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/gtod"
export RP_TMP="None"
export RP_PILOT_STAGING="/pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/staging_area"
export RP_PROF="/pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/unit.000003//unit.000003.prof"

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
cd /pylon5/mc3bggp/hrlee/radical.pilot.sandbox/re.session.two.hrlee.018334.0000/pilot.0000/unit.000003/
prof cu_cd_done

# Pre-exec commands
prof cu_pre_start
module load vmd/1.9.2 ||  (echo "pre_exec failed"; false) || exit
echo 'package require ssrestraints
mol new 1ake-initial_autopsf.psf
mol addfile 1ake-initial_autopsf.pdb
ssrestraints -psf 1ake-initial_autopsf.psf -pdb 1ake-initial_autopsf.pdb -o 1ake-extrabonds.txt -hbonds
exit' > fourth_stage.tcl ||  (echo "pre_exec failed"; false) || exit
prof cu_pre_stop

# The command to run
prof cu_exec_start
vmd -dispdev text -e fourth_stage.tcl
RETVAL=$?
prof cu_exec_stop

# Exit the script with the return code from the command
prof cu_stop
exit $RETVAL
