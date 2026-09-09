"""
stickman_animator.py
Procedural 30-FPS Animated Stickman News Anchor:
- Symmetrical Bottom-Center News Anchor Studio Desk (+1 Size Increase)
- Continuous background news video with Ken Burns zoom & effects
- Dynamic facial expressions: idle smile, speech visemes (talking mouth flaps), blinking, and shocked/wide eyes
- Dynamic hand gestures: resting on desk, pointing up at background news/headline, explaining, and saluting
- Synchronized to Edge-TTS voiceover timestamps and timeline phases
"""

import os
import math
import subprocess
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
BASE_PART_PATH = "assets/stickman_parts/original_trans.png"


def prepare_base_trans():
    """Ensure base transparent cutout exists from user upload or asset."""
    if os.path.exists(BASE_PART_PATH):
        return Image.open(BASE_PART_PATH).convert("RGBA")
    
    src = "assets/stickman.png"
    if not os.path.exists(src):
        src = r"C:\Users\hp\.gemini\antigravity-ide\brain\3ee5cd3f-2453-4676-b3fb-40ba7db77732\.user_uploaded\media_1788950310715.png"
    
    if os.path.exists(src):
        img = Image.open(src).convert("RGBA")
        os.makedirs(os.path.dirname(BASE_PART_PATH), exist_ok=True)
        img.save(BASE_PART_PATH)
        return img
    return None


_CACHED_BASE = None

def get_base_img():
    global _CACHED_BASE
    if _CACHED_BASE is None:
        _CACHED_BASE = prepare_base_trans()
    return _CACHED_BASE.copy() if _CACHED_BASE else None


