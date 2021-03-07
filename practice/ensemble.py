'''
Practice trial for the pure ensemble block.
Include both low and high sd.
contain 28 trials
'''

# import libraries
from datetime import datetime
from psychopy import visual, event, monitors, core, logging
import math
import numpy as np
import os
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

# declare timing variables
fixation_time = 0.5
gaborset_time = 0.5
blankscreen_time = 0.4
feedback_screen_time = 1
isi_time = 0.5

# declare variables for trial generations
No_of_Trials = 28
orientations = [0,10,-10,20,-20,30,-30]
sds = [8, 32]
reps = 2

# generate the trial list and randomly shuffle
triallist = []
for i in range(reps):
    for orientation in orientations:
        for sd in sds:
            trial = [orientation, sd]
            triallist.append(trial)
            np.random.shuffle(triallist)

# clear command output and start logging
os.system('cls' if os.name == 'ht' else 'clear')
logging.console.setLevel(logging.CRITICAL)
print("**************************************")
print("PRACTICE TRIAL - NO SAVE")
print("PSYCHOPY LOGGING set to : CRITICAL")
print(datetime.now())
print("**************************************")

# calibrating monitor and creating window for experiment
mon = monitors.Monitor(monitor_name)
mon.setWidth(screen_width)
mon.setDistance(view_distance)
win = visual.Window(size=screen_resolution, color='#C0C0C0',
                    fullscr=True, monitor=mon, allowGUI = True
                    )


def instruction():
    #  creating the instruction text to shown at the beginning
    instruct_text = \
        "\
ENSEMBLE - PRACTICE TRIAL: NO SAVE\n\n\
Instructions: \n\
This experiment is about judging the orientation. On each trial, \
A black fixation cross will appear, followed by a flash of 9 orientation patches. \
You are required to judge the Average of all orientation patches when the red fixation cross appear. \
After response, A green circle will appear if the response was correct, \
otherwise, A red circle will appear if the response was wrong.\n\n\
Press 'f' to indicate an anti-clockwise tilt & \n\
Press 'j' to indicate a clockwise tilt. \n\n\
Press Spacebar to start the practice trial. \n\
Press 'End' if you want to Terminate anytime.\
"
    instruct = visual.TextStim(win = win, text = ' ', font = 'Times New Roman',
                               pos = (0,0), color = 'black', units = 'deg',
                               height = 0.5, wrapWidth=26
                               )
    instruct.setText(instruct_text)
    instruct.draw()
    win.flip()
    instructresp = event.waitKeys(maxWait=1000, keyList=['end','space'],
                                  clearEvents=True
                                  )
    if 'space' in instructresp:
        pass
    elif 'end' in instructresp:
        win.close()
        sys.exit()


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
    # https://stackoverflow.com/questions/51515423/generate-sample-data-with-an-exact-mean-and-standard-deviation
    # Generate 9 gabors random in normal distrubution and normalize to mean, sd
    samples = stats.truncnorm.rvs((-30-0)/ori_std, (30-0)/ori_std, loc=0, scale=ori_std, size=9)
    samples_mean = np.mean(samples)
    samples_std = np.std(samples)
    array = (samples - samples_mean) * (ori_std/samples_std) + ori

    if any(item > 88 for item in array) or any (item < -88 for item in array):
        return generate_ori_array(ori, ori_std)
    else:
        return array


def gabor(orientation, sd):
    grating = visual.GratingStim(win = win, units= 'deg',tex='sin',
                                 mask='gauss', ori=0, pos=(0, 0),
                                 size=(1.6,1.6), sf=3, opacity = 1,
                                 blendmode='avg', texRes=128,
                                 interpolate=True, depth=0.0
                                 )
    # Construction of the Position of Gabors and randomly shuffle it.
    pos_array = [1,2,3,4,5,6,7,8,9]
    np.random.shuffle(pos_array)

    # Generate 9 gabors random in normal distribution
    ori_array = generate_ori_array(orientation, sd)
    np.random.shuffle(ori_array)

    for z in range(9):
        grating.pos=pos_to_coordinate(pos_array[z])
        grating.setOri(ori_array[z])
        grating.draw()


def feedback(orientation, resp):
    # Create Feedback for Practice Trial and draw to memory
    '''
    Draw a green circle for correct, red for wrong
    if 0 in ori: always correct
    '''
    correct_fb = visual.Circle(win=win, units = 'deg', pos=(0,0), radius=3.5,
                               edges=1000, fillColor='#ADFF2F',
                               lineColor='#ADFF2F',
                               lineWidth=line_width_in_pixel,
                               opacity=1)
    wrong_fb = visual.Circle(win=win, units = 'deg', pos=(0,0), radius=3.5,
                             edges=1000, fillColor='#FF0000',
                             lineColor='#FF0000',
                             lineWidth=line_width_in_pixel,
                             opacity=1)

    if 'f' in resp:
        resp_bin = 0
    else:
        resp_bin = 1

    if orientation == 0:
        answer = resp_bin
    elif orientation < 0:
        answer = 0
    else:
        answer = 1

    if resp_bin == answer:
        correct_fb.draw()
    else:
        wrong_fb.draw()


def debriefing():
    #  Debriefing Note
    debrief_text = \
        "\
End of this Practice.\
"

    debrief = visual.TextStim(win = win, text = ' ', font = 'Times New Roman',
                              pos = (0,0), color = 'black', units = 'deg',
                              height = 0.5, wrapWidth=20
                              )
    debrief.setText(debrief_text)
    debrief.draw()
    win.flip()
    core.wait(3)


def main():
    instruction()
    for i in range(No_of_Trials):
        black_fixation()
        win.flip()
        core.wait(fixation_time)
        gabor(triallist[i][0], triallist[i][1])
        win.flip()
        core.wait(gaborset_time)
        win.flip()
        core.wait(blankscreen_time)
        red_fixation()
        win.flip()

        resp = event.waitKeys(maxWait=1000, keyList=['end','f', 'j'],
                              clearEvents=True)
        if 'end' in resp:
            win.close()
            sys.exit()

        elif any(keylist in resp for keylist in ("f", "j")):
            # Feedback Screen
            feedback(triallist[i][0], resp)
            win.flip()
            core.wait(feedback_screen_time)
            # ISI
            win.flip()
            core.wait(isi_time)
    debriefing()


if __name__ == '__main__':
    main()
