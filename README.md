## Project Notes:
Most of the effort spent on this project was focused on the auditory aspect of it (specifically, the WaveGroup class
and anything deeper inside of it). Much care was used to ensure that audio played would not 'clip,' as these bugs are
very common. Each of the wave classes were written to also operate independently outside of this specific project,
and as such main() functions were written at the bottom of most of them to demonstrate that. Outside the vocoder,
all audio processing was done manually with only the use of pyaudio to play the signals.
Files to look at: 'WaveGroup.py' --> 'Wave.py' --> 'DrySignal.py'

To get an indepth description of the project, please see the 'How To Play' section of my program. In short, curling your
fingers will result in the synth playing a tone, with hand movements controlling certain parameters. To see how fingers
are detected, please see 'Camera.py,' specifically from line 60 down.

All UI elements are contained within 'main.py'

Music, art, and sfx assets were created by me.

## AI Usage:
The following is a list of things that I did not do/received significant help from an online source
(any AI used was Claude):

- FPS and Overlay function is entirely taken from AI
- Initializing objects that are not mine (likely taken from documentation)
- Fundamental infrastructure regarding OpenCV, MediaPipe, and PyAudio (documentation / AI)
- Implementation of mpdraw.draw_landmarks (edited from documentation)
- Misc. organization ideas, such as using unpacking to initialize dictionaries or using getattr (AI)
- Many 'busy work' dictionaries were created by AI (scales and note values are often information that is hard/tedious to 
calculate, or at worst are arbitrarily determined and require online resources regardless)
- Suppressing error messages from outdated modules (AI)
- Occasional refactoring edits (AI)
- Partial edits to vocoder (AI)
- Combination of Vocoder and Camera (AI)
- Settings File (AI)
- Mono and Change Wave menu button (AI, prompted to copy current human-made code)
- Reset Default settings function (AI)
- Partially helped with custom wave editor (AI)

## Font:
For visual purposes, download the Pixelated Elegance font. You can do so by opening the .ttf file in the file directory
and clicking install, or using this link:
https://www.fontspace.com/pixelated-elegance-font-f126145
