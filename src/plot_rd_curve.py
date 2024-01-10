#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import subprocess
import matplotlib.pyplot as plt

class PlotRDCurve:
    def __init__(self, bitrates = list(range(100, 1300, 100))):
        self.bitrates = bitrates
        self.imps = {   0: 'BR_control_no.py',
                        1: 'BR_control_add_lost.py',
                        2: 'BR_control_lost.py',
                        3: 'BR_control_conservative.py'}
        self.imp_rmses = []
    
    def plot(self):
        for imp_no in range(0, 4):
            rmse_arr = []
            for br in self.bitrates:
                self.simulate_link(br)
                rmse = subprocess.run(['python', '-O', 'RMSE_chunks.py', '-f', 'nuclear.wav', '-z', str(imp_no)], stdout=subprocess.PIPE).stdout
                print(rmse)
                rmse = float(rmse.decode('utf-8').rstrip())
                rmse_arr.append(rmse)
                self.delete_sim_rule(br)
            self.imp_rmses.append(rmse_arr)
        
            plt.plot(self.bitrates, rmse_arr, marker='o')
            plt.xlabel('Bitrate (kbps)')
            plt.ylabel('RMSE')
            plt.title('R/D curve for ' + self.imps[imp_no])
            plt.savefig(self.imps[imp_no]+'.png')
            plt.clf()
    
    def simulate_link(self, bitrate):
        subprocess.run(['tc', 'qdisc', 'add', 'dev', 'lo', 'root', 'handle', '1:', 'tbf', 'rate', str(bitrate)+'kbit', 'burst', '32kbit', 'limit', '32kbit'])
        #subprocess.run(['tc', 'qdisc', 'add', 'dev', 'lo', 'parent', '1:1', 'handle', '10:', 'netem', 'delay', '100ms', '10ms', '25%', 'distribution', 'normal'])
    
    def delete_sim_rule(self, bitrate):
        #for bitrate in self.bitrates:
            #subprocess.run(['tc', 'qdisc', 'delete', 'dev', 'lo', 'parent', '1:1', 'handle', '10:', 'netem', 'delay', '100ms', '10ms', '25%', 'distribution', 'normal'])
        subprocess.run(['tc', 'qdisc', 'delete', 'dev', 'lo', 'root', 'handle', '1:', 'tbf', 'rate', str(bitrate)+'kbit', 'burst', '32kbit', 'limit', '32kbit'])

if __name__ == "__main__":
    plotter = PlotRDCurve()
    plotter.plot()