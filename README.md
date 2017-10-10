The Plymouth Interactive Social Robots dataset
==============================================

This dataset contains 75 recordings of free-play interactions between 2 children
(45 recordings) or one child and one robot (30 recordings).

To learn more about the dataset, visit its [web
site](https://freeplay-sandbox.github.io/).

The remaining of this file describe how to manipulate the dataset.


Installation of the scripts
---------------------------

**The provided scripts require a bash interpreter (ie, the Linux command-line)
as well as a Python interpreter with all the rosbag tools installed.**

You simply need to download or clone the
[freeplay-sandbox-analysis](https://github.com/freeplay-sandbox/analysis)
project somewhere. All the scripts are in `scripts/`.

All the commands hereafter assume that you are in the `scripts/` directory.

Besides, most of the scripts take the path to the dataset as parameter,
typically `/media/<your username>/PInSoRo/freeplay_sandbox/data`. In the
examples hereafter, we call this path `$DATASET`.

Exploring the dataset
---------------------

`./dataset_stats` provides several statistics on the dataset:

- `dataset_stats $DATASET`: provides an overview of the dataset: file names,
  conditions, ages, durations of each session:

```
OVERVIEW
path                     timestamp   len   condition  C1    C2
2017-05-18-145157833880 1498207252 19:59 childchild 4 f   4 m  
2017-05-18-152118060656 1495117502 19:59 childchild 4 m   4 f  
2017-06-01-102743523980 1496309538 15:57 childchild 4 m   4 m  
2017-06-06-145135235899 1498170771 09:05 childchild 4 f   4 m  
2017-06-06-150808383862 1496758227 19:59 childchild 4 m   4 m  
...

Total records: 75 (child-child: 45, child-robot: 30)
Total duration: 27:42:01 -- Average duration per record: 00:22:09

Total duration, child-child: 18:06:41 -- Average duration per record,
child-child: 00:24:08

Total duration, child-robot: 09:35:20 -- Average duration per record,
child-robot: 00:19:10

Total children: 120
Total children duration: 45:48:43 -- Average duration per child: 00:22:54
```

With the option `--csv <csv file>```, you can conveniently save this data to a
csv file for processing in an external application.

- `dataset_stats --check $DATASET`: display the framerate of selected recorded topics, and display in red suspicious ones:

```
PUBLICATION RATES (in Hz)
                       cdt   len         tf  p/rgb/info   p/rgb/img  y/rgb/info   y/rgb/img  p/dpth/inf  p/dpth/img  y/dpth/inf  y/dpth/img     p/audio     y/audio    env/info     env/img 
2017-05-18-145157833880 CC 19:59     1943.6        30.5        30.5        30.5        30.4        30.5        30.5        30.6        30.6        25.7        25.7        30.7        30.7  
2017-05-18-152118060656 CC 19:59      828.1        30.2        30.1        30.1        30.0        30.2        30.2        30.1        30.1        25.1        25.1        30.0        30.0  
2017-06-01-102743523980 CC 15:57     1716.2        30.0        30.0        30.0        30.0        30.0        30.0        30.1        30.1        25.1        25.1        30.0        30.0  
2017-06-06-145135235899 CC 09:05    29127.1        30.5        30.4        30.6        30.5        30.4        30.4        30.6        30.6        26.5        26.3        30.7        30.6  
2017-06-06-150808383862 CC 19:59      905.7        30.1        30.1        30.1        30.1        30.2        30.2        30.2        30.2        25.2        25.3        29.8        29.8  
2017-06-07-101750079399 CR 18:22     1140.4        30.1        30.0        30.1        30.0        30.2        30.2        30.2        30.2        25.4        25.3        29.0        29.0  
2
```

- `dataset_stats --filter "<expression>" $DATASET` returns the sessions that
  match `<expression>`.
  
`<expression>` is any valid Python expression. The
following variable can be used: `age` (average age of the participants),
`age1`, `age2` (ages of each of the participants), `gender1`, `gender2`
(either `male` or `female`),
`duration` (in seconds), `condition` (can be either `childchild` or
`childrobot`).

Example that returns all sessions with both children being 6 yo and the first
child ('purple' child) being a girl:

```sh
$ ./dataset_stats --filter "age1==6 and age2==6 and gender1=='female'" $DATASET
/media/user/PInSoRo/freeplay_sandbox/data/2017-06-26-112331105839
/media/user/PInSoRo/freeplay_sandbox/data/2017-06-28-110943922717
/media/user/PInSoRo/freeplay_sandbox/data/2017-07-06-101405806926
```

Example returning only the child-robot sessions:
```sh
$ ./dataset_stats --filter "condition=='childrobot'" $DATASET
```


