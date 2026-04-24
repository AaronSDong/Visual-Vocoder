# This file was created by individually creating a vocoder and the camera, then prompting an AI to combine the two
# I have slightly edited this file to fit some style issues or updates

import cv2 as cv
import time
import mediapipe as mp
import threading
import numpy as np
import pyworld as pw
import pyaudio
# from ChorusSettings import ChorusSettings
from SettingsScript import load_settings, getScale
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf')

# --- Vocoder State ---
# Each of the 8 finger slots maps to a frequency; None means that slot is inactive.
# The vocoder blends all active frequencies (or passes through if none active).

class VocoderState:
    def __init__(self):
        self.scale_type = 'major'
        self.key = 'C'
        self.finger_frequencies = getScale(self.scale_type, self.key)

        self.lock = threading.Lock()
        self.active_fingers = set()   # set of finger slot indices (0-7) that are "closed"
        self.volume = 1.0             # 0.0 - 1.0, set by palm height
        self.octave_shift = 0         # integer, same octave logic as before
        self.running = True

        # Chorus (kept for palm x-axis, same as before)
        self.chorus_bypass = True
        self.chorus_hand = 'left'

    def get_target_frequency(self):
        """Average frequency of all active fingers, shifted by octave."""
        with self.lock:
            if not self.active_fingers:
                return None
            freqs = [self.finger_frequencies[i] for i in self.active_fingers]
            base = sum(freqs) / len(freqs)
            return base * (2 ** self.octave_shift)

    def set_finger(self, slot, active: bool):
        with self.lock:
            if active:
                self.active_fingers.add(slot)
            else:
                self.active_fingers.discard(slot)

    def set_volume(self, vol: float):
        with self.lock:
            self.volume = max(0.0, min(1.0, vol))

    def set_octave(self, shift: int):
        with self.lock:
            self.octave_shift = shift

    def get_volume(self):
        with self.lock:
            return self.volume


def vocoder_thread(state: VocoderState):
    """Runs the vocoder in a background thread, reading mic and writing to speaker."""
    sample_rate = 44100
    chunk = 8192
    p = pyaudio.PyAudio()
    input_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate,
                          input=True, frames_per_buffer=chunk)
    output_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate,
                           output=True)

    while state.running:
        raw = input_stream.read(chunk, exception_on_overflow=False)
        audio_np = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
        audio_np = audio_np * 5  # input gain

        rms = np.sqrt(np.mean(audio_np ** 2))
        vol = state.get_volume()

        if rms < 0.005 or vol < 0.01:
            output_stream.write(np.zeros(chunk, dtype=np.float32).tobytes())
            continue

        target_freq = state.get_target_frequency()

        try:
            frequency, spectral_envelope, aperiodicity = pw.wav2world(audio_np, sample_rate)
        except Exception:
            output_stream.write(np.zeros(chunk, dtype=np.float32).tobytes())
            continue

        if target_freq is not None:
            frequency[:] = target_freq   # pin pitch to the finger-controlled frequency
            aperiodicity[:] = 0                    # remove aperiodicity for a cleaner tone

        y = pw.synthesize(frequency, spectral_envelope, aperiodicity, sample_rate,
                          pw.default_frame_period)
        y = (y * vol).astype(np.float32)

        # Pad or trim to expected output length to avoid glitches
        expected = chunk
        if len(y) < expected:
            y = np.pad(y, (0, expected - len(y)))
        else:
            y = y[:expected]

        output_stream.write(y.tobytes())

    input_stream.stop_stream()
    input_stream.close()
    output_stream.stop_stream()
    output_stream.close()
    p.terminate()


# --- Camera / Hand tracking (same structure as before) ---

def calculate_fps(prev_time, frame):
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    fps_text = f"FPS: {fps:.0f}"
    cv.putText(frame, fps_text, (10, 30), cv.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0), 2)
    return prev_time


def camera():
    mirrored_camera = True
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 300)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 360)
    cap.set(cv.CAP_PROP_FPS, 30)

    mphands = mp.solutions.hands
    hands = mphands.Hands(max_num_hands=2, min_detection_confidence=0.4,
                          min_tracking_confidence=0.6, static_image_mode=False)
    mpdraw = mp.solutions.drawing_utils

    settings = load_settings()
    state = VocoderState()
    state.chorus_bypass = settings['chorus_bypass']
    state.chorus_hand = 'left'

    # Start vocoder on a daemon thread
    vt = threading.Thread(target=vocoder_thread, args=(state,), daemon=True)
    vt.start()

    prev_time = 0

    while True:
        _, frame = cap.read()
        if mirrored_camera: frame = cv.flip(frame, 1)
        prev_time = calculate_fps(prev_time, frame)
        cv.putText(frame, 'press q to exit', (10, 50),
                   cv.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0), 2)
        process_hands(frame, hands, mphands, mpdraw, state, mirrored_camera)

        cv.imshow('frame', frame)
        if cv.waitKey(1) == ord('q'):
            break

    state.running = False
    vt.join(timeout=2)
    cap.release()
    cv.destroyAllWindows()