def render_centered_anchor_frame(
    mouth_state="smile",   # "smile", "open_o", "open_wide", "shocked"
    eye_state="normal",     # "normal", "blink", "wide"
    gesture="idle",         # "idle", "point_up", "explain", "salute"
    target_w=580,
    target_h=620,
    bob_y=0
):
    """
    Renders a centered 30-FPS frame of the stickman seated at the news desk (+1 size scale):
    - User's exact hand-drawn head with dynamic mouth & eyes
    - Symmetrical modern studio news desk in foreground
    - Broadcast studio microphone with 'LIVE' indicator
    - Dynamic gestures synced to speech
    """
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    line_col = (12, 12, 16, 255)
    line_w = 8

    center_x = target_w // 2
    desk_y = 380
    desk_half_w = 260

    # 1. Studio Chair back centered behind stickman
    draw.line([(center_x - 70, 200 + bob_y), (center_x - 70, 440)], fill=(35, 42, 58, 255), width=12)
    draw.line([(center_x + 70, 200 + bob_y), (center_x + 70, 440)], fill=(35, 42, 58, 255), width=12)
    draw.arc([(center_x - 95, 160 + bob_y), (center_x + 95, 230 + bob_y)], 180, 360, fill=(35, 42, 58, 255), width=14)

    # 2. Seated Torso & Pelvis (Centered)
    neck_x, neck_y = center_x, 305 + bob_y
    pelvis_x, pelvis_y = center_x, 450
    draw.line([(neck_x, neck_y), (pelvis_x, pelvis_y)], fill=line_col, width=line_w)

    # 3. Arms & Gestures
    shoulder_y = neck_y + 18
    shoulder_offset = 12

    if gesture == "point_up":
        # Left arm resting on desk
        draw.line([(neck_x - shoulder_offset, shoulder_y), (center_x - 65, desk_y + 12), (center_x - 110, desk_y + 28)], fill=line_col, width=line_w)
        draw.ellipse([center_x - 124, desk_y + 16, center_x - 96, desk_y + 40], fill=line_col)
        # Right arm pointing up towards breaking news/headline
        elbow_x, elbow_y = center_x + 105, 230 + bob_y
        hand_x, hand_y = center_x + 165, 100 + bob_y
        draw.line([(neck_x + shoulder_offset, shoulder_y), (elbow_x, elbow_y), (hand_x, hand_y)], fill=line_col, width=line_w)
        draw.ellipse([hand_x - 16, hand_y - 16, hand_x + 16, hand_y + 16], fill=line_col)
        draw.line([(hand_x, hand_y), (hand_x + 18, hand_y - 32)], fill=line_col, width=line_w - 1)

    elif gesture == "explain":
        # Both hands gesturing outward from desk
        draw.line([(neck_x - shoulder_offset, shoulder_y), (center_x - 80, desk_y - 15), (center_x - 135, desk_y + 12)], fill=line_col, width=line_w)
        draw.ellipse([center_x - 148, desk_y + 2, center_x - 122, desk_y + 24], fill=line_col)
        draw.line([(neck_x + shoulder_offset, shoulder_y), (center_x + 80, desk_y - 15), (center_x + 135, desk_y + 12)], fill=line_col, width=line_w)
        draw.ellipse([center_x + 122, desk_y + 2, center_x + 148, desk_y + 24], fill=line_col)

    elif gesture == "salute":
        # Left arm on desk
        draw.line([(neck_x - shoulder_offset, shoulder_y), (center_x - 65, desk_y + 12), (center_x - 110, desk_y + 28)], fill=line_col, width=line_w)
        draw.ellipse([center_x - 124, desk_y + 16, center_x - 96, desk_y + 40], fill=line_col)
        # Right arm saluting
        salute_x, salute_y = center_x + 125, 175 + bob_y
        elbow_x, elbow_y = center_x + 95, 265 + bob_y
        draw.line([(neck_x + shoulder_offset, shoulder_y), (elbow_x, elbow_y), (salute_x, salute_y)], fill=line_col, width=line_w)
        draw.ellipse([salute_x - 16, salute_y - 16, salute_x + 16, salute_y + 16], fill=line_col)

    else: # idle
        # Both hands resting symmetrically on desk
        draw.line([(neck_x - shoulder_offset, shoulder_y), (center_x - 65, desk_y + 12), (center_x - 110, desk_y + 28)], fill=line_col, width=line_w)
        draw.ellipse([center_x - 124, desk_y + 16, center_x - 96, desk_y + 40], fill=line_col)
        draw.line([(neck_x + shoulder_offset, shoulder_y), (center_x + 65, desk_y + 12), (center_x + 110, desk_y + 28)], fill=line_col, width=line_w)
        draw.ellipse([center_x + 96, desk_y + 16, center_x + 124, desk_y + 40], fill=line_col)

    # 4. Symmetrical Curved Modern Studio Desk (Glassmorphism Dark)
    front_poly = [
        (center_x - desk_half_w, desk_y + 40),
        (center_x + desk_half_w, desk_y + 40),
        (center_x + desk_half_w - 35, target_h),
        (center_x - desk_half_w + 35, target_h)
    ]
    draw.polygon(front_poly, fill=(15, 23, 42, 245))

    top_poly = [
        (center_x - desk_half_w + 40, desk_y),
        (center_x + desk_half_w - 40, desk_y),
        (center_x + desk_half_w, desk_y + 40),
        (center_x - desk_half_w, desk_y + 40)
    ]
    draw.polygon(top_poly, fill=(30, 41, 59, 255), outline=(56, 189, 248, 230), width=3)

    # Broadcast Studio Microphone
    mic_x, mic_y = center_x + 140, desk_y + 22
    draw.ellipse([mic_x - 16, mic_y - 7, mic_x + 16, mic_y + 7], fill=(51, 65, 85, 255))
    draw.line([(mic_x, mic_y), (mic_x - 12, mic_y - 65)], fill=(148, 163, 184, 255), width=6)
    draw.ellipse([mic_x - 24, mic_y - 105, mic_x, mic_y - 62], fill=(15, 23, 42, 255), outline=(239, 68, 68, 255), width=2)
    draw.ellipse([mic_x - 15, mic_y - 88, mic_x - 9, mic_y - 82], fill=(239, 68, 68, 255))

    # 5. Extract & Render User's Exact Hand-Drawn Head (Scaled up by +1 point)
    base = get_base_img()
    if base is None:
        base = Image.new("RGBA", (571, 1024), (0, 0, 0, 0))

    head_crop = base.crop((40, 80, 530, 600))
    h_draw = ImageDraw.Draw(head_crop)
    h_draw.ellipse([100, 260, 440, 480], fill=(255, 255, 255, 255))

    # Eyes
    left_eye_x, left_eye_y = 206, 310
    right_eye_x, right_eye_y = 378, 308

    if eye_state == "blink":
        h_draw.arc([left_eye_x - 16, left_eye_y - 6, left_eye_x + 16, left_eye_y + 14], 200, 340, fill=line_col, width=line_w)
        h_draw.arc([right_eye_x - 16, right_eye_y - 6, right_eye_x + 16, right_eye_y + 14], 200, 340, fill=line_col, width=line_w)
    elif eye_state == "wide":
        h_draw.ellipse([left_eye_x - 14, left_eye_y - 16, left_eye_x + 14, left_eye_y + 16], fill=line_col)
        h_draw.ellipse([right_eye_x - 14, right_eye_y - 16, right_eye_x + 14, right_eye_y + 16], fill=line_col)
        h_draw.arc([left_eye_x - 20, left_eye_y - 40, left_eye_x + 20, left_eye_y - 18], 190, 350, fill=line_col, width=5)
        h_draw.arc([right_eye_x - 20, right_eye_y - 40, right_eye_x + 20, right_eye_y - 18], 190, 350, fill=line_col, width=5)
    else:
        eye_r = 8.5
        h_draw.ellipse([left_eye_x - eye_r, left_eye_y - eye_r, left_eye_x + eye_r, left_eye_y + eye_r], fill=line_col)
        h_draw.ellipse([right_eye_x - eye_r, right_eye_y - eye_r, right_eye_x + eye_r, right_eye_y + eye_r], fill=line_col)

    # Mouth
    if mouth_state == "open_wide":
        h_draw.chord([115, 390, 285, 475], 10, 175, fill=line_col, outline=line_col, width=line_w)
    elif mouth_state == "open_o":
        h_draw.ellipse([175, 400, 235, 460], fill=line_col)
    elif mouth_state == "shocked":
        h_draw.ellipse([185, 405, 225, 465], fill=line_col)
    else:
        h_draw.arc([105, 340, 280, 465], 25, 155, fill=line_col, width=line_w + 1)

    # Scaled up head (+1 size point)
    head_crop.thumbnail((275, 275), Image.Resampling.LANCZOS)
    canvas.paste(head_crop, (neck_x - 140, neck_y - 235), head_crop)

    # 6. Add White Outer Silhouette Glow
    alpha = canvas.split()[-1]
    stroke_mask = alpha.filter(ImageFilter.MaxFilter(7))
    stroke_layer = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    stroke_layer.putalpha(stroke_mask)
    final_canvas = Image.alpha_composite(stroke_layer, canvas)

    return final_canvas


