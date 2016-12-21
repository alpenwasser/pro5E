#!/usr/bin/env bash

declare -a filelist
while IFS= read -r -d '' element;do
	filelist+=( "$element" )
done < <( find "$(pwd)/../../measurements--"*"/data" -type f -print0 )

for file in "${filelist[@]}";do
	targetName="${file#${PWD}/}"
	targetName="../../${targetName}"
	linkName="${targetName##*/}"
	linkDir="${targetName%/*}"
	linkDir="${linkDir#../../../../measurements--}"
	linkDir="${linkDir/\/data\///}"
	linkPath="${linkDir}/${linkName/txt/dat}"

	mkdir -p "$linkDir"
	ln -s "$targetName" "$linkPath"
done
