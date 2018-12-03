#! /usr/bin/python3

"""
This script demonstrates how to open, parse and visualise the PInSoRo dataset.

It relies on Python's matplotlib to displa in 3D the children' facial landmarks,
their head pose estimate, the direction of their gaze, as well as the (manual)
annotations of their social behaviour.

You can use this script as a starting point for your own applications.

License: CC-0
"""

import argparse
import logging
logging.basicConfig(level=logging.INFO)

import numpy as np
import pandas as pd
import transformations

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation


# Set up formatting for the movie files
Writer = animation.writers['ffmpeg']
writer = Writer(fps=30, metadata=dict(artist='Severin Lemaignan'), bitrate=1800)

START_IDX=0
SEQ_SIZE=600

IMAGE_WIDTH=0.960 # the orginial images' resolution, in px/1000
IMAGE_HEIGHT=0.540

SANDTRAY_WIDTH=0.338 #m
SANDTRAY_LENGTH=0.600 #m

FPS=30.

LANDMARKS_OFFSET=10 # the index of the first column containing facial landmarks
LANDMARKS_PADDING=69 # number of fields between the landmarks of the purple child and those of the yellow child
NUM_FACIAL_LANDMARKS=70 * 2 # 70 X (x,y) values

# distance from the camera of the 'image plane' where the 2D facial landmarks
# are plotted
Z_IMAGE_PLANE = 1. #m


################## UTILITIES ####################

# Transformations of 3D points to the centre of the table (common reference
# frame)

def make_transform_matrix(quaternion, translation):
    M = np.identity(4)
    T = transformations.translation_matrix(translation)
    M = np.dot(M, T)
    R = transformations.quaternion_matrix(quaternion)
    M = np.dot(M, R)

    M /= M[3, 3]

    return M

# Obtained with the following steps:
# $ rosparam set /use_sim_time True
# $ rosbag play --clock freeplay.bag
# $ rosrun tf static_transform_publisher -0.3 0.169 0 0 0 0 sandtray_centre sandtray 20
# $ rosrun tf tf_echo sandtray_centre camera_{purple|yellow}_rgb_optical_frame
YELLOW_CAM_TO_CENTRE_QUATERNION=[-0.530, 0.220, -0.314, 0.757]
YELLOW_CAM_TO_CENTRE_TRANSLATION=[-0.408, -0.208, 0.035]

PURPLE_CAM_TO_CENTRE_QUATERNION=[0.220, -0.530, 0.757, -0.314]
PURPLE_CAM_TO_CENTRE_TRANSLATION=[-0.408, 0.190, 0.035]

# numpy.dot({PURPLE,YELLOW}_CAM_TO_CENTRE, <vector>) transforms
# a vector <vector> from one of the camera's frame to the centre of the sandtray table frame.
YELLOW_CAM_TO_CENTRE =  make_transform_matrix(YELLOW_CAM_TO_CENTRE_QUATERNION, YELLOW_CAM_TO_CENTRE_TRANSLATION)
PURPLE_CAM_TO_CENTRE =  make_transform_matrix(PURPLE_CAM_TO_CENTRE_QUATERNION, PURPLE_CAM_TO_CENTRE_TRANSLATION)


def project_gaze_on_plane(gaze_origin, gaze_vector, plane):
    """ Calculates the 2D coordinate of the intersection between a ray cast
    from a 3D 'gaze_orgin' along the 'gaze_vector' and the XY plane defined by 'plane'
    pose ('plane' is a 4x4 transformation matrix, expressed in the
    same (arbitrary) reference frame as gaze_origin).

    :returns: the [x,y,z] coordinates of the ray intersection, expressed in the
    'plane' reference frame (as such, the z coordinate should always be 0).
    """

    plane_normal = normalize(numpy.dot(plane, [0,0,1,1])[:3])
    distance_plane_to_origin = 0

    t = - (numpy.dot(gaze_origin, plane_normal) + distance_plane_to_origin) / (numpy.dot(gaze_vector, plane_normal))

    gaze_projection = gaze_origin + gaze_vector * t

    return gaze_projection


def idot(a,b):
    """ This simple helper function is required later as numpy.apply_along_axis does
    not let us change the order of parameters, and we need
    np.dot(<transform>, <vector>) and not np.dot(<vector>, <transform>).
    """
    return np.dot(b,a)

################## MAIN RENDERING FUNCTIONS ####################

