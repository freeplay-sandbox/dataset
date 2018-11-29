PInSoRo dataset - data structure
================================

Each sub-directory represents one interaction. Directories are named after the
date and time at which the interaction has been recorded.

The content of the directories depends on the data you have actually downloaded:

- this repository contains only the dataset's *meta-data* and *annotations* (cf
  section *Meta-data* below)
- if you have downloaded the publicly available *anonymous dataset* from
  [Zenodo](https://doi.org/10.5281/zenodo.1043507), you find additional CSV
  files containing facial features, skeletons, gaze, etc. See section *Anonymous
  dataset* below.
- if you have [obtained access](https://freeplay-sandbox.github.io/application) to the full data, the subdirectories also
  contains the original ROS bag files, including all the raw audio and video
  footage.

## Meta-data

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

- `freeplay.bag.yaml`: this file describes the content of `freeplay.bag`. It can
  also be used to check the exact duration of the recording.
- `freeplay.annotations.<annotator name>.yaml`: annotations of social behaviours
  for this recording (*missing for a few interactions that have not been
  annotated*). The timestamps in these files correspond to the ROS bag file
  timestamps.
- `freeplay.bag.md5`, `freeplay.poses.json.md5`, `visual_tracking.bag.md5`,
  `visual_tracking.poses.json.md5`: the MD5 checksums of the corresponding
  files, used to verify the data integrity of the recordings.

## Anonymised dataset

- `pinsoro-*.csv`: an easy-to-consume CVS file with all the main dataset
  features, sampled at 30Hz. [See below for the
  details](#format-of-the-csv-files). **THIS IS MOST LIKELY THE FILES YOU WANT
  TO USE**.
- `freeplay.poses.json`: stores the skeletons and facial features extracted from
  each of the video frames. See here [the format of the poses
  data](https://github.com/freeplay-sandbox/analysis#format-of-poses-files).
- `visual_tracking.poses.json`: same as `freeplay.poses.json`, but for the
  visual tracking preliminary task (a short task that the children performed
  before starting to play. They were instructed to follow with their gaze a
  moving target on the touchscreen)

## Full dataset

- `freeplay.bag`: the raw recordings, as [ROS bag
  file](http://wiki.ros.org/Bags). These bag files contains in particular all
  the RGB-D video streams and audio streams. To replay them, you need the
  `rosbag` tool to be installed, or other dedicated tools. See the
  [`tools/README.md`](../tools/README.md) for more details.
- `visual_tracking.bag`: same as `freeplay.bag`, but for the visual tracking
  preliminary task (a short task that the children performed before starting to
  play. They were instructed to follow with their gaze a moving target on the
  touchscreen)
- `video/camera_{purple|yellow|env}_raw.mkv`: RGB video streams extracted from the bag, for all three cameras (the two child-facing cameras and the environment camera)
- `video/camera_{purple|yellow|env}_skel.mkv`: skeleton and facial features of
  the children, over a uniform black background
- `video/camera_{purple|yellow|env}.mkv`: skeleton and facial features of
  the children, overlaid on the raw video footage
- `audio/freeplay_camera_{purple|yellow}_audio.{mp3|wav}`: audio streams, as recorded by the two child-facing cameras


Format of the CSV files
-----------------------

The `pinsoro-*.csv` files contains 449 fields, explained below.
The first row contains the columns headers.

The data is sampled at 30Hz. It starts at the first video frame of either of the
2 cameras filming the children's faces.

Note that the children were wearing brightly colored sport bibs (the left child
had a yellow one, the right child a purple one). The (left) camera filming the
(right) *purple child* is accordingly refered to as the *purple camera*, and the
(right) camera filming the *yellow child* as the *yellow camera*.

Besides, in the child-robot condition, the robot was always replacing the
*yellow child*. Hence, in that condition, all yellow child-related data is
missing.


- `timestamp`: UNIX timestamp of the row; the first timestamp is the timestamp
  of the first recorded video frame, on either of the two cameras
- `id`: ID of this recording (simply the date and time of the start of the
  experiment -- note that this is typically a few minutes before the the
  timestamp of the first video frame)
- `condition`: child-child or child-robot. [Refer to the
  website](https://freeplay-sandbox.github.io/dataset) for details.
- `annotators`: name of the annotators who annotated this interaction. If empty,
  this interaction has not been annotated. If more than one annotator, the names
  are separated by a '+'
- `complete`: true if all the data is available at that timestamp. Might be
  false for different reasons (no annotation, missing video frame, etc)
- `purple_child_age`, `purple_child_gender`, `yellow_child_age`, `yellow_child_gender`: self explanatory
- `purple_frame_idx`: index of the frame in the purple camera video stream.
  Can be used to quickly extract a specific frame or range of frame in the video
  stream
- `purple_child_face{00..69}_{x,y}`: 2D coordinates of the 70 facial landmarks
  (including pupils) extracted by [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose/). See [OpenPose documentation](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md#face-output-format) for the location of these landmarks.
- `purple_child_skel{00..17}_{x,y}`: 2D coordinates of the 18 skeleton keypoints
  extracted by [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose/). See [OpenPose documentation](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md#pose-output-format-coco) for the location of these keypoints. Note that, due to the experimental setting generating a lot of occlusion (children sitting in front of a table), the skeletal data is not always reliable

