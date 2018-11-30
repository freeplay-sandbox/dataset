#! /usr/bin/python3

import argparse

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation


# Set up formatting for the movie files
Writer = animation.writers['ffmpeg']
writer = Writer(fps=30, metadata=dict(artist='Severin Lemaignan'), bitrate=1800)

import numpy as np
import pandas as pd
import transformations

START_IDX=0
SEQ_SIZE=600

WIDTH=0.960
HEIGHT=0.540

SANDTRAY_WIDTH=0.338 #m
SANDTRAY_LENGHT=0.600 #m

FPS=30.

NUM_FACIAL_LANDMARKS=70 * 2

Z_IMAGE_PLANE = 1. #m

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
    return np.dot(b,a)


def update(num, data, faces, time_label, ann_labels):
    # NOTE: there is no .set_data() for 3 dim data...
    #faces[0].set_data(data.iloc[START_IDX:START_IDX+num, 7:77:2], -1*data.iloc[START_IDX:START_IDX+num, 8:78:2],0)
    #faces[0].set_3d_properties(list(range(num)))


    purple_face = np.array(
            [WIDTH*data.iloc[START_IDX+num, 10:10+NUM_FACIAL_LANDMARKS:2] - WIDTH/2, 
             HEIGHT*data.iloc[START_IDX+num, 11:11+NUM_FACIAL_LANDMARKS:2] - HEIGHT/2, 
             [Z_IMAGE_PLANE] * int(NUM_FACIAL_LANDMARKS/2), 
             [1]* int(NUM_FACIAL_LANDMARKS/2)]).transpose()

    purple_face_transformed = np.apply_along_axis(idot,1,purple_face,PURPLE_CAM_TO_CENTRE).transpose()
    #purple_face_transformed=purple_face

    faces[0][0].set_data(purple_face_transformed[0:2,:])
    faces[0][0].set_3d_properties(purple_face_transformed[2,:])

    offset = NUM_FACIAL_LANDMARKS + 69

    yellow_face = np.array(
            [WIDTH*data.iloc[START_IDX+num, 10+offset:10+offset+NUM_FACIAL_LANDMARKS:2] - WIDTH/2, 
             HEIGHT*data.iloc[START_IDX+num, 11+offset:11+offset+NUM_FACIAL_LANDMARKS:2] - HEIGHT/2, 
             [Z_IMAGE_PLANE] * int(NUM_FACIAL_LANDMARKS/2), 
             [1]* int(NUM_FACIAL_LANDMARKS/2)]).transpose()

    yellow_face_transformed = np.apply_along_axis(idot,1,yellow_face,YELLOW_CAM_TO_CENTRE).transpose()
    #yellow_face_transformed=yellow_face

    faces[1][0].set_data(yellow_face_transformed[0:2,:])
    faces[1][0].set_3d_properties(yellow_face_transformed[2,:])

    ###### 3D pose of the purple head

    px = data["purple_child_head_x"][START_IDX+num]
    py = data["purple_child_head_y"][START_IDX+num]
    pz = data["purple_child_head_z"][START_IDX+num]

    faces[2][0].set_data([px, py])
    faces[2][0].set_3d_properties(pz)

    ###### 3D pose of the yellow head
    yx = data["yellow_child_head_x"][START_IDX+num]
    yy = data["yellow_child_head_y"][START_IDX+num]
    yz = data["yellow_child_head_z"][START_IDX+num]

    faces[3][0].set_data([yx, yy])
    faces[3][0].set_3d_properties(yz)

    ###### 3D gaze
    gaze_magnitude = 0.300 #m
    pgx = data["purple_child_gaze_x"][START_IDX+num] * gaze_magnitude
    pgy = data["purple_child_gaze_y"][START_IDX+num] * gaze_magnitude
    pgz = data["purple_child_gaze_z"][START_IDX+num] * gaze_magnitude
    faces[4][0].set_data([[px,px+pgx],[py,py+pgy]])
    faces[4][0].set_3d_properties([pz,pz+pgz])

    ygx = data["yellow_child_gaze_x"][START_IDX+num] * gaze_magnitude
    ygy = data["yellow_child_gaze_y"][START_IDX+num] * gaze_magnitude
    ygz = data["yellow_child_gaze_z"][START_IDX+num] * gaze_magnitude
    faces[5][0].set_data([[yx,yx+ygx],[yy,yy+ygy]])
    faces[5][0].set_3d_properties([yz,yz+ygz])

    ####### Heads orientation
    xyz_vectors = [[0,0,0,1],[0.1,0,0,1],[0,0,0,1],[0,0.1,0,1],[0,0,0,1],[0,0,0.1,1]]

    prx = data["purple_child_head_rx"][START_IDX+num]
    pry = data["purple_child_head_ry"][START_IDX+num]
    prz = data["purple_child_head_rz"][START_IDX+num]

    yrx = data["yellow_child_head_rx"][START_IDX+num]
    yry = data["yellow_child_head_ry"][START_IDX+num]
    yrz = data["yellow_child_head_rz"][START_IDX+num]

    purple_headpose = transformations.compose_matrix(angles=[prx,pry,prz], translate=[px,py,pz])
    yellow_headpose = transformations.compose_matrix(angles=[yrx,yry,yrz], translate=[yx,yy,yz])

    purple_xyz = np.apply_along_axis(idot,1,xyz_vectors,purple_headpose)
    yellow_xyz = np.apply_along_axis(idot,1,xyz_vectors,yellow_headpose)

    vx=purple_xyz[0:2].transpose()
    faces[6][0].set_data(vx[0],vx[1])
    faces[6][0].set_3d_properties(vx[2])

    vy=purple_xyz[2:4].transpose()
    faces[7][0].set_data(vy[0],vy[1])
    faces[7][0].set_3d_properties(vy[2])

    vz=purple_xyz[4:].transpose()
    faces[8][0].set_data(vz[0],vz[1])
    faces[8][0].set_3d_properties(vz[2])

    vx=yellow_xyz[0:2].transpose()
    faces[9][0].set_data(vx[0],vx[1])
    faces[9][0].set_3d_properties(vx[2])

    vy=yellow_xyz[2:4].transpose()
    faces[10][0].set_data(vy[0],vy[1])
    faces[10][0].set_3d_properties(vy[2])

    vz=yellow_xyz[4:].transpose()
    faces[11][0].set_data(vz[0],vz[1])
    faces[11][0].set_3d_properties(vz[2])




    ################## Labels/annotations

    ann_p_label, ann_y_label = ann_labels
    if isinstance(data["annotators"][START_IDX+num], str):
        time_label.set_text("frame #%d (t=%.1fs)" % (num, num/FPS))
        ann_p_label.set_text(data.iloc[START_IDX+num,-6] + "\n" + \
                            data.iloc[START_IDX+num,-5] + "\n" + \
                            data.iloc[START_IDX+num,-4]
                            )
        if data["condition"][START_IDX+num] == "childchild":
            ann_y_label.set_text(data.iloc[START_IDX+num,-3] + "\n" + \
                                data.iloc[START_IDX+num,-2] + "\n" + \
                                data.iloc[START_IDX+num,-1])
        else:
            ann_y_label.set_text("[robot]")
    else:
        time_label.set_text("frame #%d (t=%.1fs) (no annotations)" % (num, num/FPS))
    return faces