def update(num, data, plots, time_label, ann_labels):
    """ This function is called by matplotlib' AnimationFunc for each frame.

    :param num: the frame index
    :param data: the pandas DataFrame containing the dataset
    :param plots: the matplotlib 3D plots that we update. This includes the
                  scatter plots of the 2D facial landmarks, the gaze vectors, 
                  the orientation of the heads
    :param time_label: the matplotlib text objects that we update with the frame
                       index and elapsed time
    :param ann_labels: the matplotlib text objects that we update with the
                       social annotations

    :return: nothing. However, the plots and labels are updated.
    """

    ####### Facial landmarks

    # coordinates of the facial landmarks of the purple child, in the purple
    # camera reference frame
    purple_face = np.array(
            # x coordinates (in m) of the facial landmarks of the purple child
            [IMAGE_WIDTH * data.iloc[START_IDX+num,
                                     LANDMARKS_OFFSET:LANDMARKS_OFFSET+NUM_FACIAL_LANDMARKS:2] - IMAGE_WIDTH/2,
            # y coordinates (in m) of the facial landmarks of the purple child
             IMAGE_HEIGHT * data.iloc[START_IDX+num, 
                                      LANDMARKS_OFFSET + 1:LANDMARKS_OFFSET + 1 + NUM_FACIAL_LANDMARKS:2] - IMAGE_HEIGHT/2, 
             # all the 2D points are placed on the same plane
             [Z_IMAGE_PLANE] * int(NUM_FACIAL_LANDMARKS/2), 
             # (we need homogenous vectors for transformation)
             [1]* int(NUM_FACIAL_LANDMARKS/2)]).transpose()

    # transform of the 2D landmarks into the common reference frame (centre of
    # the interactive table)
    purple_face_transformed = np.apply_along_axis(idot,1,purple_face,PURPLE_CAM_TO_CENTRE).transpose()

    # update the corresponding matplotlib plot
    plots[0][0].set_data(purple_face_transformed[0:2,:])
    plots[0][0].set_3d_properties(purple_face_transformed[2,:])


    # same thing for the yellow child
    stride = NUM_FACIAL_LANDMARKS + LANDMARKS_PADDING

    yellow_face = np.array(
            [IMAGE_WIDTH*data.iloc[START_IDX+num,
                                   LANDMARKS_OFFSET + stride:LANDMARKS_OFFSET + stride +NUM_FACIAL_LANDMARKS:2] - IMAGE_WIDTH/2, 
             IMAGE_HEIGHT*data.iloc[START_IDX+num, 
                                    LANDMARKS_OFFSET + 1 + stride:LANDMARKS_OFFSET + 1 + stride + NUM_FACIAL_LANDMARKS:2] - IMAGE_HEIGHT/2, 
             [Z_IMAGE_PLANE] * int(NUM_FACIAL_LANDMARKS/2), 
             [1]* int(NUM_FACIAL_LANDMARKS/2)]).transpose()

    yellow_face_transformed = np.apply_along_axis(idot,1,yellow_face,YELLOW_CAM_TO_CENTRE).transpose()

    plots[1][0].set_data(yellow_face_transformed[0:2,:])
    plots[1][0].set_3d_properties(yellow_face_transformed[2,:])

    ###### 3D pose of the purple head

    px = data["purple_child_head_x"][START_IDX+num]
    py = data["purple_child_head_y"][START_IDX+num]
    pz = data["purple_child_head_z"][START_IDX+num]

    # the 6D pose estimate is already in the table reference frame; no need to
    # transform

    plots[2][0].set_data([px, py])
    plots[2][0].set_3d_properties(pz)

    ###### 3D pose of the yellow head

    yx = data["yellow_child_head_x"][START_IDX+num]
    yy = data["yellow_child_head_y"][START_IDX+num]
    yz = data["yellow_child_head_z"][START_IDX+num]

    plots[3][0].set_data([yx, yy])
    plots[3][0].set_3d_properties(yz)

    ####### Heads orientation

    # to represent the head orientation, we draw a small (red, green, blue)
    # reference gizmo at the head's origin. To this end, we transform simple
    # unit vectors x, y, z from the head reference frame to the common table
    # reference frame.

    xyz_vectors = [[0,0,0,1],[0.1,0,0,1],[0,0,0,1],[0,0.1,0,1],[0,0,0,1],[0,0,0.1,1]]

    # get the head 3D rotation (Euler angles) from the dataset
    prx = data["purple_child_head_rx"][START_IDX+num]
    pry = data["purple_child_head_ry"][START_IDX+num]
    prz = data["purple_child_head_rz"][START_IDX+num]

    yrx = data["yellow_child_head_rx"][START_IDX+num]
    yry = data["yellow_child_head_ry"][START_IDX+num]
    yrz = data["yellow_child_head_rz"][START_IDX+num]

    # create the transformation matrices
    purple_headpose = transformations.compose_matrix(angles=[prx,pry,prz], translate=[px,py,pz])
    yellow_headpose = transformations.compose_matrix(angles=[yrx,yry,yrz], translate=[yx,yy,yz])

    # apply them to the unit vectors
    purple_xyz = np.apply_along_axis(idot,1,xyz_vectors,purple_headpose)
    yellow_xyz = np.apply_along_axis(idot,1,xyz_vectors,yellow_headpose)

    # finally, update each of the plot (each plot is a simple red/green/blue
    # coloured line, 3 for the purple child, 3 for the yellow child)
    vx=purple_xyz[0:2].transpose()
    plots[6][0].set_data(vx[0],vx[1])
    plots[6][0].set_3d_properties(vx[2])

    vy=purple_xyz[2:4].transpose()
    plots[7][0].set_data(vy[0],vy[1])
    plots[7][0].set_3d_properties(vy[2])

    vz=purple_xyz[4:].transpose()
    plots[8][0].set_data(vz[0],vz[1])
    plots[8][0].set_3d_properties(vz[2])

    vx=yellow_xyz[0:2].transpose()
    plots[9][0].set_data(vx[0],vx[1])
    plots[9][0].set_3d_properties(vx[2])

    vy=yellow_xyz[2:4].transpose()
    plots[10][0].set_data(vy[0],vy[1])
    plots[10][0].set_3d_properties(vy[2])

    vz=yellow_xyz[4:].transpose()
    plots[11][0].set_data(vz[0],vz[1])
    plots[11][0].set_3d_properties(vz[2])

    ###### 3D gaze

    # the gaze vector origin is at the head's origin.
    # the gaze vector is already in the table reference frame, so 
    # we only need to sum (head + gaze)
    gaze_magnitude = 0.300 #m
    pgx = data["purple_child_gaze_x"][START_IDX+num] * gaze_magnitude
    pgy = data["purple_child_gaze_y"][START_IDX+num] * gaze_magnitude
    pgz = data["purple_child_gaze_z"][START_IDX+num] * gaze_magnitude

    plots[4][0].set_data([[px,px+pgx],[py,py+pgy]])
    plots[4][0].set_3d_properties([pz,pz+pgz])

    ygx = data["yellow_child_gaze_x"][START_IDX+num] * gaze_magnitude
    ygy = data["yellow_child_gaze_y"][START_IDX+num] * gaze_magnitude
    ygz = data["yellow_child_gaze_z"][START_IDX+num] * gaze_magnitude

    plots[5][0].set_data([[yx,yx+ygx],[yy,yy+ygy]])
    plots[5][0].set_3d_properties([yz,yz+ygz])




    ################## Labels/annotations

    ann_p_label, ann_y_label = ann_labels

    # first check that annotations are available for this frame.
    # When annotations are available, the field 'annotators' contain the names
    # of the annotators. Otherwise, pandas returns 'nan'
    if isinstance(data["annotators"][START_IDX+num], str):
        time_label.set_text("frame #%d (t=%.1fs)" % (num, num/FPS))
        ann_p_label.set_text(data.iloc[START_IDX+num,-6] + "\n" + \
                             data.iloc[START_IDX+num,-5] + "\n" + \
                             data.iloc[START_IDX+num,-4])

        # in the child-robot condition, no annotation for the yellow child
        if data["condition"][START_IDX+num] == "childchild":
            ann_y_label.set_text(data.iloc[START_IDX+num,-3] + "\n" + \
                                 data.iloc[START_IDX+num,-2] + "\n" + \
                                 data.iloc[START_IDX+num,-1])
        else:
            ann_y_label.set_text("[robot]")
    else:
        time_label.set_text("frame #%d (t=%.1fs) (no annotations)" % (num, num/FPS))
    return plots

