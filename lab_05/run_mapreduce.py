#!/usr/bin/env python3
import subprocess
import os

def run_mapred(input_dir, output_file):
    mapper_script = "mapper.py"
    reducer_script = "reducer.py"
    temp_file = "temp_mapped.txt"
    
    # Map фаза
    with open(temp_file, 'w') as out:
        for filename in os.listdir(input_dir):
            with open(os.path.join(input_dir, filename), 'r') as f:
                subprocess.run(f"python {mapper_script}", stdin=f, stdout=out, shell=True)
    
    # Sort and Shuffle (встроено в unix sort)
    sorted_file = "temp_sorted.txt"
    subprocess.run(f"sort -k1,1 {temp_file} > {sorted_file}", shell=True)
    
    # Reduce фаза
    with open(output_file, 'w') as out:
        subprocess.run(f"python {reducer_script}", stdin=open(sorted_file, 'r'), stdout=out, shell=True)
    
    # Cleanup
    os.remove(temp_file)
    os.remove(sorted_file)
    print(f"Результат сохранён в {output_file}")

if __name__ == "__main__":
    run_mapred("input_data", "result.txt")
