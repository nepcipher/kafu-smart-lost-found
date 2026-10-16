from PIL import Image, ImageDraw
import os

os.makedirs("static/icons", exist_ok=True)

for size in (192, 512):
    img = Image.new("RGB", (size, size), "#102b50")
    d = ImageDraw.Draw(img)

    # Rounded blue background
    margin = size * 0.06
    d.rounded_rectangle(
        (margin, margin, size-margin, size-margin),
        radius=int(size * 0.18),
        fill="#1769aa"
    )

    # Magnifying glass
    cx, cy = int(size * 0.43), int(size * 0.40)
    r = int(size * 0.19)
    width = max(5, int(size * 0.045))
    d.ellipse((cx-r, cy-r, cx+r, cy+r), outline="white", width=width)
    d.line(
        (cx+int(r*0.70), cy+int(r*0.70),
         int(size*0.76), int(size*0.75)),
        fill="white", width=width+2
    )

    # Check mark
    d.line(
        (int(size*0.31), int(size*0.63),
         int(size*0.43), int(size*0.74),
         int(size*0.66), int(size*0.53)),
        fill="#70f0b0", width=max(6, int(size*0.055)),
        joint="curve"
    )

    img.save(f"static/icons/icon-{size}.png")

print("KAFU app icons created successfully!")