################ MAIN ###################

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='PInSoRo Dataset -- Dataset player')
    parser.add_argument("-i", "--start-idx", type=int, default=0, help="Start frame")
    parser.add_argument("-l", "--length", type=int, help="# of frames to display (default: full dataset)")
    parser.add_argument("--video", nargs="?", help="If set, save the animation as a video with given filename")
    parser.add_argument("path", help="path to the dataset")

    args = parser.parse_args()

    START_IDX=args.start_idx
    SEQ_SIZE=args.length

    # we are using pandas to read the CSV file. pandas is several order of
    # magnitude faster than Python's own CSV library
    logging.info("Loading dataset...")
    data=pd.read_csv(args.path)
    logging.info("Done loading.")

    # create and configure the matplotlib plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_proj_type('persp')
    fig.set_figwidth(30)
    fig.set_figheight(10)
    fig.set_dpi(100)

    ax.set_xlim3d([-0.200, 0.600])
    ax.set_ylim3d([-0.600, 0.600])
    ax.set_zlim3d([-0.100, 0.600])
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')

    # place the 3D camera so that the 2 children' faces are visible
    ax.azim=-170
    ax.elev=18

    colors = ["xkcd:royal purple", "xkcd:gold"]

    # First, we draw all the static scene objects:

    # draw the interactive table
    ax.plot([-SANDTRAY_LENGTH/2, -SANDTRAY_LENGTH/2, SANDTRAY_LENGTH/2, SANDTRAY_LENGTH/2, -SANDTRAY_LENGTH/2],
            [-SANDTRAY_WIDTH/2, SANDTRAY_WIDTH/2, SANDTRAY_WIDTH/2, -SANDTRAY_WIDTH/2, -SANDTRAY_WIDTH/2],
            0, color="black")

    # draw the main axes of the scene
    ax.plot([0,0.100],[0,0],[0,0], color="red")
    ax.plot([0,0],[0,0.100],[0,0], color="green")
    ax.plot([0,0],[0,0],[0,0.100], color="blue")

    # draw the 2 cameras
    cw = 0.05 # width of the camera
    ch= cw * 1. *  IMAGE_HEIGHT/IMAGE_WIDTH # height of the camera, keeping the image's aspect ratio
    cz = Z_IMAGE_PLANE / IMAGE_WIDTH * (cw*2)
    camera = [[0, cw,-cw,0,cw,-cw,0,cw,cw,-cw,-cw],
              [0,ch,ch,0,-ch,-ch,0,-ch,ch,ch,-ch],
              [0, cz,cz,0,cz,cz,0,cz,cz,cz,cz],
              [1]*11]
    purple_camera = np.apply_along_axis(idot,0,camera,PURPLE_CAM_TO_CENTRE)
    yellow_camera = np.apply_along_axis(idot,0,camera,YELLOW_CAM_TO_CENTRE)

    ax.plot(*purple_camera[0:3], color=colors[0])
    ax.plot(*yellow_camera[0:3], color=colors[1])

    # draw the image plane of the 2 cameras (plan of the 2D facial landmarks)
    image_plane = [[-IMAGE_WIDTH/2, IMAGE_WIDTH/2, IMAGE_WIDTH/2, -IMAGE_WIDTH/2, -IMAGE_WIDTH/2],
                   [-IMAGE_HEIGHT/2, -IMAGE_HEIGHT/2, IMAGE_HEIGHT/2, IMAGE_HEIGHT/2, -IMAGE_HEIGHT/2],
                   [Z_IMAGE_PLANE]*5,
                   [1]*5]

    purple_image_plane = np.apply_along_axis(idot,0,image_plane,PURPLE_CAM_TO_CENTRE)
    yellow_image_plane = np.apply_along_axis(idot,0,image_plane,YELLOW_CAM_TO_CENTRE)

    ax.plot(*purple_image_plane[0:3])
    ax.plot(*yellow_image_plane[0:3])

    # Then, we prepare empty plots for all the dynamic objects:

    # 2D facial landmarks
    plots=[ax.plot([], [], [], 'o', markersize=2, color=c) for c in colors]

    # 3D heads
    plots += [ax.plot([], [], [], 'o', markersize=10, color=c) for c in colors]

    # gaze vectors
    plots += [ax.plot([], [], [], color=c) for c in colors]

    # xyz gizmo, purple head
    plots += [ax.plot([], [], [], color=c) for c in ["red","green","blue"]]
    # xyz gizmo, yellow head
    plots += [ax.plot([], [], [], color=c) for c in ["red","green","blue"]]

    time_text=ax.text(-0.500,0,0,"",None, fontsize=14)
    ann_p_text = ax.text(0, -0.300, 0, "",None, fontsize=12, color=colors[0])
    ann_y_text = ax.text(0, 0.300,0, "",None, fontsize=12, color=colors[1])

    ann_labels=[ann_p_text,ann_y_text]

    # Finally, we create the Animation object
    line_ani = animation.FuncAnimation(fig, update, SEQ_SIZE, fargs=(data, plots, time_text, ann_labels),
                                    interval=1000/FPS, blit=False, repeat=False)

    if args.video is not None:
        print("Generating video... please be patient...")

        ax.set_aspect(540/960.)
        line_ani.save(args.video, writer=writer)
    else:
        plt.show()
