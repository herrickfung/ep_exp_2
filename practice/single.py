'''
Practice trial for the pure single block.
contain 14 trials
'''

# import libraries
from datetime import datetime
import numpy as np
import os
from psychopy import visual, event, monitors, core, logging
import sys

# Setting for the Dell G7 Monitor
monitor_name = 'RLG307'
view_distance = 60
screen_width = 34.5
screen_resolution = [1920,1080]
line_width_in_pixel = 7

# declare timing variables
fixation_time = 0.5
gaborset_time = 0.2
blankscreen_time = 0.5
feedback_screen_time = 1
isi_time = 0.5

# declare variables for trial generations
No_of_Trials = 14
reps = 2
orientations = [0,10,-10,20,-20,30,-30]

# generate the trial list and randomly shuffle
triallist = []
for i in range(reps):
    for orientation in orientations:
        trial = [orientation]
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
SINGLE - PRACTICE TRIAL: NO SAVE\n\n\
Instructions: \n\
This experiment is about judging the orientation. On each trial, \
A black fixation cross will appear, followed by a flash of orientation patch. \
You are required to judge the orientation when the red fixation cross appear. \
After response, A green circle will appear if the response was correct, \
otherwise, A red circle will appear if the response was wrong. \n\n\
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


def gabor(orientation):
    grating = visual.GratingStim(win = win, units= 'deg',tex='sin',
                                 mask='gauss', ori=orientation, pos=(0, 0),
                                 size=(1.6,1.6), sf=3, opacity = 1,
                                 blendmode='avg', texRes=128,
                                 interpolate=True, depth=0.0
                                 )
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
        gabor(triallist[i][0])
        win.flip()
        core.wait(gaborset_time)
        black_fixation()
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
