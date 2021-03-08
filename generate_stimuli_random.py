'''
Generate stimuli for all participants
directory:
/experiment/data/ - contain all partis data and backup file
create folder for all parti in /experiment/parti_no + parti_name
within parti folder, paste the eprime file within
psychopy will generate images folder, images/fixation and images/stimuli
'''

# import libraries
from datetime import datetime
from psychopy import visual, event, monitors, core, logging, gui
import numpy as np
import math
import os
import pandas as pd
import scipy.stats as stats
import sys

# Setting for the Dell G7 Monitor
monitor_name = 'RLG307'
view_distance = 60
screen_width = 34.5
screen_resolution = [1920,1080]
line_width_in_pixel = 7

# Setting for Home Monitor
# monitor_name = 'testMonitor'
# view_distance = 60
# screen_width = 31
# screen_resolution = [1920, 1080]
# line_width_in_pixel = 7

# clear command output and start logging
os.system('cls' if os.name == 'ht' else 'clear')
logging.console.setLevel(logging.CRITICAL)
print("**************************************")
print("SINGLE-ENSEMBLE ERP EXPERIMENT - STIMULI GENERATION")
print("PSYCHOPY LOGGING set to : CRITICAL")
print(datetime.now())
print("**************************************")

# get current date and time
current_date = datetime.now().strftime("%Y%m%d")
current_time = datetime.now().strftime("%H%M%S")

# get observer's information
info = gui.Dlg(title="Ensemble Perception Experiment", pos = [600,300],
               labelButtonOK="READY", labelButtonCancel=" ")
info.addText("Observer's Info. ")
info.addField('Experiment Date (YMD): ', current_date)
info.addField('Experiment Time (HMS): ', current_time)
info.addField('Participant No.:')
# info.addField('Block Sequence:', choices = ['Single-Ensemble', 'Ensemble-Single'])
info.addField('Name: ')
info.addField('Age: ')
info.addField('Gender:', choices = ['Male', 'Female'])
info.addField('Dominant Hand: ', choices=['Right', 'Left'])
show_info = info.show()
parti_no = show_info[2]
# sequence = show_info[3]
parti_name = show_info[3]

# Create a data director, check info. and create save file name
try:
    os.mkdir('experiment/' + parti_no + '_' + parti_name)
    os.mkdir('experiment/' + parti_no + '_' + parti_name + '/images')
    os.mkdir('experiment/' + parti_no + '_' + parti_name + '/images/fixation')
    os.mkdir('experiment/' + parti_no + '_' + parti_name + '/images/stimuli')
    print("Directory Created!")
except FileExistsError:
    print("Directory Exist!")

if info.OK:
    save_file_name = 'experiment/data/' + show_info[0] + show_info[1] + '_' + \
        parti_no + '_' + parti_name + '_ep_experiment.csv'
    save_file_name_backup = 'experiment/data/' + show_info[0] + show_info[1] + '_' + \
        parti_no + '_' + parti_name + '_backup_orientation.csv'
else:
    print("User Cancelled")

# Create save path and backup file
save_path = gui.fileSaveDlg(initFileName=save_file_name,
                            prompt='Select Save File'
                            )
backup_file = open(save_file_name_backup, 'w')

# declare variables for trial generations
No_of_Trials = 756
conditions = [1,2,3]
orientations = [0,10,-10,20,-20,30,-30]
# ori_stds = [8, 32]
reps = 36

# generate the triallist and randomly shuffle
# single_triallist = []
# ensemble_triallist = []
triallist = []

# for i in range(reps):
#     for orientation in orientations:
#         trial = [1, orientation, None]
#         single_triallist.append(trial)
#         np.random.shuffle(single_triallist)

# for i in range(reps):
#     for orientation in orientations:
#         for ori_std in ori_stds:
#             trial = [2, orientation, ori_std]
#             ensemble_triallist.append(trial)
            # np.random.shuffle(ensemble_triallist)


for i in range(reps):
    for condition in conditions:
        for orientation in orientations:
            trial = [condition, orientation]
            triallist.append(trial)

np.random.shuffle(triallist)


# if sequence == "Single-Ensemble":
#     triallist = single_triallist[:126] + \
#                 ensemble_triallist + \
#                 single_triallist[126:]
# else:
#     triallist = ensemble_triallist[:252] + \
#                 single_triallist + \
#                 ensemble_triallist[252:]

# # generate blank arrays for the output data file
date_array = []
time_array = []
parti_no_array = []
# sequence_array = []
name_array = []
age_array = []
gender_array = []
hand_array = []
trial_no_array = []
condition_array = []
orientation_array = []
# orientation_std_array = []

# calibrating monitor and creating window for experiment
mon = monitors.Monitor(monitor_name)
mon.setWidth(screen_width)
mon.setDistance(view_distance)
win = visual.Window(size=screen_resolution, color='#C0C0C0',
                    fullscr=True, monitor=mon, allowGUI = True
                    )


def black_fixation():
    # creating and drawing fixation cross to memeory
    fix_hori = visual.Rect(win = win, width=0.9, height=0.1, units='deg',
                           lineColor='black', fillColor='black', pos=(0,0)
                           )
    fix_vert = visual.Rect(win = win, width=0.1, height=0.9, units='deg',
                           lineColor='black', fillColor='black', pos=(0,0)
                           )
    fix_hori.draw()
    fix_vert.draw()


