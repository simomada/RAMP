# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 14:35:00 2019
This is the code for the open-source stochastic model for the generation of 
multi-energy load profiles in off-grid areas, called RAMP, v.0.2.1-pre.

@authors:
- Francesco Lombardi, Politecnico di Milano
- Sergio Balderrama, Université de Liège
- Sylvain Quoilin, KU Leuven
- Emanuela Colombo, Politecnico di Milano

Copyright 2019 RAMP, contributors listed above.
Licensed under the European Union Public Licence (EUPL), Version 1.1;
you may not use this file except in compliance with the License.

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.
"""

#%% Import required modules
import pandas as pd
import os
import shutil

if os.path.isdir('Inputs'):
    shutil.rmtree('Inputs')
os.makedirs('Inputs')

if os.path.isdir('Outputs'):
    shutil.rmtree('Outputs')
os.makedirs('Outputs')

Users = pd.read_excel('Inputs.xlsx', sheet_name='Users')
Assets = pd.read_excel('Inputs.xlsx', sheet_name='Appliances')

Regions = Users.columns
User= Users.index
Apps = Assets.Apps

for R in Regions:
    f=open('Inputs/' + R + ".py","w+")
    f.write('from core import User, np\n\n\nUser_list = []\n\n')
    
    for U in User:
        
        f.write('%s' %U + ' = User("%s' %U + '", n_users = %i'  %Users[R][U] + ')\nUser_list.append(%s' %U + ')\n\n')
        S=pd.read_excel('Inputs.xlsx', sheet_name='%s' %U ,header=0)

        for A in Apps:
            
 
            if S[A].n is not 0:
               
                f.write("%s" %U + "_%s" %A +" = %s" %U +".Appliance(%s" %U + ",%i" %S[A].n + ",%i" %S[A].P + ",%i" %S[A].w + ",%i" %S[A].t + ",%.2f" %S[A].r_t + ",%i" %S[A].c + ",fixed='%s" %S[A].fixed + "',fixed_cycle=%i" %S[A].fixed_cycle + ",occasional_use=%.2f" %S[A].occasional_use + ",thermal_P_var=%.2f" %S[A].thermal_P_var + ",flat='%s" %S[A].flat + "')\n")
                f.write('%s' %U +'_%s' %A + '.windows(')
                for w in range(0,S[A].w):
                    if w is 0:
                        f.write('[%i' %S[A].start_w1 + ',%i]'  %S[A].end_w1)
                    if w is 1:
                        f.write(',[%i' %S[A].start_w2 + ',%i]'  %S[A].end_w2)
                    if w is 2:
                        f.write(',[%i' %S[A].start_w3 + ',%i]'  %S[A].end_w3)
                
                if S[A].fixed_cycle is 0: f.write(',%.2f' %S[A].r_w)
                f.write(')\n')
                
                if S[A].fixed_cycle is not 0:
                    for fc in range(0,S[A].fixed_cycle):
                        if fc is 0:
                            f.write('%s' %U + '_%s' %A + '.specific_cycle_1(%i' %S[A].P_11 + ',%i' %S[A].t_11 + ',%i' %S[A].P_12 + ',%i' %S[A].t_12 + ')\n')
                        if fc is 1:
                            f.write('%s' %U + '_%s' %A + '.specific_cycle_2(%i' %S[A].P_21 + ',%i' %S[A].t_21 + ',%i' %S[A].P_22 + ',%i' %S[A].t_22 + ')\n')
                        if fc is 2:
                            f.write('%s' %U + '_%s' %A + '.specific_cycle_3(%i' %S[A].P_31 + ',%i' %S[A].t_31 + ',%i' %S[A].P_32 + ',%i' %S[A].t_32 + ')\n')
                            
                    f.write('%s' %U + '_%s' %A + '.cycle_behaviour(')
                    
                    for fc in range(0,S[A].fixed_cycle):
                        if fc is 0:
                            f.write('[%i' %S[A].start_cw11 + ',%i'  %S[A].end_cw11 + '],[%i' %S[A].start_cw12 + ',%i' %S[A].end_cw12 + ']' )
                        if fc is 1:
                            f.write(',[%i' %S[A].start_cw21 + ',%i'  %S[A].end_cw21 + '],[%i' %S[A].start_cw22 + ',%i' %S[A].end_cw22 + ']')
                        if fc is 2:
                            f.write(',[%i' %S[A].start_cw31 + ',%i'  %S[A].end_cw31 + '],[%i' %S[A].start_cw32 + ',%i' %S[A].end_cw32 + ']')
                    f.write(')\n')

                f.write('\n\n')
        f.write('\n\n')
    f.close()
    
    
from stochastic_process import Stochastic_Process
from post_process import*

# Calls the stochastic process and saves the result in a list of stochastic profiles
# By default, the process runs for only 1 input file ("input_file_1"), but multiple files
# can be run in sequence enlarging the iteration range and naming further input files with
# progressive numbering
num_profiles = int(input("please indicate the number of profiles to be generated: ")) #asks the user how many profiles (i.e. code runs) he wants
print('Please wait...') 
length = num_profiles*1440
All_Profiles=pd.DataFrame(0,index=range(length), columns=Regions, dtype=float)

for j in range(0,len(Regions)):
    R=Regions[j]
    shutil.copyfile('Inputs/' + R + ".py", 'input_file_%d.py' %j)
    Profiles_list = Stochastic_Process(j,num_profiles)

# Post-processes the results and generates plots
    Profiles_avg, Profiles_list_kW, Profiles_series = Profile_formatting(Profiles_list)
    Profile_series_plot(Profiles_series)
    os.remove('input_file_%d.py' %j)
    np.save('Outputs/profile_%s.npy' %R, Profiles_series)
    All_Profiles[R] = Profiles_series

All_Profiles.to_csv('Outputs/All_prof.csv')