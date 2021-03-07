% Create a function at the beginning to manage paths
InFilePath = 'C:\Users\Herrick Fung\Desktop\jacky_pilot\Jacky_session_';
OutPPFilePath = 'C:\Users\Herrick Fung\Desktop\jacky_pilot\preprocessed\';
OutMergedPath = 'C:\Users\Herrick Fung\Desktop\jacky_pilot\mergedset.set';
OutSortedPath = 'C:\Users\Herrick Fung\Desktop\jacky_pilot\sorted\';
BehavioralPath = 'C:\Users\Herrick Fung\Desktop\jacky_pilot\behavioral\20210222130124_999_jjj_ep_experiment.csv';

% Main Function Runs here.
PREPROCESSALL(InFilePath, OutPPFilePath);
MERGEALL(OutPPFilePath, OutMergedPath);
SORTEPOCH(BehavioralPath, OutMergedPath, OutSortedPath);

disp('all done');
close all;
clear all;

function PREPROCESSALL(InFilePath, OutPPFilePath)
    for i = 1:6
        InFileName = append(InFilePath, num2str(i),'.raw');
        PreProed = PrePro(InFileName);
        OutFileName = append(OutPPFilePath, 'Session_', num2str(i), 'preprocessed.set');
        PreProed = pop_saveset(PreProed, 'filename', OutFileName);
        clear PreProed;
    end
end


function OutEEG = PrePro(InFileName)
    % reference:
    % https://sccn.ucsd.edu/wiki/Makoto's_preprocessing_pipeline#Remove_line_noise_using_CleanLine_.2804.2F25.2F2020_updated.29% Import data
    EEG = pop_readegi(InFileName);
    % Remove non-filterable artifacts (optional)
    % Downsample the data
    % our sampling rate is 250Hz, which is the frequency people usually downsample to, 
    % so i didn't downsample our data.

    % Bandpass-Filter
    % High-Pass filter at 0.1 Hz
    EEG = pop_eegfiltnew(EEG, 0.1, [], [], false, [], false);
    % Low-Pass filter at 40 Hz, [Not in pipeline]
    EEG = pop_eegfiltnew(EEG, [], 40, [], false, [], false);

    % Import Channel Info
    EEG = pop_chanedit(EEG, 'lookup','C:\\Users\\Herrick Fung\\Desktop\\jacky_pilot\\GSN-HydroCel-257.sfp',...
        'load',{'C:\\Users\\Herrick Fung\\Desktop\\jacky_pilot\\GSN-HydroCel-257.sfp',...
        'filetype','sfp'},'delete',257);

    % Remove bad channels with clean_rawdata()
    old_EEG = EEG;
    EEG = pop_clean_rawdata(EEG, 'FlatlineCriterion',5,'ChannelCriterion',0.8,...
        'LineNoiseCriterion',4,'Highpass','off','BurstCriterion','off',...
        'WindowCriterion','off','BurstRejection','off','Distance','Euclidian');

    % Interpolate removed channels from above
    EEG = pop_interp(EEG, old_EEG.chanlocs, 'spherical');
    clear old_EEG;

    % Rereferencing to the average
    EEG = pop_reref(EEG, []);

    % CleanLine to remove line noise
    EEG = pop_cleanline(EEG, 'LineFrequencies', [50 100 150 200 250]);

    % Low-Pass filter at 30 Hz, [Not in pipeline]
    % EEG = pop_eegfiltnew(EEG, [], 30, [], false, [], 1);
     
    % Epoch the data to an event onset
    EEG = pop_epoch(EEG, {'gabo'}, [-0.2    0.504], 'epochinfo', 'yes');
    EEG = pop_rmbase(EEG, [-200, 0]);
    EEG = pop_eegthresh(EEG,1,[1:126],-100,100,-0.2,0.5,1,0);

    % Run ICA
    % read this https://sccn.ucsd.edu/wiki/Chapter_09:_Decomposing_Data_Using_ICA#Independent_Component_Analysis_of_EEG_data
    EEG = pop_runica(EEG, 'icatype', 'runica', 'extended',1,'interrupt','on', 'stop', 1E-7);
    EEG = pop_iclabel(EEG, 'default');
    EEG = pop_icflag(EEG, [NaN NaN; 0.9 1; 0.9 1; NaN NaN;NaN NaN;NaN NaN;NaN NaN]);
    EEG = pop_subcomp(EEG, [], 0);

    OutEEG = EEG;
    clear EEG;
end


function MERGEALL(OutPPFilePath, OutMergedPath)
    for j = 1:5
        InFileName = append(OutPPFilePath, 'Session_', num2str(j), 'preprocessed.set');
        LoadFile = pop_loadset(InFileName);
        if j == 1
            MergedSet = LoadFile;
        else
            MergedSet = pop_mergeset(MergedSet, LoadFile, true);
        end
    end

    MergedSet = pop_saveset(MergedSet, 'filename', OutMergedPath);
    clear LoadFile MergedSet;
end


function SORTEPOCH(BehavioralPath, OutMergedPath, OutSortedPath)
    TrialList = readtable(BehavioralPath, 'Format', 'auto');
    
    trial_con = struct('single',[TrialList.Trial_No, TrialList.Condition == 1],...
                       'lowSD', [TrialList.Trial_No, TrialList.Condition == 2],...
                       'highSD', [TrialList.Trial_No, TrialList.Condition == 3]...
                       );
    
    fn = fieldnames(trial_con);
    
    for k = 1:numel(fn)
        trial_con.(fn{k}) = find(trial_con.(fn{k})(:,2)==1);
        trial_con.(fn{k}) = reshape(trial_con.(fn{k}), 1, 252);
    end
    
    FullEpochs = pop_loadset(OutMergedPath);
    SortedEpochs = struct('single_epochs', pop_selectevent(FullEpochs,'epoch',trial_con.single),...
                          'lowSD_epochs', pop_selectevent(FullEpochs,'epoch',trial_con.lowSD),...
                          'highSD_epochs', pop_selectevent(FullEpochs,'epoch',trial_con.highSD)...
                          );
    
    efn = fieldnames(SortedEpochs);
    
    for m = 1:numel(efn)
        OutFileName = append(OutSortedPath, efn{m}, '.set');
        SortedEpochs.(efn{m}) = pop_saveset(SortedEpochs.(efn{m}), 'filename', OutFileName);
    end
   
    clear FullEpochs SortedEpochs       
end
