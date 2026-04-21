import cv2 as cv
import time
import mediapipe as mp
import WaveGroup
from ChorusSettings import ChorusSettings
from SettingsScript import load_settings, get_key, get_key_index

import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf')  # AI
TEXT_COLOR = (199, 66, 193)

def camera():
    prev_time = 0  # To calculate FPS
    mirrored_camera = True
    cap = cv.VideoCapture(0)  # this is from documentation
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 900)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv.CAP_PROP_FPS, 30)

    mphands = mp.solutions.hands  # this chunk is taken from documentation (mostly)
    hands = mphands.Hands(max_num_hands=2, min_detection_confidence=0.4, min_tracking_confidence=0.6,
                          static_image_mode=False)
    mpdraw = mp.solutions.drawing_utils

    settings = load_settings()
    mono = True if settings['enable_mono'] == 'True' else False
    chorus_bypass = True if settings['chorus_bypass'] == 'True' else False
    chorus = ChorusSettings(bypass=chorus_bypass, delay=settings['chorus_delay'],
                            depth=settings['chorus_depth'], speed=settings['chorus_speed'],
                            dry_wet=settings['chorus_dry_wet'])
    wave_list = WaveGroup.WaveGroup(wave_shape=settings['wave_shape'], mono=mono,
                                    scale=settings['scale'], key=settings['key'],
                                    max_vol=0, chorus=chorus)

    while True:
        _, frame = cap.read()  # documentation

        if mirrored_camera: frame = cv.flip(frame, 1)
        process_hands(frame, hands, mphands, mpdraw, wave_list, mirrored_camera)
        frame, prev_time = draw_ui(wave_list, frame, prev_time)

        cv.imshow('frame', frame)
        if cv.waitKey(1) == ord('q'):  # Exit key, AI
            break

    # When everything done, release the capture (AI)
    cap.release()
    cv.destroyAllWindows()
    wave_list.stop_all()

def draw_ui(wave_list, frame, prev_time):
    # UI background
    overlay_image(frame, 'Assets\\Button Background.png', (300, 150))
    cv.putText(frame, '----Press q to exit----', (40, 32),
               cv.FONT_HERSHEY_SIMPLEX, .5, TEXT_COLOR, 1)

    # Volume elements
    vol_left  = wave_list.vol_left
    vol_right = wave_list.vol_right
    cv.putText(frame, f'Left Volume = {vol_left*100:.1f}%',   (25, 50),
               cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)
    cv.putText(frame, f'Right Volume = {vol_right*100:.1f}%', (25, 65),
               cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)

    # Chorus elements
    chorus = wave_list.chorus
    if chorus.bypass:
        cv.putText(frame, f'Chorus Delay: BYPASSED',   (145, 50),
                   cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)
        cv.putText(frame, f'Chorus Depth: BYPASSED',   (145, 65),
                   cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)
        cv.putText(frame, f'Chorus Speed: BYPASSED',   (145, 80),
                   cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)
        cv.putText(frame, f'Chorus Dry-Wet: BYPASSED', (145, 95),
                   cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)
    else:
        cv.putText(frame, f'Chorus Delay: {chorus.delay_ms:.1f}ms',     (145, 50),
                   cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)
        cv.putText(frame, f'Chorus Depth: {chorus.depth_ms:.1f}ms',     (145, 65),
                   cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)
        cv.putText(frame, f'Chorus Speed: {chorus.speed_hz:.1f}Hz',     (145, 80),
                   cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)
        cv.putText(frame, f'Chorus Dry-Wet: {chorus.dry_wet*100:.1f}%', (145, 95),
                   cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)

    # Notes played
    active_wave_indices = []
    for i in range(len(wave_list.active_waves)):
        if wave_list.active_waves[i] != 0: active_wave_indices.append(i)

    # Grab frequencies in the chromatic scale of the key
    settings = load_settings()
    frequencies_in_C = [256.0, 273.07, 288.0, 307.2, 320.0, 341.33,
                        364.44, 384.0, 409.6, 426.67, 455.11, 480.0, 512.0]  # C4=256 just intonation (AI)
    key_shift = get_key_index(settings['key'])
    freq_shift = 2 ** (key_shift / 12)
    frequencies = [f * freq_shift for f in frequencies_in_C]

    # Turn the list into a range from C4 to C5 (256 to 512 Hz)
    frequencies_played = [float(wave_list.scale[i]) for i in active_wave_indices]
    for i in range(len(frequencies_played)):
        while not frequencies_played[i] <= frequencies[-1]: frequencies_played[i] = frequencies_played[i] / 2
        while not frequencies_played[i] >= frequencies[0]:  frequencies_played[i] = frequencies_played[i] * 2

    # Grab the notes played
    notes_played = ''
    for frequency in frequencies_played:
        for i in range(len(frequencies)):
            if abs(frequency - frequencies[i]) <= 2:
                note = get_key((i + key_shift) % 12)
                notes_played += f'{note}, '
                break
    notes_played = notes_played[:-2]

    cv.putText(frame, f'Notes playing: {notes_played}', (25, 120),
               cv.FONT_HERSHEY_SIMPLEX, .3, TEXT_COLOR, 1)

    prev_time = calculate_fps(prev_time, frame)
    return frame, prev_time

