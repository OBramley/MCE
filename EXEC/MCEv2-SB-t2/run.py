#########################################################################################
#
#   Python Run script for Parallel Open MP execution of the MCE / CCS program
#   Written by O.A. Bramley                                     07/10/2020
#
#   This script is based of a similar script witted by C. Symonds using bash. This script
#   aims to simplify the running process and make the program more useable as python is
#   widely understood and should make modifications easier to implement.
#   The script is designed to compile, copy all reaquired files into an execution folder, 
#   and submit the program as a job. Included are various checks, output handling,  
#   parameter setting and module loading porcedures. This script  can also be used for 
#   for restarting a timed-out simulation by setting the restart paramter to 'YES'.
#   
#   To run the program variables must be set/checked in input.py, inham.py and prop.py.
#   The following arguemtns then have ot be set in the run folder
#       1) The number of repeats
#       2) The number of folders/nodes
#       3) The number of parallel cores per folder/node (max8)
#
#
#
#
#
#
#########################################################################################
import sys
import socket
import os
import subprocess
import getpass
import random
import shutil
import csv
import numpy as np
import inham
import inputs

#########################################################################################
#                              VARIABLES TO SET FOR SIMULATION                          #
#########################################################################################

# Number of repeats 
repeats=40
# Number of nodes/folders
nodes=1
#Number of parallel cores per folder/node (max 8)
cores=4
# Name of running folder 
# Default : <method>-<system>-<random number> ie CCS-HP-31254
# Otherwise:  <method>-<system>-<runfolder string>
Runfolder='t2'
# Generate Basis Set? YES/NO
gen='YES'
# Propagate Basis Set? YES/NO
prop='YES'
# Restart? YES/NO
# To restart a timedout run set to yes and rerun this script from the execution folder
restart='NO'
# Seed value for doing the random number routine- if you do not specify it 
# (leave default value of 0) will automatically generate one
SEED=0
#########################################################################################
#                                   END OF INPUTS                                       #
#########################################################################################
#                * NO NEED TO SCROLL FURTHER IF USING AS BLACKBOX *                     #
#########################################################################################

