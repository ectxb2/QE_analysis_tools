#this script analizes the packets from a LArPix h5 file
#it creates a histogram of the timestamps of data packets
#timestamps are ajusted to be relative to the ext trigger that comes after it 
#It also cops the amount of time scanned over
#Arg 1 is the file you want to use


import h5py
import sys
import numpy as np
import matplotlib.pyplot as plt

f = h5py.File(sys.argv[1])
pkts = f['packets']
mask7 = pkts['packet_type'] == 7 # this is ext. trig.
mask0 = pkts['packet_type'] == 0 # this is data packet?
pkts0 = pkts[mask0]
pkts7 = pkts[mask7]
print(len(pkts7))

timestamps0 = pkts0['timestamp']
timestamps7 = pkts7['timestamp']
#remove tail end of data that should have no laser pulses and begining that may mess with data
threshold = timestamps7[-1]
tailmask = timestamps0 < threshold
timestamps0 = timestamps0[tailmask]
threshold = timestamps7[0]
topmask = timestamps0 > threshold
timestamps0 = timestamps0[topmask]

delta_t7 = []
for t in timestamps7:
    dt = t - timestamps7[0]
    delta_t7 += [dt]

#shift times to line up and remove 40000 clock cycles after pulse (laser prpbably not there)
shifted_ts = []
shifted_ts7 = []
print(len(timestamps7))
for i in range(0,(len(timestamps7)-1)):
    mask1 = timestamps0 > (timestamps7[i]+300000) #500,000 CS between pulses
    timestampsnew = timestamps0[mask1]
    mask2 = timestampsnew < timestamps7[i+1]
    timestampsnew1 = timestampsnew[mask2]-(delta_t7[i]+timestamps7[0]+500000)
    #print(timestamps7[i])
    #print( 'delta_t7 = ' + str(delta_t7[i]))
    #print(len(timestampsnew1))
    shifted_ts = np.append(shifted_ts, timestampsnew1)
    newts7 = timestamps7[i+1]-delta_t7[i]-timestamps7[0]-500000
    shifted_ts7 = np.append(shifted_ts7,newts7)
    

print (len(shifted_ts7))
n, bins = np.histogram(shifted_ts, bins = 1000)
max_bin_time = bins[np.where(n == (max(n)))[0][0]]
plt.axvline(x = max_bin_time, color = 'r', label = 'Max Counts at '+str(max_bin_time))
plt.stairs(n, bins, label = 'Data')

#n7, bins = np.histogram(shifted_ts7, bins = bins)
n7, bins = np.histogram(shifted_ts7, bins = 10)
plt.stairs(n7, bins, label = 'Triggers')
#print(n7[-1])

plt.xlabel('Clock Cycles till next trigger, 100ns (10MHx)')
plt.ylabel('Summed Counts')
plt.legend()
plt.title('Time delay from Calibration Data to Trigger Signal Summed Data Counts')
current_values = plt.gca().get_xticks()
#plt.gca().set_xticklabels(['{:.0f}'.format(y) for y in current_values])
plt.show()

max_timestamps_2_trig = max_bin_time - bins[-1]
print('time delay is ' + str(max_timestamps_2_trig))

