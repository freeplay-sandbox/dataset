PInSoRo dataset - data structure
================================

Each sub-directory represents one interaction. Directories are named after the
date and time at which the interaction has been recorded.

Inside each directory, the following files are **always** present:

- `experiment.yaml`: contains the interaction details.

Example:

```yaml
timestamp: 1496917355889909029 # timestamp of the begining of the interaction
condition: childchild # condition (childchild or childrobot)
purple-participant:
  id: 2017-06-08-11:18-p1
  age: 4
  gender: female
  details:
    tablet-familiarity: 0  # self-reported familiarity with tablets, from 0 (no familiarity to 2 (familiar)
yellow-participant: # absent in the child-robot condition
  id: 2017-06-08-11:18-y1
  age: 4
  gender: female
  details:
    tablet-familiarity: 2
markers:  # events of interest, annotated during the experiment by the experimenter. Timestamps in seconds from the begining
  75.936775922: interesting
  104.153236866: interesting
  214.65380907: interesting
  328.371172904: interesting
  376.429432868: interesting
  428.393737077: interesting
  590.867943048: issue
  685.981807947: interesting
  708.350763082: issue
  789.571500062: interesting
  811.970171928: interesting
notes: # open-ended notes, taken by the experimenter during the experiment. Timestamp in seconds from the begining.
  general: Both very quiet. P has done experiment before (1y002).
  75: Very quiet
  104: Y watching P
  214: Both absorbed in own games
  328: Confusion about colours
  376: P drawing pictures
  428: Quiet battle about colours
  590: P to FS "Look!"
  685: Y copied P's drawing
  708: P seeking encouragement from FS
  780: P drawing pictures, Y scribbling
  811: Both seem kind of bored
postprocess: # (optinal) details of specific post-processing performed on that
recording
    - recompressed sandtray background, start timestamp moved from 1496917354.451842 to 1498168785.467365
issues: # (optional) specific issues with this dataset
    - skeleton extraction failed
```
- `freeplay.bag`: *[missing if you do not have the full dataset]* the raw
  recordings, as [ROS bag file](http://wiki.ros.org/Bags). These bag files
  contains in particular all the RGB-D video streams and audio streams. To
  replay them, you need the `rosbag` tool to be installed, or other dedicated
  tools. See the [`tools/README.md`](../tools/README.md) for more details.
- `freeplay.bag.yaml`: this file describes the content of `freeplay.bag`. It can
  also be used to check the exact duration of the recording.
- `freeplay.poses.json`: *[missing if you haven't yet downloaded the dataset data]* stores the skeletons and facial features extracted from each of the video frames. See here [the format of the poses data](https://github.com/freeplay-sandbox/analysis#format-of-poses-files).
- `visual_tracking.bag` and `visual_tracking.poses.json`: same as `freeplay.bag`
  and `freeplay.poses.json`, but for the visual tracking preliminary task (a
  short task that the children performed before starting to play. They were
  instructed to follow with their gaze a moving target on the touchscreen)
- `freeplay.bag.md5`, `freeplay.poses.json.md5`, `visual_tracking.bag.md5`,
  `visual_tracking.poses.json.md5`: the MD5 checksums of the corresponding
  files, used to verify the data integrity of the recordings.

