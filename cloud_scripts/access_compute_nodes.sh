#!/bin/bash

declare -A clust_ip_addr

hosts_file=${HOME}/.hosts
base_dir=/pw/storage/mdtf
res=3445
nclusts=1

#if [ -f ${hosts_file}  ]; then
#	rm -rf ${hosts_file}
#fi

export HOSTALIASES=${hosts_file}

#create the cluster string for starting them

if [ "${res}"  == "3357" ]; then
	clust_str=pclust_m1
	for i in $(seq 2 ${nclusts})
	do
		clust_str=${clust_str},pclust_m${i}
	done
	echo "Cluster start string is ${clust_str}"
fi
if [ "${res}"  == "3445" ]; then
	clust_str=pcna_m1
	for i in $(seq 2 ${nclusts})
	do
		clust_str=${clust_str},pcna_m${i}
	done
	echo "Cluster start string is ${clust_str}"
fi


#start clusters and wait till they are ready

dirpath=${base_dir}/MDTF-diagnostics/cloud_scripts
echo "dirpath is ${dirpath}"

#status="No"
#while (test "${status}" != "Yes" )
#do
	if [ -f ${hosts_file} ]; then
		cat ${HOME}/.hosts
		status="Yes"
        echo "${status}"
	fi
	#sleep 10

#done

while read -r line
do
        str_array=($line)
        key=${str_array[0]}
        val=${str_array[1]}
        clust_ip_addr[$key]=$val
        #echo "IP address is $key $val  ${clust_ip_addr[$key]}"
done < "$hosts_file"

sleep 10

for i in $(seq 1 "${nclusts}")
do
	if [ $res == "3357" ];then
        	key=pclust_m${i}
	elif [ $res == "3445" ];then
        	key=pcna_m${i}
	fi
	ip_addr=${clust_ip_addr[$key]}
    echo "IP address of cluster $i is $ip_addr"
	ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  ${ip_addr}
    ./contrib/${USER}/mdtf/MDTF-diagnostics/cloud_scripts/run_mdtf_singularity_container.sh
done

exit 0