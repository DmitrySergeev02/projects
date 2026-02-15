#!/bin/bash

START_SCENE=0
END_SCENE=199

echo "Starting batch generation of synthetic data..."

CURRENT_DIR=$(pwd)

for ((i=START_SCENE; i<=END_SCENE; i++))
do
   echo "--------------------------------------------------"
   echo "Processing Scene ID: $i"

   docker run --rm \
     --user $(id -u):$(id -g) \
     --volume "$CURRENT_DIR:/workspace" \
     --workdir "/workspace" \
     kubricdockerhub/kubruntu \
     /usr/bin/python3 generate_single_scene.py --scene_id $i

   if [ $? -ne 0 ]; then
       echo "ERROR: Failed to generate scene $i"
   else
       echo "SUCCESS: Scene $i generated."
   fi
   
   sleep 1
done

echo "Batch generation completed."