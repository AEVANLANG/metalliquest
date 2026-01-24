from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, date
from zoneinfo import ZoneInfo
import json
import math

# ---------- CONFIG ----------

START_DATE = date(2026, 1, 25)
TIMEZONE = ZoneInfo("Europe/Amsterdam")

IMAGE_WIDTH = 2048
IMAGE_HEIGHT = 512

TEXT_BOX_WIDTH = 1140
TEXT_BOX_HEIGHT = 440

LEFT_IGNORE = 512

QUESTION_SIZE_START = 64
ANSWER_SIZE_START = 44
LINE_SPACING = 10
BLOCK_SPACING = 24

FONT_PATH = "assets/fonts/VT323-Regular.ttf"

BACKGROUND_IMAGE = "assets/background.png"
OUTPUT_IMAGE = "dailyjoke/today.png"

JOKES_FILE = "data/jokes.json"

# ---------- HELPERS ----------

def wrap_text(draw, text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word
        width = draw.textlength(test, font=font)
        if width <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def calculate_block_height(draw, lines, font):
    ascent, descent = font.getmetrics()
    line_height = ascent + descent + LINE_SPACING
    return len(lines) * line_height


# ---------- MAIN ----------

def main():
    # Load jokes
    with open(JOKES_FILE, "r", encoding="utf-8") as f:
        jokes = json.load(f)

    total_jokes = len(jokes)

    # Get today in NL time
    today = datetime.now(TIMEZONE).date()
    days_passed = (today - START_DATE).days
    index = days_passed % total_jokes

    joke = jokes[index]
    question = joke["question"]
    answer = joke["answer"]

    # Load background
    image = Image.open(BACKGROUND_IMAGE).convert("RGBA")
    draw = ImageDraw.Draw(image)

    # Font sizing loop
    q_size = QUESTION_SIZE_START
    a_size = ANSWER_SIZE_START

    while True:
        q_font = ImageFont.truetype(FONT_PATH, q_size)
        a_font = ImageFont.truetype(FONT_PATH, a_size)

        q_lines = wrap_text(draw, question, q_font, TEXT_BOX_WIDTH)
        a_lines = wrap_text(draw, answer, a_font, TEXT_BOX_WIDTH)

        q_height = calculate_block_height(draw, q_lines, q_font)
        a_height = calculate_block_height(draw, a_lines, a_font)

        total_height = q_height + BLOCK_SPACING + a_height

        if total_height <= TEXT_BOX_HEIGHT or q_size <= 20:
            break

        q_size -= 2
        a_size -= 2

    # Vertical centering
    y_start = (TEXT_BOX_HEIGHT - total_height) // 2

    x_start = IMAGE_WIDTH - TEXT_BOX_WIDTH
    y = y_start

    # Draw question
    for line in q_lines:
        draw.text((x_start, y), line, font=q_font, fill="white")
        y += q_font.getmetrics()[0] + q_font.getmetrics()[1] + LINE_SPACING

    y += BLOCK_SPACING

    # Draw answer
    for line in a_lines:
        draw.text((x_start, y), line, font=a_font, fill="white")
        y += a_font.getmetrics()[0] + a_font.getmetrics()[1] + LINE_SPACING

    # Save output
    image.save(OUTPUT_IMAGE, "PNG")


if __name__ == "__main__":
    main()
