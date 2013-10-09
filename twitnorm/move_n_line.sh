#!/bin/bash

function traverse {
    path=$1
    echo 'Traversing path: $path'
    for OUTPUT in $(ls $path);
do 
	echo "***********${path}/$OUTPUT*************";
	head  $path/$OUTPUT;
	echo '**********************'; 
done
}

function move_lines {
   filefrom=$1
   fileto=$2
   n=$3
   tmpfile=$(date +%s)
   head -n 2 $filefrom >> $fileto
   sed -e "1,${n}d" $filefrom > $tmpfile
   mv $tmpfile $filefrom
}

echo 'usage: . move_n_line.sh'
echo ''
echo 'move_lines fromfile tofile numberoflines'
echo 'move_lines ~/Datasets/snap/splited-07/tweets2009-07-splitedag ~/Datasets/snap/splited-07/tweets2009-07-splitedaf 3'
echo ''
echo 'traverse ~/Datasets/snap/splited-07/'
echo ''

#move_lines $1 $2 $3
#traverse $1

#head -n 6 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedag > from.txt
#tail -n 5 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedaf > to.txt
#move_lines from.txt to.txt 3