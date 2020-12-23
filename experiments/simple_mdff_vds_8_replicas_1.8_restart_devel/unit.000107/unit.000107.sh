#!/bin/sh


# Environment variables
export RADICAL_BASE="/gpfs/alpine/bip115/scratch/hrlee/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000"
export RP_SESSION_ID="re.session.login5.hrlee.018617.0020"
export RP_PILOT_ID="pilot.0000"
export RP_AGENT_ID="agent.0"
export RP_SPAWNER_ID="agent_executing.0000"
export RP_UNIT_ID="unit.000107"
export RP_UNIT_NAME="task.0109,task6,stage.0109,NAMD simulation,pipeline.0004,simple-mdff-replica-4"
export RP_GTOD="/gpfs/alpine/bip115/scratch/hrlee/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000/gtod"
export RP_TMP="None"
export RP_PILOT_SANDBOX="/gpfs/alpine/bip115/scratch/hrlee/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000"
export RP_PILOT_STAGING="/gpfs/alpine/bip115/scratch/hrlee/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000/staging_area"
export RP_PROF="/gpfs/alpine/scratch/hrlee/bip115/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000/unit.000107//unit.000107.prof"

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
cd /gpfs/alpine/scratch/hrlee/bip115/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000/unit.000107/

# Pre-exec commands
prof cu_pre_start
module unload prrte ||  (echo "pre_exec failed"; false) || exit
module load spectrum-mpi ||  (echo "pre_exec failed"; false) || exit
module load fftw/3.3.8 ||  (echo "pre_exec failed"; false) || exit
export fpath=`grep -v "a" $RP_PILOT_STAGING/*_0_cc.dat|sort -k2 -n -r|head -n1|cut -d":" -f1` ||  (echo "pre_exec failed"; false) || exit
export fname=`basename $fpath` ||  (echo "pre_exec failed"; false) || exit
echo $fname ||  (echo "pre_exec failed"; false) || exit
echo $fpath ||  (echo "pre_exec failed"; false) || exit
replica_id=`echo $fname|cut -d_ -f1` ||  (echo "pre_exec failed"; false) || exit
iter_id=`echo $fname|cut -d_ -f2` ||  (echo "pre_exec failed"; false) || exit
echo $replica_id, $iter_id ||  (echo "pre_exec failed"; false) || exit
cp $RP_PILOT_STAGING/${replica_id}_${iter_id}_*restart.* . ||  (echo "pre_exec failed"; false) || exit
cp $fpath . ||  (echo "pre_exec failed"; false) || exit
sed -i -- "s/#####/set INPUTNAME ${replica_id}_${iter_id}_adk-step1\n\n#####/" adk-step1.namd ||  (echo "pre_exec failed"; false) || exit
prof cu_pre_stop

# The command to run
prof cu_exec_start
/opt/ibm/spectrum_mpi/jsm_pmix/bin/jsrun --erf_input /gpfs/alpine/scratch/hrlee/bip115/radical.pilot.sandbox/re.session.login5.hrlee.018617.0020/pilot.0000/unit.000107//unit.000107.rs   /gpfs/alpine/world-shared/bip115/NAMD_binaries/summit/NAMD_build.latest/Linux-POWER-MPI-smp-Summit/namd2 "+ppn" "4" "adk-step1.namd" 
RETVAL=$?
prof cu_exec_stop

# Exit the script with the return code from the command
prof cu_stop
exit $RETVAL