def red_fixation():
    # creating and drawing fixation cross to memeory
    fix_hori = visual.Rect(win = win, width=0.9, height=0.1, units='deg',
                           lineColor='red', fillColor='red', pos=(0,0)
                           )
    fix_vert = visual.Rect(win = win, width=0.1, height=0.9, units='deg',
                           lineColor='red', fillColor='red', pos=(0,0)
                           )
    fix_hori.draw()
    fix_vert.draw()


def pos_to_coordinate(position):
    '''
    Dictionary to convert position code to coordinates,
    Position Code Refer below
    (1,2,3)
    (4,5,6)
    (7,8,9)
    '''

    return {1: (2.0*math.cos(math.radians(0)), 2.0*math.sin(math.radians(0))),
            2: (2.0*math.cos(math.radians(40)), 2.0*math.sin(math.radians(40))),
            3: (2.0*math.cos(math.radians(80)), 2.0*math.sin(math.radians(80))),
            4: (2.0*math.cos(math.radians(120)), 2.0*math.sin(math.radians(120))),
            5: (2.0*math.cos(math.radians(160)), 2.0*math.sin(math.radians(160))),
            6: (2.0*math.cos(math.radians(200)), 2.0*math.sin(math.radians(200))),
            7: (2.0*math.cos(math.radians(240)), 2.0*math.sin(math.radians(240))),
            8: (2.0*math.cos(math.radians(280)), 2.0*math.sin(math.radians(280))),
            9: (2.0*math.cos(math.radians(320)), 2.0*math.sin(math.radians(320)))}.get(position)


def generate_ori_array(ori, ori_std):
    # Generate 9 gabors random in normal distrubution and normalize to mean, sd
    samples = stats.truncnorm.rvs((-30-0)/ori_std, (30-0)/ori_std, loc=0, scale=ori_std, size=9)
    samples_mean = np.mean(samples)
    samples_std = np.std(samples)
    array = (samples - samples_mean) * (ori_std/samples_std) + ori

    if any(item > 88 for item in array) or any (item < -88 for item in array):
        return generate_ori_array(ori, ori_std)
    else:
        return array


def gabor(con, ori):
    grating = visual.GratingStim(win = win, units= 'deg',tex='sin',
                                 mask='gauss', ori=0, pos=(0, 0),
                                 size=(1.6,1.6), sf=3, opacity = 1,
                                 blendmode='avg', texRes=128,
                                 interpolate=True, depth=0.0
                                 )
    if con == 1:
        grating.setOri(ori)
        grating.draw()
    else:
        # construct position array and shuffle it.
        if con == 2:
            ori_std = 8
        else:
            ori_std = 32

        pos_array = [1,2,3,4,5,6,7,8,9]
        np.random.shuffle(pos_array)
        ori_array = generate_ori_array(ori, ori_std)
        np.random.shuffle(ori_array)

        # ori_backup_file
        ori_array_list_to_string = ','.join([str(element) for element in ori_array])
        backup_file.write(ori_array_list_to_string)
        backup_file.write("\n")

        for z in range(9):
            grating.pos=pos_to_coordinate(pos_array[z])
            grating.setOri(ori_array[z])
            grating.draw()


def main():
    # fixation screen
    black_fixation()
    win.flip()
    win.getMovieFrame(buffer='front')
    win.saveMovieFrames('experiment/' + parti_no + '_' + parti_name + '/images/fixation/black_fixation.png')
    red_fixation()
    win.flip()
    win.getMovieFrame(buffer='front')
    win.saveMovieFrames('experiment/' + parti_no + '_' + parti_name + '/images/fixation/red_fixation.png')

    for i in range(No_of_Trials):
        date_array.append(show_info[0])
        time_array.append(show_info[1])
        parti_no_array.append(parti_no)
        # sequence_array.append(sequence)
        name_array.append(parti_name)
        age_array.append(show_info[4])
        gender_array.append(show_info[5])
        hand_array.append(show_info[6])
        trial_no_array.append(i + 1)
        condition_array.append(triallist[i][0])
        orientation_array.append(triallist[i][1])
        # orientation_std_array.append(triallist[i][2])

        # stimuli screen
        gabor(triallist[i][0], triallist[i][1])
        win.flip()
        win.getMovieFrame(buffer='front')
        win.saveMovieFrames('experiment/' + parti_no + '_' + parti_name + f'/images/stimuli/stimuli{i+1}.png')
        if event.getKeys() == ['end']:
            break

    outputfile = pd.DataFrame({'Exp_Date': date_array,
                               'Exp_Time': time_array,
                               'Parti_No': parti_no_array,
                               # 'Sequence': sequence_array,
                               'Parti_Name': name_array,
                               'Age': age_array,
                               'Gender': gender_array,
                               'Dominant_Hand': hand_array,
                               'Trial_No': trial_no_array,
                               'Condition': condition_array,
                               'Orientation': orientation_array,
                               # 'Std_Orientation': orientation_std_array,
                            })

    outputfile.to_csv(save_path, sep=',', index=False)


if __name__ == '__main__':
    main()
