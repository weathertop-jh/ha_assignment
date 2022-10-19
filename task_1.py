from math import floor
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
            frame_index = str(int(video_capture.get(cv2.CAP_PROP_POS_FRAMES)))
            success, frame = video_capture.read()
			
            # number of frame in each video
            #key = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            bounding_boxes = frame_data[frame_index]["bounding boxes"]
            detect_scores = frame_data[frame_index]["detection scores"]
            detected_classes = frame_data[frame_index]["detected classes"]
            
            #define class options and colors
            options_class = ["car", "bicycle", "person", "truck"]
            colors = [(255,0,0), (0,255,0), (0,0,255), (138,12,200)]
            
            #Assigning class found 
            for j in range(len(detected_classes)):
                classes = detected_classes[j]
                
                #Assigning color based on name
                for k in range(len(options_class)):
                    if(classes == options_class[k]):
                        color = colors[k]
            
            #Drawing bounding boxes with assigned color
            for i in range(len(bounding_boxes)): 
                bounding = bounding_boxes[i]
                frame = cv2.rectangle(frame, (bounding[0], bounding[1]), (bounding[0] + bounding[2],bounding[1] + bounding[3]),  (color), 2)
						                     
				
    finally:
        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    VIDEO_PATH = "resources/video_2.mp4"
    main(VIDEO_PATH, "My Video")
	
	
	
	
	
	
	
	
	