def calculate_fps(prev_time, frame):  # AI
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    fps_text = f"FPS: {fps:.0f}"
    cv.putText(frame, fps_text, (860, 20), cv.FONT_HERSHEY_SIMPLEX, .8, TEXT_COLOR, 2)
    return prev_time


def overlay_image(frame, overlay_path, size=(60, 60)):  # AI
    overlay = cv.imread(overlay_path, cv.IMREAD_UNCHANGED)
    overlay = cv.resize(overlay, size)
    h, w = overlay.shape[:2]

    # Handle transparency (PNG with alpha channel)
    if overlay.shape[2] == 4:
        alpha = overlay[:, :, 3:] / 255.0
        overlay_rgb = overlay[:, :, :3]
        frame[:h, :w] = (alpha * overlay_rgb + (1 - alpha) * frame[:h, :w]).astype('uint8')
    else:
        frame[:h, :w] = overlay

def process_hands(frame, hands, mphands, mpdraw, wave_list, mirrored_camera):
    result = hands.process(frame)
    octave = 0
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
        process_nodes(frame, handLm, wave_list, handedness)
        octave += adjust_octave(frame, handLm.landmark[4], handLm.landmark[5], wave_list, handedness)

        # Documentation
        mpdraw.draw_landmarks(frame, handLm, mphands.HAND_CONNECTIONS,
                              mpdraw.DrawingSpec(color=(255, 255, 255), circle_radius=3,
                                                 thickness=cv.FILLED),
                              mpdraw.DrawingSpec(color=(255, 255, 255), thickness=1))
    wave_list.octave_set_attempt(octave)

def process_nodes(frame, handLm, wave_list, handedness):
    node_map, wave_map, tolerance_map = get_maps(handedness)

    for i in range(len(handLm.landmark)):
        wave_num = wave_map[i]
        tolerance = tolerance_map[i]

        if node_map[i] == 'palm': adjust_palm_values(handLm.landmark[0], wave_list, handedness)
        elif node_map[i] == 'note': adjust_note(frame, handLm.landmark[i], handLm.landmark[i-3], wave_list,
                                                wave_num, tolerance)

def adjust_palm_values(palm_landmark, wave_list, handedness):
    vol = (1 - palm_landmark.y) * 2
    if vol > 1: vol = 1
    wave_list.set_vol_all(vol, channel=handedness)

    if not wave_list.chorus_bypass and handedness.lower() == wave_list.chorus_hand:
        # These values should be read from a file
        bypass = False
        max_delay = 20
        max_depth = 5
        max_speed = .4
        max_dry_wet = .5

        distance_from_middle = abs(palm_landmark.x -.5) * 2
        # normalize the values to fit in what would have been .3-.8
        min_threshold = .3
        max_threshold = .8
        threshold_range = max_threshold - min_threshold
        if distance_from_middle <= min_threshold:
            multiplier = 0
            max_speed = 1  # prevent crashing
            bypass = True
        elif distance_from_middle >= max_threshold:
            multiplier = 1
        else:
            multiplier = (distance_from_middle - min_threshold) / (1 - threshold_range)
            max_speed *= multiplier

        chorus = ChorusSettings(bypass=bypass, delay=max_delay*multiplier, depth=max_depth*multiplier,
                                speed=max_speed, dry_wet=max_dry_wet*multiplier)
        wave_list.update_chorus(chorus)


