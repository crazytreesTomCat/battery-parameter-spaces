#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 07:29:14 2018

@author: peter

NOTE: REQUIRES IMAGEMAGICK. https://www.imagemagick.org/script/download.php
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import operator
import glob

def animate(best_arm_params=[0,0]):
    plt.close('all')
    
    ##############################################################################

    # PARAMETERS TO CREATE POLICY SPACE
    C1list = [3.6, 4.0, 4.4, 4.8, 5.2, 5.6, 6, 8]
    C2list = [3.6, 4.0, 4.4, 4.8, 5.2, 5.6, 6, 7]
    C3list = [3.6, 4.0, 4.4, 4.8, 5.2, 5.6]

    C4_LIMITS = [0.1, 4.81] # Lower and upper limits specifying valid C4s
    FILENAME = 'hi'

    ############################################################################## 

    one_step = 4.8
    margin = 0.2 # plotting margin
    
    colormap = 'plasma_r' 
    
    # IMPORT RESULTS
    # Get folder path containing text files
    file_list = sorted(glob.glob('./pred/[0-9].csv'))
    data = []
    for file_path in file_list:
        data.append(np.genfromtxt(file_path, delimiter=','))
    
    # Find number of batches
    batchnum = len(data)
    
    # Min and max lifetime
    min_lifetime = np.min(data)
    max_lifetime = np.min(data)
    
    ## CREATE CONTOUR PLOT
    # SETTINGS
    
    ## CREATE CONTOUR PLOT
    # Calculate C4(CC1, CC2) values for contour lines
    C1_grid = np.arange(min(C1list)-margin,max(C1list) + margin,0.01)
    C2_grid = np.arange(min(C1list)-margin,max(C1list) + margin,0.01)
    [X,Y] = np.meshgrid(C1_grid,C2_grid)
    
    # Initialize plot
    fig = plt.figure() # x = C1, y = C2, cuts = C3, contours = C4
    plt.style.use('classic')
    plt.rcParams.update({'font.size': 16})
    plt.set_cmap(colormap)
    manager = plt.get_current_fig_manager() # Make full screen
    manager.window.showMaximized()
    minn, maxx = min_lifetime, max_lifetime
    
    ## MAKE PLOT
    for k, c3 in enumerate(C3list):
        plt.subplot(2,3,k+1)
        plt.axis('square')
        
        C4 = 0.2/(1/6 - (0.2/X + 0.2/Y + 0.2/c3))
        C4[np.where(C4<C4_LIMITS[0])]  = float('NaN')
        C4[np.where(C4>C4_LIMITS[1])] = float('NaN')
        
        ## PLOT CONTOURS
        levels = np.arange(2.5,4.8,0.25)
        C = plt.contour(X,Y,C4,levels,zorder=1,colors='k')
        plt.clabel(C,fmt='%1.1f')
        
        ## PLOT POLICIES
        idx_subset = np.where(policies[:,2]==c3)
        policy_subset = policies[idx_subset,:][0]
        lifetime_subset = lifetime[idx_subset,:]
        plt.scatter(policy_subset[:,0],policy_subset[:,1],vmin=minn,vmax=maxx,
                    c=lifetime_subset.ravel(),zorder=2,s=100)
        
        ## BASELINE
        if c3 == one_step:
            lifetime_onestep = sim(one_step, one_step, one_step,FILENAME,variance=False)
            plt.scatter(one_step,one_step,c=lifetime_onestep,vmin=minn,vmax=maxx,
                        marker='s',zorder=3,s=100)
        
        plt.title('C3=' + str(c3) + ': ' + str(len(policy_subset)) + ' policies',fontsize=16)
        plt.xlabel('C1')
        plt.ylabel('C2')
        plt.xlim((min(C1list)-margin, max(C1list)+margin))
        plt.ylim((min(C1list)-margin, max(C1list)+margin))
    
    plt.tight_layout()
    
    # Add colorbar
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    norm = matplotlib.colors.Normalize(minn, maxx)
    m = plt.cm.ScalarMappable(norm=norm, cmap=colormap)
    m.set_array([])
    cbar = fig.colorbar(m, cax=cbar_ax)
    #plt.clim(min(lifetime),max(lifetime))
    cbar.ax.set_title('Cycle life')
    
    # INITIALIZE SCATTER PLOT
    scatplot = plt.scatter([10,10],[10,10],c=[min_lifetime,max_lifetime], 
                          zorder=2,s=100,vmin=min_lifetime,vmax=max_lifetime) 
    
    # ANIMATION FUNCTION. This is called sequentially
    def animate(i):
        
        batch = data[i]
        scatplot.set_array(batch[:,5])
        scatplot.set_offsets(batch[:,0:1])
        plt.suptitle('Batch ' + str(i+1))
        return (scatplot,)
    
    # COLORBAR
    cbar = plt.colorbar()
    cbar.set_label('Cycle life')
    cbar.set_clim(min_lifetime,max_lifetime)
    
    
    """
    # ADD TEXT LABELS
    # LABEL FOR TRUE BEST ARM
    try:
        policies_lifetimes = np.genfromtxt('highgradient.csv', delimiter=',', skip_header=0)
        index, max_lifetime = max(enumerate(policies_lifetimes[:,2]), key=operator.itemgetter(1))
        plt.gcf().text(0.05, 0.9, "True best arm: (" + str(policies_lifetimes[index,0]) + ", " + \
               str(policies_lifetimes[index,1]) + ")", fontsize=14)
        plt.gcf().text(0.05, 0.85, " Lifetime=" + str(policies_lifetimes[index,2]),
                fontsize=14)
    except:
        pass
    
    # LABEL FOR ESTIMATED BEST ARM
    if best_arm_params[0]:
        plt.gcf().text(0.05, 0.7, "Estimated best arm: (" + str(best_arm_params[0]) + ", " + \
               str(best_arm_params[1]) + ")", fontsize=14)
    """
    
    ## SAVE ANIMATION
    anim = animation.FuncAnimation(fig, animate, frames=batchnum, 
                                   interval=1000, blit=False)
    
    anim.save('animation.gif', writer='imagemagick', fps=1)