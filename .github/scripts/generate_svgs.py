import urllib.request
import re
import math
import os

# 1. Fetch contribution calendar data
url = "https://github.com/users/Mailor-Jorge/contributions"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode("utf-8")

# Extract all days
days = []
# Match date and level
matches = re.findall(r'<td[^>]*data-date="([^"]+)"[^>]*data-level="([^"]+)"', html)
if not matches:
    matches = re.findall(r'<td[^>]*data-level="([^"]+)"[^>]*data-date="([^"]+)"', html)
    matches = [(d, l) for l, d in matches]

print(f"Total days extracted: {len(matches)}")

# 53 weeks, 7 days per week
# Group into weeks
weeks = []
current_week = []
for date_str, level_str in matches:
    current_week.append((date_str, int(level_str)))
    if len(current_week) == 7:
        weeks.append(current_week)
        current_week = []
if current_week:
    weeks.append(current_week)

print(f"Total weeks: {len(weeks)}")

# Colors
dark_bg = "#0d1117"
cell_empty_dark = "#161b22"
green_levels = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

# -------------------------------------------------------------
# Generate Snake Animated SVG
# -------------------------------------------------------------
def generate_snake_svg(dark=True):
    bg = "#0d1117" if dark else "#ffffff"
    empty = "#161b22" if dark else "#ebedf0"
    cols = len(weeks)
    cell_size = 11
    gap = 3
    pad_x = 30
    pad_y = 25
    width = pad_x * 2 + cols * (cell_size + gap)
    height = pad_y * 2 + 7 * (cell_size + gap)

    # Active day positions
    active_coords = []
    rects = []
    for w_idx, week in enumerate(weeks):
        for d_idx, (date_str, lvl) in enumerate(week):
            x = pad_x + w_idx * (cell_size + gap)
            y = pad_y + d_idx * (cell_size + gap)
            color = green_levels[lvl] if dark else (
                ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"][lvl]
            )
            rects.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{color}" />')
            if lvl > 0:
                active_coords.append((x + cell_size//2, y + cell_size//2))

    # Snake path animation: create an animated path across the board
    # Snake path travels across weeks and visits active cells
    path_points = []
    # Start top left
    path_points.append((pad_x, pad_y))
    # Sweep along bottom and right
    for ax, ay in active_coords:
        path_points.append((ax, ay))
    # End around right edge
    path_points.append((pad_x + (cols - 1) * (cell_size + gap), pad_y + 3 * (cell_size + gap)))
    path_points.append((pad_x + 5, pad_y + 6 * (cell_size + gap)))

    d_path = f"M {path_points[0][0]} {path_points[0][1]} " + " ".join([f"L {x} {y}" for x, y in path_points[1:]]) + " Z"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    .snake-head {{
      fill: #58a6ff;
      filter: drop-shadow(0 0 4px #58a6ff);
    }}
    .snake-body {{
      stroke: #39d353;
      stroke-width: 6;
      stroke-linecap: round;
      stroke-linejoin: round;
      fill: none;
      stroke-dasharray: 40 800;
      animation: snakeMove 14s linear infinite;
    }}
    @keyframes snakeMove {{
      0% {{ stroke-dashoffset: 840; }}
      100% {{ stroke-dashoffset: 0; }}
    }}
  </style>
  <rect width="100%" height="100%" rx="8" fill="{bg}" />
  <g id="grid">
    {''.join(rects)}
  </g>
  <path class="snake-body" d="{d_path}" />
  <circle r="5" class="snake-head">
    <animateMotion path="{d_path}" dur="14s" repeatCount="indefinite" />
  </circle>
</svg>"""
    return svg

# Write snake SVGs
os.makedirs("profile-3d-contrib", exist_ok=True)
os.makedirs("profile-summary-card-output/classic", exist_ok=True)

with open("github-contribution-grid-snake-dark.svg", "w", encoding="utf-8") as f:
    f.write(generate_snake_svg(dark=True))
with open("github-contribution-grid-snake.svg", "w", encoding="utf-8") as f:
    f.write(generate_snake_svg(dark=False))

# -------------------------------------------------------------
# Generate 3D Isometric Contribution Graph SVG
# -------------------------------------------------------------
def generate_3d_isometric_svg():
    width = 800
    height = 360
    origin_x = 400
    origin_y = 120

    # Isometric projection angles
    # X axis extends down-right (+30 deg), Y axis extends down-left (+150 deg)
    angle_x = math.radians(26)
    angle_y = math.radians(154)

    dx_x = math.cos(angle_x) * 6.8
    dx_y = math.sin(angle_x) * 6.8

    dy_x = math.cos(angle_y) * 14.5
    dy_y = math.sin(angle_y) * 14.5

    bars = []
    
    # Sort order for isometric rendering (painter's algorithm: back to front)
    # weeks 0..52, days 0..6
    for w_idx in range(len(weeks)):
        for d_idx in range(len(weeks[w_idx])):
            date_str, lvl = weeks[w_idx][d_idx]
            # Height of bar based on contribution level
            h = 4 + lvl * 16

            # Grid base position
            bx = origin_x + (w_idx - len(weeks)/2) * dx_x + (d_idx - 3.5) * dy_x
            by = origin_y + (w_idx - len(weeks)/2) * dx_y + (d_idx - 3.5) * dy_y

            # Colors based on lvl
            if lvl == 0:
                top_col = "#161b22"
                left_col = "#0e131a"
                right_col = "#121820"
            elif lvl == 1:
                top_col = "#0e4429"
                left_col = "#09331e"
                right_col = "#0c3b24"
            elif lvl == 2:
                top_col = "#006d32"
                left_col = "#005226"
                right_col = "#005f2c"
            elif lvl == 3:
                top_col = "#26a641"
                left_col = "#1d8233"
                right_col = "#21943a"
            else:
                top_col = "#39d353"
                left_col = "#2db143"
                right_col = "#34c44d"

            # Hexagonal/cube isometric bar
            bw = 4.8
            # Top polygon
            top_poly = f"{bx},{by-h} {bx+bw},{by-h+2.4} {bx},{by-h+4.8} {bx-bw},{by-h+2.4}"
            # Left polygon
            left_poly = f"{bx-bw},{by-h+2.4} {bx},{by-h+4.8} {bx},{by+4.8} {bx-bw},{by+2.4}"
            # Right polygon
            right_poly = f"{bx},{by-h+4.8} {bx+bw},{by-h+2.4} {bx+bw},{by+2.4} {bx},{by+4.8}"

            poly_group = f"""<g>
  <polygon points="{left_poly}" fill="{left_col}" />
  <polygon points="{right_poly}" fill="{right_col}" />
  <polygon points="{top_poly}" fill="{top_col}" />
</g>"""
            bars.append(poly_group)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090d13" />
      <stop offset="100%" stop-color="#0d1117" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>
  <rect width="100%" height="100%" rx="8" fill="url(#bg)" stroke="#30363d" stroke-width="1" />
  <text x="30" y="38" fill="#58a6ff" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="15" font-weight="600">3D Contribution Profile Matrix · Mailor-Jorge</text>
  <text x="30" y="58" fill="#8b949e" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="12">Isometric Commit Topology · SE/2026</text>
  <g transform="translate(0, 40)">
    {''.join(bars)}
  </g>
</svg>"""
    return svg

with open("profile-3d-contrib/profile-green-animate.svg", "w", encoding="utf-8") as f:
    f.write(generate_3d_isometric_svg())

print("Generated all SVGs successfully!")
