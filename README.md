# 🪔 Digital Diwali Lakshmi Pujan (Python + Streamlit)

*Conceptualized and Developed by **CA Alok Sethi** using Claude*  
[LinkedIn](https://www.linkedin.com/in/caaloksethi) · [YouTube @aloksethisir](https://www.youtube.com/@aloksethisir) · [Instagram @caaloksethi](https://www.instagram.com/caaloksethi)

An interactive, camera-controlled Lakshmi Pujan. You can pick up a candle and light the diyas
on a brass thali, offer flowers to Lakshmi ji, perform the aarti by circling the thali, ring
the ghanti and play your own bhajan, all with hand gestures in front of your webcam.

## Quick start (Windows)

**Option A: one click**
Double-click `run_puja.bat`. The first run creates a virtual environment and installs
Streamlit and Pillow. After that it opens the app in your browser.

**Option B: manual**
```bat
git clone https://github.com/aloksethi-ai/digital-diwali-lakshmi-pujan.git
cd digital-diwali-lakshmi-pujan
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Open **http://localhost:8501** (browsers only allow camera access on `localhost` or HTTPS).

## Gestures

| Action | Gesture |
|---|---|
| Move the golden cursor | Move your hand (the point between your thumb and index finger is the cursor) |
| Pick up / hold | **Pinch**: touch your thumb and index finger together |
| Drop / place | Open your fingers |
| Touch the thali | Hover your hand over it |
| Light a diya | Hold the candle and bring its flame to the diya's wick |
| Offer a flower | Pinch in the basket, carry the flower to Lakshmi ji, open your fingers |
| Offer the lotus garland | Pinch the कमल माला hanging on the right and drop it on Lakshmi ji |
| Offer bhog | Pinch a motichoor ladoo or kaju katli from the silver mithai thali and drop it on Lakshmi ji |
| Offer to Dhan Lakshmi | Click / pinch the Dhan thali (gold & silver coins, ₹ and $ bundles); each tap grows the stacks and showers wealth |
| Aarti | Pinch and hold the thali, then move it in full circles around Lakshmi ji |
| Play / pause the bhajan | Hover over the golden ▶ button for 1 second, or pinch it |
| Ring the ghanti | Wave your hand through the bell |

You can use both hands at once, for example the candle in one hand and the thali in the other.
**Mouse / touch mode** works without a camera: press and hold to pick up, release to drop.

## Your own Lakshmi ji image and bhajan
* Upload them from the sidebar, **or**
* save them as `assets/lakshmi.jpg` (or .png/.webp) and `assets/bhajan.mp3` so they load automatically every time.

Use an image and audio you have the right to use, e.g. your own photo of the family murti or a
licensed or royalty-free bhajan recording.

## Files
```
digital-diwali-lakshmi-pujan/
├── app.py                 Streamlit app (sidebar, uploads, settings, embeds the stage)
├── assets/
│   └── puja_stage.html    Canvas stage: scene, hand tracking, puja logic, sounds
├── .streamlit/config.toml Theme + upload limits
├── requirements.txt
└── run_puja.bat           Windows one-click launcher
```

## How it works
* **Python / Streamlit** builds the page, validates and resizes the uploaded image (Pillow),
  encodes the image and audio, and passes the settings to the stage as JSON.
* **The stage** is an HTML5 canvas embedded with `streamlit.components.v1.html`. It runs
  **Google MediaPipe Hand Landmarker** (`@mediapipe/tasks-vision` 0.10.14) in the browser and
  tracks 21 points on each hand at about 30 fps. Running the tracker in Python and streaming the
  video back and forth would add too much lag for grabbing and moving things.
* Bell sounds and the fallback ambient drone are synthesised with the Web Audio API, so no sound files are needed.

## Privacy & safety
* The webcam feed is processed **only in your browser**. No frames are recorded, stored or uploaded.
* Internet is needed on first use to download the MediaPipe library (jsDelivr CDN) and the
  hand model (Google storage). Without internet the app automatically falls back to mouse mode.
* User-entered text is JSON-escaped before it is placed in the page (no script injection).

## Troubleshooting
* **Camera not starting:** close Zoom/Teams/other apps using the camera, and allow camera access in the browser's address-bar prompt.
* **Hand not detected:** use front lighting, show your palm, and stay 40–80 cm from the camera.
* **Pinch hard to trigger:** raise *Pinch sensitivity* in the sidebar.
* **No sound:** click the stage once, then press ▶ (browsers block sound until you interact with the page).
* Changing a sidebar setting restarts the stage, so set up first and then begin the puja.
