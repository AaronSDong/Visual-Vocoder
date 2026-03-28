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

def camera():
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FPS, 30)

    mphands = mp.solutions.hands
    hands = mphands.Hands(max_num_hands= 2, min_detection_confidence= 0.2, min_tracking_confidence= 0.2 )
    mpdraw = mp.solutions.drawing_utils

    hand_synth = Wave.Wave(wave_shape='sine')
    hand_synth.play()

    # Debugging
    prev_time = 0

    while True:
        ret, frame = cap.read()

        prev_time = calculate_fps(prev_time, frame)  # FPS counter
        process_hands(frame, hands, mphands, mpdraw, hand_synth)
        # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)  # Grey Scale

        cv.imshow('frame', frame)
        if cv.waitKey(1) == ord('q'):  # Exit key
            break

    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

def process_hands(frame, hands, mphands, mpdraw, wave):
    result = hands.process(frame)
    if not result.multi_hand_landmarks: return

    for handLm in result.multi_hand_landmarks:
        process_nodes(handLm, wave)
        mpdraw.draw_landmarks(frame, handLm, mphands.HAND_CONNECTIONS,
                              mpdraw.DrawingSpec(color=(255, 255, 255), circle_radius=3,
                                                 thickness=cv.FILLED),
                              mpdraw.DrawingSpec(color=(255, 255, 255), thickness=1))

def process_nodes(handLm, wave):
    # Nodes values represent the type of value they store, or if a float, their note frequency
    left_nodes = {

    }

    right_nodes = {

    }

    handiness = handLm.multi_handedness
    node_list = left_nodes if handiness == "Left" else right_nodes
    octave = 2

    for i in handLm:
        if node_list[i] == 'palm': adjust_palm_values(handLm[0], wave)
        elif node_list[i] == 'thumb': adjust_octave(handLm, wave)
        elif type(node_list[i]) == int: adjust_note(node_list[i], octave, wave)

def adjust_palm_values(node, wave):
    wrist_l_y = node.y
    freq = (1 - wrist_l_y) * 2000
    wave.set_target_frequency(freq)

def adjust_octave(handLm, wave):
    pass

def adjust_note(freq, octave, wave):
    pass

def main():
    camera()

if __name__ == '__main__':
    main()