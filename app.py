"""
Digital Diwali Lakshmi Pujan — a Streamlit app.

Python / Streamlit handles the app shell: uploads (Lakshmi ji image, bhajan audio),
puja settings and instructions. The interactive puja stage is an HTML5 canvas
embedded with streamlit.components.v1.html. It reads your webcam and tracks your
hands with Google MediaPipe *inside the browser*, so the camera feed never
leaves your computer.

Run:  streamlit run app.py
"""
from __future__ import annotations

import base64
import io
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

APP_DIR = Path(__file__).resolve().parent
ASSETS = APP_DIR / "assets"
STAGE_TEMPLATE = ASSETS / "puja_stage.html"
CONFIG_MARKER = "/*__PUJA_CONFIG__*/"

IMAGE_EXTS = ("png", "jpg", "jpeg", "webp")
AUDIO_EXTS = ("mp3", "wav", "ogg", "m4a", "aac")
AUDIO_MIME = {"mp3": "audio/mpeg", "wav": "audio/wav", "ogg": "audio/ogg",
              "m4a": "audio/mp4", "aac": "audio/aac"}
MAX_AUDIO_MB = 60          # keep the embedded page light enough for the browser

st.set_page_config(page_title="Digital Lakshmi Pujan", page_icon="🪔",
                   layout="wide", initial_sidebar_state="expanded")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def image_to_data_url(raw: bytes, max_side: int = 900) -> str:
    """Validate the image, fix phone rotation, shrink it, return a data URL."""
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img)
    img.thumbnail((max_side, max_side))
    has_alpha = img.mode in ("RGBA", "LA") or "transparency" in img.info
    buf = io.BytesIO()
    if has_alpha:
        img.convert("RGBA").save(buf, format="PNG", optimize=True)
        mime = "image/png"
    else:
        img.convert("RGB").save(buf, format="JPEG", quality=90)
        mime = "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode()}"


@st.cache_data(show_spinner=False)
def audio_to_data_url(raw: bytes, ext: str) -> str:
    mime = AUDIO_MIME.get(ext.lower(), "audio/mpeg")
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def find_default(stem: str, exts: tuple[str, ...]) -> Path | None:
    """Return assets/<stem>.<ext> if the user dropped a default file there."""
    for ext in exts:
        for candidate in (ASSETS / f"{stem}.{ext}", ASSETS / f"{stem}.{ext.upper()}"):
            if candidate.is_file():
                return candidate
    return None


def build_stage_html(cfg: dict) -> str:
    template = STAGE_TEMPLATE.read_text(encoding="utf-8")
    # Escape "<" so no user-supplied text (e.g. a name) can close the <script> tag.
    payload = json.dumps(cfg, ensure_ascii=False).replace("<", "\\u003c")
    return template.replace(CONFIG_MARKER, f"const CONFIG = {payload};", 1)


# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
      .stApp { background: radial-gradient(ellipse at top, #4a0d0b 0%, #1a0404 55%, #0e0202 100%); }
      [data-testid="stSidebar"] { background: linear-gradient(180deg, #3b0a0a, #1f0505); border-right: 1px solid #b8862b; }
      [data-testid="stSidebar"] * { color: #ffe9b0 !important; }
      .block-container { padding-top: 3.2rem; padding-bottom: 0.5rem; max-width: 1500px; }
      .puja-title { text-align:center; font-family: 'Georgia', serif; color:#ffd36b;
                    text-shadow: 0 0 16px rgba(255,180,40,.7); font-size: 2.1rem; margin: 0; }
      .puja-sub { text-align:center; color:#ffe9b0; opacity:.85; letter-spacing:2px; margin: 0 0 .15rem; font-size:.95rem; }
      .puja-credit { text-align:center; color:#ffd36b; font-size:.85rem; letter-spacing:.5px; margin: 0 0 .6rem;
                     font-style: italic; opacity:.95; }
      .stExpander { border: 1px solid #8a5a10 !important; border-radius: 10px; background: rgba(40,6,3,.55); }
      .stExpander * { color: #ffe9b0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Sidebar — puja samagri (materials) and settings
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🪔 Puja Samagri")

    img_file = st.file_uploader("Lakshmi ji image", type=list(IMAGE_EXTS),
                                help="A portrait image works best. It is shown in full and never cropped.")
    audio_file = st.file_uploader("Lakshmi Pujan bhajan / aarti (audio)", type=list(AUDIO_EXTS),
                                  help="MP3 is the most widely supported format.")
    st.caption("Tip: save files as `assets/lakshmi.jpg` and `assets/bhajan.mp3` "
               "and they will load automatically every time.")

    devotee = st.text_input("Devotee / family name (optional)", max_chars=60,
                            placeholder="e.g. Sethi Parivar")

    st.markdown("## ⚙️ Puja Settings")
    diyas = st.select_slider("Number of diyas on the thali", options=[1, 3, 5, 7, 9, 11], value=5)
    flowers_needed = st.slider("Flowers to offer", 1, 11, 5)
    sweets_needed = st.slider("Sweets to offer as bhog", 1, 10, 3, help="Motichoor ladoo / kaju katli placed for Lakshmi ji")
    aarti_rounds = st.slider("Aarti rounds", 1, 7, 3, help="Full circles of the thali around Lakshmi ji")

    st.markdown("## ✋ Camera & Hand Tracking")
    show_cam = st.toggle("Show camera preview (top-right)", value=True)
    cam_bg = st.toggle("Show me faintly in the background", value=False)
    skeleton = st.toggle("Draw my hand on the stage", value=True)
    mirror = st.toggle("Mirror view (like a selfie)", value=True)
    pinch = st.slider("Pinch sensitivity", 0.20, 0.60, 0.35, 0.01,
                      help="Higher = easier to trigger a pinch. Increase it if grabbing feels hard.")
    smooth = st.slider("Hand smoothing", 0.15, 0.90, 0.45, 0.05,
                       help="Lower = smoother but slower cursor; higher = snappier.")

    st.markdown("## 🔊 Sound")
    sfx = st.toggle("Temple bell sound effects", value=True)
    loop = st.toggle("Loop the bhajan", value=True)
    stage_height = st.slider("Stage height (px)", 520, 1000, 760, 20)

# --------------------------------------------------------------------------
# Resolve media (uploaded files take priority over defaults in /assets)
# --------------------------------------------------------------------------
lakshmi_url, audio_url, audio_name = None, None, ""

if img_file is not None:
    try:
        lakshmi_url = image_to_data_url(img_file.getvalue())
    except Exception:
        st.sidebar.error("That image could not be read. Please upload a valid PNG / JPG / WEBP file.")
elif (p := find_default("lakshmi", IMAGE_EXTS)) is not None:
    try:
        lakshmi_url = image_to_data_url(p.read_bytes())
    except Exception:
        st.sidebar.warning(f"Could not read {p.name}.")

if audio_file is not None:
    size_mb = audio_file.size / (1024 * 1024)
    if size_mb > MAX_AUDIO_MB:
        st.sidebar.error(f"Audio is {size_mb:.0f} MB. Please use a file under {MAX_AUDIO_MB} MB (an MP3 is usually 3–10 MB).")
    else:
        ext = audio_file.name.rsplit(".", 1)[-1]
        audio_url = audio_to_data_url(audio_file.getvalue(), ext)
        audio_name = audio_file.name
elif (p := find_default("bhajan", AUDIO_EXTS)) is not None:
    if p.stat().st_size <= MAX_AUDIO_MB * 1024 * 1024:
        audio_url = audio_to_data_url(p.read_bytes(), p.suffix.lstrip("."))
        audio_name = p.name

# --------------------------------------------------------------------------
# Main page
# --------------------------------------------------------------------------
st.markdown('<p class="puja-title">॥ श्री महालक्ष्मी पूजन ॥</p>', unsafe_allow_html=True)
st.markdown('<p class="puja-sub">DIGITAL DIWALI PUJA • शुभ दीपावली</p>', unsafe_allow_html=True)
st.markdown('<p class="puja-credit">Conceptualized and Developed by <b>CA Alok Sethi</b> using Claude</p>',
            unsafe_allow_html=True)

if not STAGE_TEMPLATE.is_file():
    st.error(f"Missing file: {STAGE_TEMPLATE}. Keep the 'assets' folder next to app.py.")
    st.stop()

config = {
    "lakshmi": lakshmi_url,
    "audio": audio_url,
    "audioName": audio_name,
    "name": devotee.strip(),
    "diyas": int(diyas),
    "flowersNeeded": int(flowers_needed),
    "sweetsNeeded": int(sweets_needed),
    "aartiRounds": int(aarti_rounds),
    "pinch": float(pinch),
    "smooth": float(smooth),
    "showCam": bool(show_cam),
    "camBg": bool(cam_bg),
    "skeleton": bool(skeleton),
    "mirror": bool(mirror),
    "sfx": bool(sfx),
    "loop": bool(loop),
}

components.html(build_stage_html(config), height=stage_height, scrolling=False)

st.caption("ℹ️ Changing a sidebar setting reloads the stage and restarts the puja, so set things up first, then begin.")

c1, c2 = st.columns(2)
with c1:
    with st.expander("🙏 How to perform the digital puja", expanded=False):
        st.markdown(
            f"""
1. Click **📷 Begin Puja with Camera** and allow camera access.
2. **Touch the thali** with your hand (just hover over it).
3. **Light the diyas.** Pinch (thumb + index finger) on the 🕯️ candle, carry its flame to each of the **{diyas}** diyas, then open your fingers to put it back.
4. **Offer flowers.** Pinch inside the flower basket, carry the flower to Lakshmi ji and open your fingers to place it. Offer **{flowers_needed}** flowers.
5. **Lotus garland (कमल माला).** Pinch the garland hanging on the right and drop it on Lakshmi ji; it drapes across the centre of her image.
6. **Bhog.** Pinch a motichoor ladoo or kaju katli from the silver mithai thali and offer **{sweets_needed}** sweets to Lakshmi ji; they go onto the bhog plate.
7. **Offer to Dhan Lakshmi.** Click / pinch the Dhan thali (gold & silver coins, ₹ and $ bundles) on the left. Every tap grows the coin stacks and note bundles and showers wealth on Maa Lakshmi.
8. **Aarti.** Pinch and hold the thali, then move your hand in **{aarti_rounds}** full circles around Lakshmi ji.
9. **Bhajan.** Hover over the golden ▶ button for one second (or pinch it), or use the top bar.
10. Wave your hand through the 🔔 **ghanti** to ring it at any time.

You can use **both hands**, e.g. hold the candle in one hand and the thali in the other.
No camera? Use **Mouse / Touch only**: press and hold to pick up, release to drop.
            """
        )
with c2:
    with st.expander("🛠️ Troubleshooting", expanded=False):
        st.markdown(
            """
- **No camera prompt / black preview:** open the app at `http://localhost:8501` (browsers only allow cameras on localhost or HTTPS) and check that no other app (Zoom, Teams) is using the camera.
- **Hand not detected:** use good front lighting, keep your hand 40–80 cm from the camera, and show your palm.
- **Pinch not registering:** move the *Pinch sensitivity* slider to the right.
- **Tracker failed to load:** hand tracking downloads Google MediaPipe from a CDN the first time, so an internet connection is needed. Mouse mode works offline.
- **No sound:** click anywhere on the stage once (browsers block audio until you interact), then press ▶.
            """
        )

st.caption("Privacy: the webcam is processed only in your browser. No video, image or audio is sent to any server "
           "other than this local Streamlit app.")
