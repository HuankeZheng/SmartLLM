# SmartLLM

### Workflow

The SmartLLM framework executes a coherent, iterative workflow to generate data: (1) The Agent generates or dynamically adjusts the daily schedule. (2) The Event Module decomposes scheduled activities into executable event sequences (Move, Control, Execute), orchestrates their execution, and records the resulting multi-dimensional trajectories. (3) During execution, unplanned events (e.g., phone calls) are triggered stochastically. (4) For waiting periods or triggered calls, the Agent makes real-time decisions (e.g., choosing a filler activity), ensuring behavioral fluidity. This closed-loop process iterates, guaranteeing that the final dataset possesses both strong logical consistency and rich behavioral diversity.

### Dataset Comparison

Comparison of different smart home dataset paradigms, illustrating the dimensional fragmentation between traditional Human Activity Prediction (HAP) datasets and User-Device Interaction (UDI) datasets, and the integrated multi-dimensional approach of SmartLLM.


### Case Study

Example of a multi-activity interleaving scenario. Device and sensor logs provide crucial context for recognizing the
interrupted “Cooking” activity.

| Week    | Time  | Sensor   | Device       | Activity |
|---------|-------|----------|--------------|----------|
| Tuesday | 09:13 | Motion15 | -            | Cooking  |
| Tuesday | 09:14 | -        | FridgeON     | Cooking  |
| Tuesday | 09:15 | -        | FridgeOFF    | Cooking  |
| Tuesday | 09:26 | Motion15 | -            | Cooking  |
| Tuesday | 09:26 | Motion15 | -            | Cooking  |
| Tuesday | 09:27 | -        | StoveON      | Cooking  |
| Tuesday | 09:28 | Motion16 | -            | -        |
| Tuesday | 09:28 | Motion15 | -            | -        |
| Tuesday | 09:28 | Door03   | -            | -        |
| Tuesday | 09:29 | Motion11 | -            | -        |
| Tuesday | 09:29 | Motion17 | -            | -        |
| Tuesday | 09:29 | Motion18 | -            | -        |
| Tuesday | 09:29 | Door04   | -            | -        |
| Tuesday | 09:29 | -        | StudyLampON  | Reading  |
| Tuesday | 09:29 | Door04   | -            | Reading  |
| Tuesday | 09:30 | Motion19 | -            | Reading  |
| Tuesday | 10:03 | Motion19 | -            | Reading  |
| Tuesday | 10:03 | Door04   | -            | Reading  |
| Tuesday | 10:04 | -        | StudyLampOFF | Reading  |
| Tuesday | 10:04 | Door04   | -            | -        |
| Tuesday | 10:04 | Motion18 | -            | -        |
| Tuesday | 10:05 | Motion17 | -            | -        |
| Tuesday | 10:05 | Motion11 | -            | -        |
| Tuesday | 10:05 | Door03   | -            | -        |
| Tuesday | 10:05 | Motion15 | -            | -        |
| Tuesday | 10:05 | Motion16 | -            | -        |
| Tuesday | 10:06 | -        | StoveOFF     | Cooking  |

### Ablation study

results of activity prediction performance (Top-1 Accuracy %) across different feature combinations and user profiles.

| Configuration     | OldMan       | RemoteWorker | HolidayMaker |
|-------------------|--------------|--------------|--------------|
| Base (Activity)   | 0.626        | 0.648        | 0.578        | 
| + Device          | 0.797        | 0.814        | 0.815        | 
| + Sensor          | <u>0.633</u> | <u>0.862</u> | <u>0.894</u> | 
| + Device + Sensor | **0.909**    | **0.890**    | **0.907**    |

