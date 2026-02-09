#!/bin/bash

# set variables
dir_type=$1
search_dir=${2:-.}
all_struc=("VASP_inputs" "*_Removed" "*_Added")
# Ensure vasp.sh exists in the head directory
if [[ ! -f "$search_dir/vasp.sh" ]]; then
    echo "Error: vasp.sh not found in $search_dir"
    exit 1
fi
    
submit() {
    # Find all directories named "VASP_inputs" and copy vasp.sh into them
    find "$search_dir" -type d -name "$1" | while read -r dir; do
        echo "Copying vasp.sh to $dir"
        cp "$search_dir/vasp.sh" "$dir/"
    done

    # Find all vasp.sh files in VASP_inputs directories and submit them
    find "$search_dir" -type f -name "vasp.sh" -path "*/$1/*" | while read -r file; do
        job_dir=$(dirname "$file")
        echo "Submitting sbatch in directory: $job_dir"
        (cd "$job_dir" && sbatch vasp.sh)
    done
    
    echo "All jobs submitted."
}

if [[ "$dir_type" = "all" ]]; then
    for struc in "${all_struc[@]}"; do
        submit "$struc"
    done
else
    submit "$dir_type"
fi 

