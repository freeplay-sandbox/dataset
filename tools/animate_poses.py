import argparse

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation


# Set up formatting for the movie files
Writer = animation.writers['ffmpeg']
writer = Writer(fps=30, metadata=dict(artist='Severin Lemaignan'), bitrate=1800)

import pandas as pd

START_IDX=0
SEQ_SIZE=600

FPS=30.

NUM_FACIAL_LANDMARKS=70 * 2

def update(num, data, faces, time_label, ann_labels):
    # NOTE: there is no .set_data() for 3 dim data...
    #faces[0].set_data(data.iloc[START_IDX:START_IDX+num, 7:77:2], -1*data.iloc[START_IDX:START_IDX+num, 8:78:2],0)
    #faces[0].set_3d_properties(list(range(num)))
    faces[0][0].set_data(-1*data.iloc[START_IDX+num, 7:7+NUM_FACIAL_LANDMARKS:2] + .25, -1*data.iloc[START_IDX+num, 8:8+NUM_FACIAL_LANDMARKS:2]+1)
    offset = NUM_FACIAL_LANDMARKS
    faces[1][0].set_data(-1*data.iloc[START_IDX+num, 7+offset:7+offset+NUM_FACIAL_LANDMARKS:2] + .75, -1*data.iloc[START_IDX+num, 8+offset:8+offset+NUM_FACIAL_LANDMARKS:2]+1)


    time_label.set_text("frame #%d (t=%.1fs)" % (num, num/FPS))
    ann_p_label, ann_y_label = ann_labels
    ann_p_label.set_text(data.iloc[START_IDX+num,-6])
    ann_y_label.set_text(data.iloc[START_IDX+num,-3])
    return faces


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='PInSoRo Dataset -- Dataset player')
    parser.add_argument("-i", "--start-idx", type=int, default=0, help="Start frame")
    parser.add_argument("-l", "--length", type=int, default=600, help="# of frames to display")
    parser.add_argument("--video", nargs="?", help="If set, save the animation as a video with given filename")
    parser.add_argument("path", help="path to the dataset")

    args = parser.parse_args()

    START_IDX=args.start_idx
    SEQ_SIZE=args.length

    print("Loading dataset...")
    data=pd.read_csv(args.path)
    print("Done loading.")

    fig, ax = plt.subplots()
    fig.set_figwidth(30)
    fig.set_figheight(10)
    fig.set_dpi(100)


    ax.set_aspect(540/960.)
    ax.tick_params(labelbottom=False, bottom=False, left=False, labelleft=False)
    ax.set_xlim([-.7, .7])
    ax.set_ylim([0, 1])


    colors = ["xkcd:royal purple", "xkcd:gold"]

    plots=[ax.plot([], [], 'o', color=c) for c in colors]

    time_text=ax.text(0,0.9,"", fontsize=18)
    ann_p_text = ax.text(-0.5, 0.1,"", fontsize=14)
    ann_y_text = ax.text(0.5, 0.1,"", fontsize=14)

    ann_labels=[ann_p_text,ann_y_text]

    # Creating the Animation object
    line_ani = animation.FuncAnimation(fig, update, SEQ_SIZE, fargs=(data, plots, time_text, ann_labels),
                                    interval=1000/FPS, blit=False, repeat=False)

    if args.video is not None:
        print("iGenerating video... please be patient...")
        line_ani.save(args.video, writer=writer)
    else:
        plt.show()
