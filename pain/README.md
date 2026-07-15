# Face + Hand Recognition

A Python project using OpenCV, MediaPipe, and face_recognition to detect and recognize a specific face, along with real-time hand landmark tracking, via webcam.

## Features
- Recognizes a known face from a reference photo
- Tracks hand landmarks in real time
- Draws bounding boxes and labels on detected faces/hands

## Setup

**Requirements:** Python 3.11 (newer versions may cause dependency conflicts with dlib/mediapipe)

```bash
python -m venv venv
venv\Scripts\activate
pip install opencv-python
pip install "numpy<2"
pip install mediapipe==0.10.9
pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp311-cp311-win_amd64.whl
pip install face_recognition --no-deps
pip install Pillow Click
pip install --no-cache-dir git+https://github.com/ageitgey/face_recognition_models
```

## Usage

Place a clear front-facing photo of yourself as `me2.jpg` in the project folder, then run:

```bash
python welcome.py
```

Press `q` to quit the webcam window.

Also this was striaght hell to run, it is NEEDED to run an older version of python, using 3.11 and after install make sure u switch in vs code, also it could be needed to start a fresh folder outside of onedrive, a fresh venv and older version of specific modules.

MORE PROCESS 
1. Your Python environment was corrupted
Python installations were conflicting.

Microsoft Store alias was interfering.

You rebuilt Python cleanly.

You created a fresh venv inside FOLDER1.

2. Installed heavy CV libraries
Installed OpenCV (cv2)

Installed MediaPipe

Installed face_recognition

Installed dlib (this became the main source of pain)

Installed NumPy

3. GitHub setup
You accidentally committed your venv.

We reset the commit.

Added a .gitignore to exclude venv.

Re‑committed only your actual code.

4. Yellow import warnings in VS Code
VS Code wasn’t using your venv interpreter.

You switched to the correct interpreter.

Installed optional type stubs.

Warnings were harmless — runtime was fine.

5. First runtime crash: “Unsupported image type”
Your reference image (me.jpg) loaded fine.

But face_recognition couldn’t detect a face.

The error message was misleading.

We validated the image shape: (2065, 1549, 3) → RGB and valid.

The real issue: no detectable face.

6. You took a new picture (me2.jpg)
Still failed.

Downscaling didn’t help.

CNN model didn’t help.

HOG detector didn’t help.

This told us something deeper was wrong.

7. Discovery: Your dlib wheel was broken
Both detectors failed with the same error:

Code
Unsupported image type
Even though the image was valid.

This meant:

Your dlib build had nonfunctional face detectors.
This is common with certain Christoph Gohlke wheels.

8. Attempted reinstall — “Failed to build dlib wheel”
PyPI tried to compile dlib from source.

Windows cannot compile dlib without full Visual Studio + CMake.

Build failed (expected).

9. Final fix: Installed a working precompiled dlib wheel
You installed the correct wheel for:

Windows 11

Python 3.11

64‑bit

AVX2 CPU

This restored:

HOG face detector

CNN face detector

face_recognition functionality

10. Your script finally worked
Reference face encoded successfully.

Webcam face recognition worked.

MediaPipe hand tracking worked.

No more “unsupported image type” errors.

Full pipeline operational.

11. Final code cleanup
Added safety checks.

Switched to CNN when needed.

Ensured stable runtime.

Summary of the journey
You solved:

Python environment corruption

venv isolation

GitHub commit mistakes

VS Code interpreter mismatch

dlib wheel incompatibility

face detection failures

image validation

detector fallback logic

final working CV pipeline

This was a full-stack debugging journey across:

Python

Windows

dlib

OpenCV

MediaPipe

face_recognition

Git

VS Code

And you got it working cleanly.

If you want, I can also generate:

a polished README

a troubleshooting guide

a “lessons learned” document

a setup guide for future projects

Just tell me what you want next.