if(restart=="NO"):
    #Check basic arguements
    if(isinstance(repeats,int)==False):
        sys.exit("Number of repeats must be an integer")
    elif(isinstance(nodes,int)==False):
        sys.exit("Number of folders must be an integer")
    elif(isinstance(cores,int)==False):
        sys.exit("Number of parallel cores must be an integer")
    elif(repeats<1):
        sys.exit("Not enough runs selected. Must be 1 or greater")
    elif(nodes<1):
        sys.exit("Not enough nodes selected. Must be 1 or greater")
    elif(nodes>100):
        sys.exit("Too many nodes. Maximum of 100 simultaneous submisions")
    elif(cores>8):
        sys.exit("Too many cores selected. Maximum of 8 available")
    elif(cores<1):
        sys.exit("Not enough cores selected. Must be 1 or greater")
    elif((repeats/nodes)>5000):
        sys.exit("Too many repeats per folder. Must be less than 5000")
    elif((inputs.Conjugate_Repeats=='YES')and((repeats%(2*nodes*cores))!=0)):
        sys.exit("Number of repeats not valid for conjugate repetition. Should be integer multiple of 2*cores*nodes")
    elif((repeats%(nodes*cores))!=0):
        sys.exit("Number of repeats must be an integer multiple of cores*folders")
    elif(nodes*cores>100):
        sys.exit("Total number of cores should stay below 100")
    else:
        print("Arguments checked")    
        if(socket.gethostname()==("arc3"or"arc4")):
            HPCFLG=1
        else:
            HPCFLG=0
    
    #Might need grid altering calibration test for chlin451 bash code
    #if [[ -n $( echo $HOSTNAME | fgrep -e "chmlin451" ) ]]; then
    #grdalt=1
    #else
    #grdalt=0
    #fi

    #Makes execution folder and run folder
    if(HPCFLG==0):
        if not os.path.exists("../EXEC"):
            os.mkdir("../EXEC")
        EXDIR="../EXEC"
    else:
        subprocess.run(['module','load','mkl'])
        os.environ['LOGNAME']
        EXDIR="/nobackup/"+getpass.getuser()

    if(Runfolder=="Default"):
        Runfolder=inputs.method+"-"+inputs.systems["System"]+"-"+repeats+"-"+nodes+"-"+cores
    else:
        Runfolder=inputs.method+"-"+inputs.systems["System"]+"-"+Runfolder


    if os.path.exists(EXDIR+"/"+Runfolder):
        value=input("File already exists do you want to delete it? y/n\n")
        if(value=="y"):
            shutil.rmtree(EXDIR+"/"+Runfolder)
        else:
            sys.exit("Runfolder already exists. Change the Runfolder name or delte/move it")
    
    os.mkdir(EXDIR+"/"+Runfolder)
    
    EXDIR1=EXDIR+"/"+Runfolder  

    #Copies input files
    shutil.copy2("inham.py",EXDIR1)
    shutil.copy2("inputs.py",EXDIR1)
    shutil.copy2("run.py",EXDIR1)

    #Makes the program input file
    if(inputs.method=="MCE12"):
       for i in range(2):
            with open('rundata'+str(i+1)+'.csv','w',newline='')as file:
                writer = csv.writer(file)
                writer.writerow([gen,prop,restart,inputs.cmprss,('MCEv'+str(i+1)),int(repeats/nodes),inputs.Conjugate_Repeats])
                writer.writerow(inputs.systems.values())
                writer.writerow(inputs.parameters.values())
                writer.writerow(inputs.Train.values())
                writer.writerow(inputs.clone.values())
                writer.writerow(inputs.paramz.values())
                writer.writerow(inham.EL.values())
                writer.writerow(inputs.prop.values())
                if(inputs.systems['System']=='MP'):
                    writer.writerow(inham.MP.values())
                elif(inputs.systems['System']=='HP'):
                    writer.writerow(inham.HP.values())
                else:
                    writer.writerow(inham.SB.values())
            shutil.copy2('rundata'+str(i+1)+'.csv',EXDIR1)  
    else:
        with open('rundata.csv','w',newline='')as file:
            writer = csv.writer(file)
            writer.writerow([gen,prop,restart,inputs.cmprss,inputs.method,int(repeats/nodes),inputs.Conjugate_Repeats])
            writer.writerow(inputs.systems.values())
            writer.writerow(inputs.parameters.values())
            writer.writerow(inputs.Train.values())
            writer.writerow(inputs.clone.values())
            writer.writerow(inputs.paramz.values())
            writer.writerow(inham.EL.values())
            writer.writerow(inputs.prop.values())
            if(inputs.systems['System']=='MP'):
                writer.writerow(inham.MP.values())
            elif(inputs.systems['System']=='HP'):
                writer.writerow(inham.HP.values())
            else:
                writer.writerow(inham.SB.values())
        shutil.copy2("rundata.csv",EXDIR1)

    #Makes subfolders
    if(inputs.method=="MCE12"):
        os.mkdir(EXDIR1+"/MCEv1")
        os.mkdir(EXDIR1+"/MCEv2")
        for j in range(2):
            for i in range (nodes):
                os.mkdir(EXDIR1+"/MCEv"+str(j+1)+"/run-"+str(i+1))         
    else:
        for i in range(nodes):
            path=os.path.join(EXDIR1,"run-"+str(i+1))
            os.mkdir(EXDIR1+"/run-"+str(i+1))
           

    #Selects the right make file and executes
    os.chdir("../build")
    if(HPCFLG==1):
        shutil.copy2("../build/makefile_arc","../build/Makefile")
        subprocess.run(["make"])
    else:
        shutil.copy2("../build/makefile_chmlin","../build/Makefile")
        subprocess.run(["make"])
    shutil.copy2("MCE.exe",EXDIR1)

    os.chdir(EXDIR1)
    if(inputs.method=="MCE12"):
        for j in range(2):
            for i in range (nodes):
                shutil.copy2("MCE.exe","MCEv"+str(j+1)+"/run-"+str(i+1))
                shutil.copy2('rundata'+str(j+1)+'.csv',"MCEv"+str(j+1)+"/run-"+str(i+1)+"/rundata.csv")
    else:
        for i in range (nodes):
            shutil.copy2("MCE.exe","run-"+str(i+1))
            shutil.copy2("rundata.csv","run-"+str(i+1))
    
    #Need code for if freqflg==1 and no freq.dat to run ./integrator.exe

    #if(gen=='NO'): Write routine to copy basis functions

#elif(restart=='YES'): Write routine to change restart flag in csv file

#Code to run the job checking for SGE

#If on a SGE machine make job submission file


for i in range(nodes):
    os.chdir("run-"+str(i+1))
    subprocess.run(['ls'])
    if(cores!=1):
        #subprocess.run(['set','OMP_NUM_THREADS='+str(cores)])
        os.environ["OMP_NUM_THREADS"]=str(cores)
        subprocess.run(['./MCE.exe'])
    else:
        subprocess.call('/MCE.exe')
    os.chdir(EXDIR1)