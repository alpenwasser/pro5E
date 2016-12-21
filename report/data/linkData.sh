#!/usr/bin/env bash

# Preamp -------------------------------------------------------------------- #
declare -a filelist
while IFS= read -r -d '' element;do
	filelist+=( "$element" )
done < <( find "$(pwd)/../../measurements--preamp/data" -type f -print0 )

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
unset filelist

# SigDel -------------------------------------------------------------------- #
declare -a filelist
while IFS= read -r -d '' element;do
	filelist+=( "$element" )
done < <( find "$(pwd)/../../measurements--sigdel/data-processed" -type f -print0 )

for file in "${filelist[@]}";do
	targetName="${file#${PWD}/}"
	targetName="../../${targetName}"
	linkName="${targetName##*/}"
	linkDir="${targetName%/*}"
	linkDir="${linkDir#../../../../measurements--}"
	linkDir="${linkDir/\/data-processed\///}"
	linkPath="${linkDir}/${linkName/txt/dat}"

	mkdir -p "$linkDir"
	ln -s "$targetName" "$linkPath"
done
unset filelist

# Both ---------------------------------------------------------------------- #
declare -a filelist
while IFS= read -r -d '' element;do
	filelist+=( "$element" )
done < <( find "$(pwd)/../../measurements--both/data-processed" -type f -print0 )

for file in "${filelist[@]}";do
	targetName="${file#${PWD}/}"
	targetName="../../${targetName}"
	linkName="${targetName##*/}"
	linkDir="${targetName%/*}"
	linkDir="${linkDir#../../../../measurements--}"
	linkDir="${linkDir/\/data-processed\///}"
	linkPath="${linkDir}/${linkName/txt/dat}"

	mkdir -p "$linkDir"
	ln -s "$targetName" "$linkPath"
done
unset filelist
