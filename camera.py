import numpy as np
import cv2 as cv
import time
import mediapipe as mp

def calculate_fps(prev_time, frame):
    # Calculate FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    # Display FPS on the frame
    fps_text = f"FPS: {fps:.0f}"
    cv.putText(frame, fps_text, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return prev_time

def main():
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FPS, 30)

    mphands = mp.solutions.hands
    hands = mphands.Hands(max_num_hands= 2, min_detection_confidence= 0.2, min_tracking_confidence= 0.2 )
    mpdraw = mp.solutions.drawing_utils

    prev_time = 0

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()


        # DEBUGGING fps
        prev_time = calculate_fps(prev_time, frame)

        result = hands.process(frame)
        if result.multi_hand_landmarks:
            for handLm in result.multi_hand_landmarks:
                mpdraw.draw_landmarks(frame, handLm, mphands.HAND_CONNECTIONS,
                                      mpdraw.DrawingSpec(color=(255, 255, 255), circle_radius=3,
                                                         thickness=cv.FILLED),
                                      mpdraw.DrawingSpec(color=(255, 255, 255), thickness=1)
                                      )

                # DEBUGGING
                # for id, lm in enumerate(handLm.landmark):
                #     h, w, _ = frame.shape
                #     cx, cy = int(lm.x * w), int(lm.y * h)
                #
                #     cv.circle(frame, (cx, cy), 5, (0, 255, 0), cv.FILLED)
                #     if id == 4:
                #         pass
                #         Tx, Ty = cx, cy
                #         cv.circle(frame, (Tx, Ty), 6, (255, 0, 0), cv.FILLED)
                #     if id == 8:
                #         pass
                #         cv.circle(frame, (cx, cy), 6, (255, 0, 0), cv.FILLED)
                #         cv.line(frame, (cx, cy), (Tx, Ty), (255, 0, 0), 5 )

        # Grey Scale (maybe reduce lag?)
        #frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Display
        cv.imshow('frame', frame)

        # Exit key
        if cv.waitKey(1) == ord('q'):
            break


    # When everything done, release the capture
    cap.release()
    cv.destroyAllWindows()

main()