def process_hands(frame, hands, mphands, mpdraw, state: VocoderState, mirrored_camera):
    result = hands.process(frame)
    octave = 0

    if not result.multi_hand_landmarks:
        # No hands visible — silence all fingers
        for slot in range(8):
            state.set_finger(slot, False)
        return

    for i in range(len(result.multi_hand_landmarks)):
        handedness_list = result.multi_handedness
        if handedness_list[0].classification[0].index == i or len(handedness_list) == 1:
            handedness = handedness_list[0].classification[0].label
        else:
            handedness = handedness_list[1].classification[0].label
        if not mirrored_camera:
            handedness = 'right' if handedness == 'left' else 'left'

        handLm = result.multi_hand_landmarks[i]
        process_nodes(frame, handLm, state, handedness)
        octave += adjust_octave(frame, handLm.landmark[4], handLm.landmark[5],
                                state, handedness)

        mpdraw.draw_landmarks(frame, handLm, mphands.HAND_CONNECTIONS,
                              mpdraw.DrawingSpec(color=(255, 255, 255), circle_radius=3,
                                                 thickness=cv.FILLED),
                              mpdraw.DrawingSpec(color=(255, 255, 255), thickness=1))

    # Clamp octave shift to a reasonable range
    state.set_octave(max(-2, min(2, octave - 1)))


def process_nodes(frame, handLm, state: VocoderState, handedness):
    node_map, wave_map, tolerance_map = get_maps(handedness)

    for i in range(len(handLm.landmark)):
        if node_map[i] == 'palm':
            adjust_palm_values(handLm.landmark[0], state, handedness)
        elif node_map[i] == 'note':
            slot = wave_map[i]
            tolerance = tolerance_map[i]
            closed = finger_is_closed(frame, handLm.landmark[i], handLm.landmark[i - 3],
                                      tolerance)
            state.set_finger(slot, closed)


def adjust_palm_values(palm_landmark, state: VocoderState, handedness):
    vol = (1 - palm_landmark.y) * 2
    if vol > 1:
        vol = 1
    state.set_volume(vol)

    # Chorus logic preserved — you can wire this back up if you re-add chorus processing
    if not state.chorus_bypass and handedness.lower() == state.chorus_hand:
        distance_from_middle = abs(palm_landmark.x - 0.5) * 2
        min_threshold = 0.3
        max_threshold = 0.8
        threshold_range = max_threshold - min_threshold
        if distance_from_middle <= min_threshold:
            bypass = True
        elif distance_from_middle >= max_threshold:
            bypass = False
        else:
            bypass = False
        state.chorus_bypass = bypass


def adjust_note(frame, finger_landmark, target_landmark, state, slot, tolerance):
    """Kept for direct calls if needed; process_nodes calls finger_is_closed directly."""
    closed = finger_is_closed(frame, finger_landmark, target_landmark, tolerance)
    state.set_finger(slot, closed)


def finger_is_closed(frame, finger_landmark, target_landmark, tolerance):
    t0, t1, _ = tolerance
    x0, y0, z0 = finger_landmark.x, finger_landmark.y, finger_landmark.z
    x1, y1, z1 = target_landmark.x, target_landmark.y, target_landmark.z
    z_average = round(abs((z0 + z1) / 2), 4)

    h, w, _ = frame.shape
    cx0, cy0 = int(x0 * w), int(y0 * h)
    cx1, cy1 = int(x1 * w), int(y1 * h)
    radius = int((z_average ** t0) * t1 * min(w, h))

    on_switch = distance(cx0, cy0, cx1, cy1) < radius
    color = (0, 255, 0) if on_switch else (0, 0, 255)
    cv.circle(frame, (cx0, cy0), radius, color, 2)
    return on_switch


def distance(x0, y0, x1, y1):
    return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5


def adjust_octave(frame, finger_landmark, target_landmark, state: VocoderState, handedness):
    _, _, tolerance_map = get_maps(handedness)
    tolerance = list(tolerance_map[4])  # copy so we don't mutate the map
    hand_binary_value = 2 if handedness.lower() == 'left' else 1
    current_octave = state.octave_shift

    if ((handedness.lower() == 'left' and current_octave >= 2) or
            (handedness.lower() == 'right' and current_octave % 2 == 1)):
        tolerance[1] = tolerance[1] * tolerance[2]

    if finger_is_closed(frame, finger_landmark, target_landmark, tolerance):
        return hand_binary_value
    return 0


def get_maps(handedness):
    left_nodes = {
        **{i: None for i in range(21)},
        0: 'palm', 4: 'thumb', 8: 'note', 12: 'note', 16: 'note', 20: 'note'
    }
    right_nodes = {
        **{i: None for i in range(21)},
        0: 'palm', 4: 'thumb', 8: 'note', 12: 'note', 16: 'note', 20: 'note'
    }
    left_waves = {
        **{i: None for i in range(21)},
        8: 0, 12: 1, 16: 2, 20: 3,
    }
    right_waves = {
        **{i: None for i in range(21)},
        8: 7, 12: 6, 16: 5, 20: 4,
    }
    tolerances = {
        **{i: None for i in range(21)},
        4:  [0.35, .30, 1.8],  # thumb
        8:  [0.42, .40, 1.9],  # index
        12: [0.44, .50, 1.7],  # middle
        16: [0.44, .40, 1.8],  # ring
        20: [0.44, .30, 1.7],  # pinky
    }
    if handedness == 'Left':
        return left_nodes, left_waves, tolerances
    else:
        return right_nodes, right_waves, tolerances

def main():
    camera()

if __name__ == '__main__':
    main()