##### Transformations of 3D points to the centre of the table

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



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='PInSoRo Dataset -- Dataset player')
    parser.add_argument("-i", "--start-idx", type=int, default=0, help="Start frame")
    parser.add_argument("-l", "--length", type=int, help="# of frames to display (default: full dataset)")
    parser.add_argument("--video", nargs="?", help="If set, save the animation as a video with given filename")
    parser.add_argument("path", help="path to the dataset")

    args = parser.parse_args()

    START_IDX=args.start_idx
    SEQ_SIZE=args.length

    print("Loading dataset...")
    data=pd.read_csv(args.path)
    print("Done loading.")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_proj_type('persp')
    fig.set_figwidth(30)
    fig.set_figheight(10)
    fig.set_dpi(100)


    #ax.set_aspect(1.)
    #ax.tick_params(labelbottom=False, bottom=False, left=False, labelleft=False)
    ax.set_xlim3d([-0.200, 0.600])
    ax.set_ylim3d([-0.600, 0.600])
    ax.set_zlim3d([-0.100, 0.600])
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')

    ax.azim=-170
    ax.elev=18

    colors = ["xkcd:royal purple", "xkcd:gold"]

    ax.plot([-SANDTRAY_LENGHT/2, -SANDTRAY_LENGHT/2, SANDTRAY_LENGHT/2, SANDTRAY_LENGHT/2, -SANDTRAY_LENGHT/2],
            [-SANDTRAY_WIDTH/2, SANDTRAY_WIDTH/2, SANDTRAY_WIDTH/2, -SANDTRAY_WIDTH/2, -SANDTRAY_WIDTH/2],
            0, color="black")

    ax.plot([0,0.100],[0,0],[0,0], color="red")
    ax.plot([0,0],[0,0.100],[0,0], color="green")
    ax.plot([0,0],[0,0],[0,0.100], color="blue")

    cw = 0.05
    ch= cw * 1. *  HEIGHT/WIDTH
    cz = Z_IMAGE_PLANE / WIDTH * (cw*2)
    camera = [[0, cw,-cw,0,cw,-cw,0,cw,cw,-cw,-cw],
              [0,ch,ch,0,-ch,-ch,0,-ch,ch,ch,-ch],
              [0, cz,cz,0,cz,cz,0,cz,cz,cz,cz],
              [1]*11]
    purple_camera = np.apply_along_axis(idot,0,camera,PURPLE_CAM_TO_CENTRE)
    yellow_camera = np.apply_along_axis(idot,0,camera,YELLOW_CAM_TO_CENTRE)

    ax.plot(*purple_camera[0:3], color="xkcd:royal purple")
    ax.plot(*yellow_camera[0:3], color="xkcd:gold")


    image_plane = [[-WIDTH/2, WIDTH/2, WIDTH/2, -WIDTH/2, -WIDTH/2],
                   [-HEIGHT/2, -HEIGHT/2, HEIGHT/2, HEIGHT/2, -HEIGHT/2],
                   [Z_IMAGE_PLANE]*5,
                   [1]*5]
    purple_image_plane = np.apply_along_axis(idot,0,image_plane,PURPLE_CAM_TO_CENTRE)
    yellow_image_plane = np.apply_along_axis(idot,0,image_plane,YELLOW_CAM_TO_CENTRE)

    ax.plot(*purple_image_plane[0:3])
    ax.plot(*yellow_image_plane[0:3])

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
    ann_p_text = ax.text(0, -0.300, 0, "",None, fontsize=12, color="xkcd:royal purple")
    ann_y_text = ax.text(0, 0.300,0, "",None, fontsize=12, color="xkcd:gold")

    ann_labels=[ann_p_text,ann_y_text]

    # Creating the Animation object
    line_ani = animation.FuncAnimation(fig, update, SEQ_SIZE, fargs=(data, plots, time_text, ann_labels),
                                    interval=1000/FPS, blit=False, repeat=False)

    if args.video is not None:
        print("Generating video... please be patient...")

        ax.set_aspect(540/960.)
        line_ani.save(args.video, writer=writer)
    else:
        plt.show()
