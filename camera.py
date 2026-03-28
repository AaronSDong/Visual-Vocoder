import cv2 as cv
import time
import mediapipe as mp
import Wave

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf')

def calculate_fps(prev_time, frame):
    # Calculate FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    # Display FPS on the frame
    fps_text = f"FPS: {fps:.0f}"
    cv.putText(frame, fps_text, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return prev_time

def create_synths():
    wave_list = []
    for i in range(2):  # change to 8 later
        wave_list.append(Wave.Wave(wave_shape='sine', t=None))  # Automatic playing is placeholder

    return wave_list

def camera():
    mirrored_camera = True
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FPS, 30)

    mphands = mp.solutions.hands
    hands = mphands.Hands(max_num_hands= 2, min_detection_confidence= 0.2, min_tracking_confidence= 0.2 )
    mpdraw = mp.solutions.drawing_utils

    wave_list = create_synths()

    # Debugging
    prev_time = 0

    while True:
        ret, frame = cap.read()

        if mirrored_camera: frame = cv.flip(frame, 1)
        prev_time = calculate_fps(prev_time, frame)  # FPS counter
        process_hands(frame, hands, mphands, mpdraw, wave_list, mirrored_camera)
        # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)  # Grey Scale

        cv.imshow('frame', frame)
        if cv.waitKey(1) == ord('q'):  # Exit key
            break

    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

def process_hands(frame, hands, mphands, mpdraw, wave_list, mirrored_camera):
    result = hands.process(frame)
    if not result.multi_hand_landmarks: return

    for i in range(len(result.multi_hand_landmarks)):
        handedness_list = result.multi_handedness
        if handedness_list[0].classification[0].index == i or len(handedness_list) == 1:
            handedness = handedness_list[0].classification[0].label
        else:
            handedness = handedness_list[1].classification[0].label
        if not mirrored_camera:  # Swap as the camera is not mirrored
            handedness = 'right' if handedness == 'left' else 'left'

        handLm = result.multi_hand_landmarks[i]
        process_nodes(handLm, wave_list, handedness)
        mpdraw.draw_landmarks(frame, handLm, mphands.HAND_CONNECTIONS,
                              mpdraw.DrawingSpec(color=(255, 255, 255), circle_radius=3,
                                                 thickness=cv.FILLED),
                              mpdraw.DrawingSpec(color=(255, 255, 255), thickness=1))

def process_nodes(handLm, wave_list, handedness):
    node_list = get_nodes(handedness)
    octave = 2

    for i in range(len(handLm.landmark)):
        if node_list[i] == 'palm': adjust_palm_values(handLm.landmark[0], wave_list, handedness)
        elif node_list[i] == 'thumb': adjust_octave(handLm, wave_list)
        elif type(node_list[i]) == int: adjust_note(node_list[i], octave, wave_list)

def adjust_palm_values(node, wave_list, handedness):
    wrist_l_y = node.y
    freq = (1 - wrist_l_y) * 2000

    wave_index = 0 if handedness.lower() == 'left' else 1  # placeholder for now
    #print(wave_index)
    wave_list[wave_index].set_target_frequency(freq)

def adjust_octave(handLm, wave):
    pass

def adjust_note(freq, octave, wave):
    pass

def get_nodes(handedness):
    # Nodes values represent the type of value they store, or if a float, their note frequency
    left_nodes = {
        0: 'palm',
        1: None,
        2: None,
        3: None,
        4: 'thumb',
        5: None,
        6: None,
        7: None,
        8: 12,
        9: None,
        10: None,
        11: None,
        12: 16,
        13: None,
        14: None,
        15: None,
        16: 20,
        17: None,
        18: None,
        19: None,
        20: 8,
    }

    right_nodes = {
        0: 'palm',
        1: None,
        2: None,
        3: None,
        4: 'thumb',
        5: None,
        6: None,
        7: None,
        8: 12,
        9: None,
        10: None,
        11: None,
        12: 16,
        13: None,
        14: None,
        15: None,
        16: 20,
        17: None,
        18: None,
        19: None,
        20: 8,
    }

    return left_nodes if handedness == 'left' else right_nodes

def main():
    camera()

if __name__ == '__main__':
    main()