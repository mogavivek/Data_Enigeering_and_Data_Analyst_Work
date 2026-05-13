from function import *
import time
import datatime


print("Starting data pipeline at", datatime.datatime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("------------------------------------------")

# Step - 1: Extract video IDs
t0 = time.time()
getVideoIDs()
t1 = time.time()
print("Step 1: Done")
print("----> Video IDs download in", str(t1-t0), "seconds", "\n")

# Step - 2: Extract transcripts from videos
t0 = time.time()
getVideoTranscripts()
t1 = time.time()
print("Step 2: Done")
print("----> Trasnscripts download in", str(t1-t0), "seconds", "\n")

# Step - 1: Transform Data
t0 = time.time()
transformData()
t1 = time.time()
print("Step 3: Done")
print("----> Data transform in", str(t1-t0), "seconds", "\n")