% Main Function Runs here.
cd 'C:\Program Files\Polyspace\R2020a\toolbox\eeglab_current\eeglab2021.0';
eeglab;
cd 'C:\Users\Herrick Fung\Desktop\Course Materials\Sem 4.1\PSY402 Research Thesis II\experiment_part2\result';

% Create Core Paths
CurrentPath = pwd;
RawPath = fullfile(CurrentPath, 'raw');
PreProcessedPath = fullfile(CurrentPath, 'preprocessed');
MergedPath = fullfile(CurrentPath, 'merged');
SortedPath = fullfile(CurrentPath, 'sorted');
CorePaths = {PreProcessedPath, MergedPath, SortedPath};
for i = 1:length(CorePaths)
    if not(isfolder(CorePaths{i}))
        mkdir(CorePaths{i});
    end
end

% Create Parti Paths and Loop All Functions
Parti_List = dir(RawPath);
Parti_List(1:2) = [];
for i = 1 : length(Parti_List)
    % Create All Required Folders
    InPPPath = fullfile(RawPath, Parti_List(i).name);
    BehavioralPath = fullfile(InPPPath, 'behavioral', '*.csv');
    OutPPFilePath = fullfile(PreProcessedPath, Parti_List(i).name);
    OutMergedPath = fullfile(MergedPath, Parti_List(i).name);
    OutSortedPath = fullfile(SortedPath, Parti_List(i).name);
    PartiPaths = {OutPPFilePath, OutMergedPath, OutSortedPath};
    for j = 1: length(PartiPaths)
        if not(isfolder(PartiPaths{j}))
            mkdir(PartiPaths{j});
        end
    end
    OutMergedPath = append(OutMergedPath, '\merge.set');

    % Loop All Functions
    PREPROCESSALL(InPPPath, OutPPFilePath);
    MERGEALL(OutPPFilePath, OutMergedPath);
    SORTEPOCH(BehavioralPath, OutMergedPath, OutSortedPath);
end

disp('all done');
close all;
clear all;

function PREPROCESSALL(InPPPath, OutPPFilePath)
    for k = 1:6
        InPPName = append(InPPPath, '\session_', num2str(k),'.raw');
        [PreProed, RM_Chan_info] = PrePro(InPPName);
        OutFileName = append(OutPPFilePath, '\session_', num2str(k), '_preprocessed.set');
        PreProed = pop_saveset(PreProed, 'filename', OutFileName);
        OutFileName = append(OutPPFilePath, '\session_', num2str(k), '_removed_channel_info.csv');
        csvwrite(OutFileName, RM_Chan_info);
        clear PreProed RM_Chan_info;
    end
end


function [OutEEG, removed_channel] = PrePro(InFileName)
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
    EEG = pop_chanedit(EEG, 'lookup',...
        'C:\\Users\\Herrick Fung\\Desktop\\Course Materials\\Sem 4.1\\PSY402 Research Thesis II\\experiment_part2\\result\\GSN-HydroCel-257.sfp',...
        'load',{'C:\\Users\\Herrick Fung\\Desktop\\Course Materials\\Sem 4.1\\PSY402 Research Thesis II\\experiment_part2\\result\\GSN-HydroCel-257.sfp',...
        'filetype','sfp'},'delete',257);

    % Remove bad channels with clean_rawdata()
    old_EEG = EEG;
    EEG = pop_clean_rawdata(EEG, 'FlatlineCriterion',5,'ChannelCriterion',0.8,...
        'LineNoiseCriterion',4,'Highpass','off','BurstCriterion','off',...
        'WindowCriterion','off','BurstRejection','off','Distance','Euclidian');

    % get removed and interpolate channel info.
    full_channel_set = [];
    removed_channel_set = [];
    
    for n = 1:numel(old_EEG.chanlocs)
        full_channel_set = [full_channel_set, old_EEG.chanlocs(n).urchan];
    end
    for n = 1:numel(EEG.chanlocs)
        removed_channel_set = [removed_channel_set, EEG.chanlocs(n).urchan];
    end
    removed_channel = setdiff(full_channel_set, removed_channel_set);
    
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
    for m = 1:6
        InFileName = append('session_', num2str(m), '_preprocessed.set');
        LoadFile = pop_loadset(InFileName, OutPPFilePath);
        if m == 1
            MergedSet = LoadFile;
        else
            MergedSet = pop_mergeset(MergedSet, LoadFile, true);
        end
    end

    MergedSet = pop_saveset(MergedSet, 'filename', OutMergedPath);
    clear LoadFile MergedSet;
end


function SORTEPOCH(BehavioralPath, OutMergedPath, OutSortedPath)
    BehavioralFileName = dir(BehavioralPath);
    BehavioralFileName = append(BehavioralFileName.folder, '\', BehavioralFileName.name);
    TrialList = readtable(BehavioralFileName, 'Format', 'auto');
    
    trial_con = struct('single',[TrialList.Trial_No, TrialList.Condition == 1],...
                       'lowSD', [TrialList.Trial_No, TrialList.Condition == 2],...
                       'highSD', [TrialList.Trial_No, TrialList.Condition == 3]...
                       );
    
    fn = fieldnames(trial_con);
    
    for n = 1:numel(fn)
        trial_con.(fn{n}) = find(trial_con.(fn{n})(:,2)==1);
        trial_con.(fn{n}) = reshape(trial_con.(fn{n}), 1, 252);
    end
    
    FullEpochs = pop_loadset(OutMergedPath);
    SortedEpochs = struct('single_epochs', pop_selectevent(FullEpochs,'epoch',trial_con.single),...
                          'lowSD_epochs', pop_selectevent(FullEpochs,'epoch',trial_con.lowSD),...
                          'highSD_epochs', pop_selectevent(FullEpochs,'epoch',trial_con.highSD)...
                          );
    
    efn = fieldnames(SortedEpochs);
    
    for o = 1:numel(efn)
        OutFileName = append(OutSortedPath, efn{o}, '.set');
        SortedEpochs.(efn{o}) = pop_saveset(SortedEpochs.(efn{o}), 'filename', OutFileName);
    end
   
    clear FullEpochs SortedEpochs       
end