def generate_stickman_video_overlay(
    total_duration,
    boundaries=None,
    fps=30,
    output_mov="temp_reel/stickman_overlay.mov",
    temp_frames_dir="temp_reel/stickman_frames"
):
    """
    Renders an alpha-transparent 30fps video overlay of the centered news anchor stickman
    synchronized to voiceover word boundaries and reel story phases.
    """
    os.makedirs(temp_frames_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_mov) or ".", exist_ok=True)

    total_frames = int(total_duration * fps)

    # Convert boundaries to active speech intervals
    speech_intervals = []
    if boundaries:
        for b in boundaries:
            start_sec = b["offset"] / 10_000_000.0
            dur_sec = b["duration"] / 10_000_000.0
            speech_intervals.append((start_sec, start_sec + dur_sec))

    print(f"🧍 Generating {total_frames} animated centered news anchor frames (+1 Size, 30 FPS)...")

    # Cache pre-rendered poses
    pose_cache = {}
    def get_pose(m, e, g, b_y):
        key = (m, e, g, b_y)
        if key not in pose_cache:
            pose_cache[key] = render_centered_anchor_frame(mouth_state=m, eye_state=e, gesture=g, bob_y=b_y)
        return pose_cache[key]

    for f_idx in range(total_frames):
        t = f_idx / float(fps)

        # 1. Speaking vs Pause detection
        is_speaking = any(s <= t <= e for s, e in speech_intervals) if speech_intervals else True

        # 2. Timeline Story Phases & Gestures
        if t < 3.8:
            gesture = "point_up"
            eye_state = "wide"
        elif t < 9.0:
            gesture = "explain"
            eye_state = "normal"
        elif t < 15.0:
            gesture = "explain"
            eye_state = "normal"
        else: # CTA / Closing Follow
            gesture = "salute"
            eye_state = "normal"

        # 3. Blinking cycle (every 3.4 seconds for 4 frames)
        blink_cycle = t % 3.4
        if blink_cycle < 0.12 and eye_state != "wide":
            eye_state = "blink"

        # 4. Mouth Visemes (Talks at natural 7.5 Hz cadence during speech)
        if is_speaking:
            mouth_cycle = int(t * 8.0) % 3
            if mouth_cycle == 0:
                mouth_state = "open_wide"
            elif mouth_cycle == 1:
                mouth_state = "open_o"
            else:
                mouth_state = "smile"
        else:
            mouth_state = "smile"

        # 5. Breathing bob on chair (gentle 4px)
        bob_y = int(4 * math.sin(2 * math.pi * t * 1.5))

        frame_img = get_pose(mouth_state, eye_state, gesture, bob_y)
        frame_path = os.path.join(temp_frames_dir, f"frame_{f_idx:05d}.png")
        frame_img.save(frame_path, "PNG")

    # Compile transparent video overlay with FFmpeg (PNG transparent video codec)
    print("🎥 Compiling centered news anchor frames to 30 FPS transparent video stream...")
    cmd = [
        FFMPEG_EXE, "-y",
        "-framerate", str(fps),
        "-i", os.path.join(temp_frames_dir, "frame_%05d.png"),
        "-c:v", "png",
        "-pix_fmt", "rgba",
        "-t", str(total_duration),
        output_mov
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Warning compiling stickman overlay: {res.stderr}")
        return None

    # Cleanup temp frame PNGs
    for f in os.listdir(temp_frames_dir):
        if f.endswith(".png"):
            try:
                os.remove(os.path.join(temp_frames_dir, f))
            except Exception:
                pass
    try:
        os.rmdir(temp_frames_dir)
    except Exception:
        pass

    return output_mov
