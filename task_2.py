from math import floor
import math
from typing import NoReturn

import cv2
import json

def open_video(path: str) -> cv2.VideoCapture:
    """Opens a video file.

    Args:
        path: the location of the video file to be opened

    Returns:
        An opencv video capture file.
    """
    video_capture = cv2.VideoCapture(path)
    if not video_capture.isOpened():
        raise RuntimeError(f'Video at "{path}" cannot be opened.')
    return video_capture


def get_frame_dimensions(video_capture: cv2.VideoCapture) -> tuple[int, int]:
    """Returns the frame dimension of the given video.

    Args:
        video_capture: an opencv video capture file.

    Returns:
        A tuple containing the height and width of the video frames.

    """
    return video_capture.get(cv2.CAP_PROP_FRAME_WIDTH), video_capture.get(
        cv2.CAP_PROP_FRAME_HEIGHT
    )


def get_frame_display_time(video_capture: cv2.VideoCapture) -> int:
    """Returns the number of milliseconds each frame of a VideoCapture should be displayed.

    Args:
        video_capture: an opencv video capture file.

    Returns:
        The number of milliseconds each frame should be displayed for.
    """
    frames_per_second = video_capture.get(cv2.CAP_PROP_FPS)
    return floor(1000 / frames_per_second)


def is_window_open(title: str) -> bool:
    """Checks to see if a window with the specified title is open."""

    # all attempts to get a window property return -1 if the window is closed
    return cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) <= 1


def main(video_path: str, title: str) -> NoReturn:
    """Displays a video at half size until it is complete or the 'q' key is pressed.

    Args:
        video_path: the location of the video to be displayed
        title: the title to display in the video window
    """

    video_capture = open_video(video_path)
    width, height = get_frame_dimensions(video_capture)
    wait_time = get_frame_display_time(video_capture)

    person_dataX = [0]
    person_dataY = [0]
    
    try:
        # read the first frame
        success, frame = video_capture.read()

        # create the window
        cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)

#		grb the json
        json_path = "resources/video_2_detections.json"
        frame_data = None
        with open(json_path, "r") as f:
                frame_data = json.load(f)

        person_index = 0
        object_index = 1
        # run whilst there are frames and the window is still open
        while success and is_window_open(title):
            # shrink it
            smaller_image = cv2.resize(frame, (floor(width // 2), floor(height // 2)))

            # display it
            cv2.imshow(title, smaller_image)

            # test for quit key
            if cv2.waitKey(wait_time) == ord("q"):
                break

            # read the next frame
            frame_index = int(video_capture.get(cv2.CAP_PROP_POS_FRAMES))
            str_frame_index = str(frame_index)
            success, frame = video_capture.read()
			
            #identifiers in the json file
            bounding_boxes = frame_data[str_frame_index]["bounding boxes"]
            detect_scores = frame_data[str_frame_index]["detection scores"]
            detected_classes = frame_data[str_frame_index]["detected classes"]
            
            #Different classes within
            options_class = ["car", "bicycle", "person", "truck"]
            colors = [(255,0,0), (0,255,0), (0,0,255), (138,12,200)]
            
            #iterating through objects in frame
            for i in range(len(bounding_boxes)): 
                bounding = bounding_boxes[i]
            
            #calculating central point of bounding box
            bounding_centerX = int(bounding[0] + (bounding[2]/2))
            bounding_centerY = int(bounding[1] + (bounding[3]/2))
            
            #inspection (debugging) point
            #if(frame_index == 100):
                #import pdb; pdb.set_trace()
            
            #iterating through the objects in frame
            for j in range(len(detected_classes)):
                classes = detected_classes[j]
                
                #if the class of object found matches "person"
                if(classes == options_class[2]):
                    color = colors[1]
                    #drawing bounding box
                    frame = cv2.rectangle(frame, (bounding[0], bounding[1]), (bounding[0]+bounding[2], bounding[1]+bounding[3]),  color, 1)

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    objectName = "OBJECT: %s" % object_index
                    #naming the bounding box
                    frame = cv2.putText(frame, objectName, (bounding[0], bounding[1]), font, 1, color, 2, cv2.LINE_AA)
                    #Drawing center of bounding box.
                    frame = cv2.circle(frame, (bounding_centerX, bounding_centerY), 5, color, -1)
                    
                    #add data of known people
                    person_dataX.append(bounding_centerX)
                    person_dataY.append(bounding_centerY) 
                    person_index = person_index + 1
                else:
                    #append empty data so index of person_dataN is the same as the frame_index. Could be helpful later
                    person_dataX.append(0)
                    person_dataY.append(0)
            
            #object-2-object variables
            x2 = person_dataX[person_index]
            y2 = person_dataY[person_index]
            x1 = person_dataX[(person_index - 1)]
            y1 = person_dataY[(person_index - 1)]
            magX = abs(x1 - x2)
            magY = abs(y1 - y2)
            #calculating distance between two points
            distance = math.sqrt(magX**2 + magY**2)
            
            #testing to see if object in previous frame is close by
            if(distance > 30):
                object_index += 1
            
            #import pdb; pdb.set_trace()
            #print(distance)
            #print("----")
            #print(object_index)
            
    finally:
        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    VIDEO_PATH = "resources/video_2.mp4"
    main(VIDEO_PATH, "My Video")