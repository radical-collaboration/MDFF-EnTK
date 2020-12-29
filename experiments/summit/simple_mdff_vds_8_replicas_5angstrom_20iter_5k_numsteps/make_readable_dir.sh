#!/bin/bash

iter_cnt=0
base_path="readable"
for unit in `ls -d unit*`
do
	rp_unit_name=`grep RP_UNIT_NAME $unit/unit*.sh|cut -d= -f2|tr -d '"'`
	pipe_name=`echo "$rp_unit_name"|cut -d, -f6`
	stage_name=`echo "$rp_unit_name"|cut -d, -f4|tr ' ' '_'`
	mkdir -p $base_path/$pipe_name
	new_dir="$base_path/$pipe_name/$iter_cnt.$stage_name"
	if [ -d "$new_dir" ]
	then
		iter_cnt=`expr $iter_cnt + 1`
	fi
	new_dir="$base_path/$pipe_name/$iter_cnt.$stage_name"

	cp -pr $unit $new_dir
	echo cp -pr $unit $new_dir
done