def adjust_note(frame, finger_landmark, target_landmark,wave_list, wave_num, tolerance):
    if wave_list.active_waves[wave_num]: tolerance[1] = tolerance[1]*tolerance[2]  # increase range to turn off note

    if finger_is_closed(frame, finger_landmark, target_landmark, tolerance):
        if wave_list.active_waves[wave_num]:
            wave_list.active_waves[wave_num] = 3
            return
        wave_list.play_wave(wave_num, None, max_vol=0)

    elif wave_list.active_waves[wave_num]:
        wave_list.deactivate_wave_attempt(wave_num)

def finger_is_closed(frame, finger_landmark, target_landmark, tolerance):
    t0, t1, _ = tolerance
    x0, y0, z0 = finger_landmark.x, finger_landmark.y, finger_landmark.z
    x1, y1, z1 = target_landmark.x, target_landmark.y, target_landmark.z
    z_average = round(abs((z0 + z1) / 2), 4)

    # Partially taken from AI
    h, w, _ = frame.shape
    cx0, cy0 = int(x0*w), int(y0*h)
    cx1, cy1 = int(x1*w), int(y1*h)
    radius = int((z_average**t0) * t1 * min(w, h))

    # Somewhat arbitrary formula, t0 accounts for distance while t1 is the allotted distance
    on_switch = (distance(cx0, cy0, cx1, cy1)) < radius
    color = (0, 255, 0) if on_switch else (0, 0, 255)
    cv.circle(frame, (cx0, cy0), radius, color, 2)

    return on_switch

def distance(x0, y0, x1, y1):
    return ((x1 - x0)**2 + (y1 - y0)**2)**.5

def adjust_octave(frame, finger_landmark, target_landmark, wave_list, handedness):  # bug where octaves might not get turned off
    _, _, tolerance_map = get_maps(handedness)
    tolerance = tolerance_map[4]  # thumb
    hand_binary_value = 2 if handedness.lower() == 'left' else 1  # thumbs are assigned binary values, left is greater
    current_octave_value = wave_list.octave_shift

    # increase range to turn off note
    if ((handedness.lower() == 'left' and current_octave_value >= 2) or
        (handedness.lower() == 'right' and current_octave_value % 2 == 1)):
        tolerance[1] = tolerance[1] * tolerance[2]

    if finger_is_closed(frame, finger_landmark, target_landmark, tolerance):
        return hand_binary_value
    else:
        return 0

def get_maps(handedness):
    # Nodes values represent the type of value they store, or if a float, their note frequency
    # Idea to initialize lists as None and unpacking key-value pairs was taken from AI
    left_nodes = {
        **{i: None for i in range(21)},
        0: 'palm',
        4: 'thumb',
        8: 'note',
        12: 'note',
        16: 'note',
        20: 'note'
    }

    right_nodes = {
        **{i: None for i in range(21)},
        0: 'palm',
        4: 'thumb',
        8: 'note',
        12: 'note',
        16: 'note',
        20: 'note'
    }

    left_waves = {
        **{i: None for i in range(21)},
        8: 0,
        12: 1,
        16: 2,
        20: 3,
    }

    right_waves = {
        **{i: None for i in range(21)},
        8: 7,
        12: 6,
        16: 5,
        20: 4,
    }

    tolerances = {
        **{i: None for i in range(21)},
        4:  [0.35, .30, 1.6],  # thumb
        8:  [0.42, .40, 1.7],  # index
        12: [0.44, .50, 1.5],  # middle
        16: [0.44, .40, 1.6],  # ring
        20: [0.44, .30, 1.5],  # pinky
    }

    if handedness == 'Left':
        return left_nodes, left_waves, tolerances
    else:
        return right_nodes, right_waves, tolerances

def main():
    camera()

if __name__ == '__main__':
    main()