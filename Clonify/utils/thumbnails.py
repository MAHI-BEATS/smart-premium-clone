import os
import re
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from py_yt import VideosSearch

from Clonify import app
from config import YOUTUBE_IMG_URL


# --- HELPER FUNCTIONS FOR IMAGE EFFECTS ---

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def clear(text):
    words = text.split(" ")
    title = ""
    for i in words:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()


def circle(img):
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)
    result = Image.new("RGBA", img.size, (0, 0, 0, 0))
    result.paste(img, (0, 0), mask)
    return result


def create_glass_panel(bg, box, radius=60, blur=20, alpha=90):
    panel = bg.crop(box)
    panel = panel.filter(ImageFilter.GaussianBlur(blur))
    tint = Image.new("RGBA", panel.size, (0, 0, 0, alpha))
    panel = Image.alpha_composite(panel.convert("RGBA"), tint)
    mask = Image.new("L", panel.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, panel.size[0], panel.size[1]), radius=radius, fill=255)
    panel.putalpha(mask)
    return panel


def add_neon_glow(img, glow_color=(255, 60, 160), blur_radius=30, expand=45):
    canvas_size = (img.width + expand * 2, img.height + expand * 2)
    glow_canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_canvas)
    glow_draw.ellipse((expand, expand, img.width + expand, img.height + expand), fill=glow_color)
    glow_canvas = glow_canvas.filter(ImageFilter.GaussianBlur(blur_radius))
    glow_canvas.paste(img, (expand, expand), img)
    return glow_canvas


def draw_text_with_glow(draw, pos, text, font, fill, glow_color):
    x, y = pos
    draw.text((x + 4, y + 4), text, font=font, fill=glow_color)
    draw.text((x, y), text, font=font, fill=fill)


async def download_user_photo(user_id):
    if not user_id:
        return None
    try:
        user = await app.get_users(user_id)
        if user.photo:
            photo_path = await app.download_media(
                user.photo.big_file_id, 
                file_name=f"cache/user_{user_id}.jpg"
            )
            return photo_path
    except Exception:
        pass
    return None

# ------------------------------------------

async def get_thumb(videoid, user_id=None):
    # Unique final path based on user_id to prevent caching issues
    final_path = f"cache/{videoid}_{user_id}.png" if user_id else f"cache/{videoid}.png"
    thumb_path = f"cache/thumb{videoid}.png"
    user_photo_path = None
    
    if os.path.isfile(final_path):
        return final_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    
    try:
        # 1. Fetch Video Metadata
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
            duration = result.get("duration", "Unknown Mins")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except Exception:
                views = "Unknown Views"
            channel = result.get("channel", {}).get("name", "Unknown Channel")

        # 2. Download Thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(thumb_path, mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # 3. Prepare Background (1920x1080)
        youtube = Image.open(thumb_path)
        image1 = youtube.resize((1920, 1080)) 
        image2 = image1.convert("RGBA")
        
        background = image2.filter(filter=ImageFilter.BoxBlur(10))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)
        
        draw = ImageDraw.Draw(background)

        # 4. Main UI Card
        panel_box = (50, 50, 1870, 1030)
        glass = create_glass_panel(background, panel_box, radius=60, blur=20, alpha=90)
        background.paste(glass, (panel_box[0], panel_box[1]), glass)
        draw.rounded_rectangle(panel_box, radius=60, outline=(132, 224, 240, 180), width=6)

        # 5. Left Thumbnail (Circular & Glowing)
        yt_circle = circle(youtube)
        yt_circle = changeImageSize(550, 550, yt_circle)
        yt_glow = add_neon_glow(yt_circle, glow_color=(255, 60, 160), blur_radius=30, expand=45)
        background.paste(yt_glow, (100, 230), yt_glow)

        # 6. User Profile (Right Side)
        if user_id:
            user_photo_path = await download_user_photo(user_id)
            if user_photo_path and os.path.exists(user_photo_path):
                try:
                    u_img = Image.open(user_photo_path).convert("RGBA")
                    u_circle = circle(u_img)
                    u_circle = changeImageSize(380, 380, u_circle)
                    u_glow = add_neon_glow(u_circle, glow_color=(0, 255, 255), blur_radius=30, expand=45)
                    background.paste(u_glow, (1410, 310), u_glow)
                except Exception:
                    pass

        # 7. Load Fonts
        try:
            heading_font = ImageFont.truetype("Clonify/assets/font2.ttf", 60)
            font = ImageFont.truetype("Clonify/assets/font.ttf", 55)
            small_font = ImageFont.truetype("Clonify/assets/font.ttf", 40)
            branding_font = ImageFont.truetype("Clonify/assets/font2.ttf", 50)
        except Exception:
            heading_font = ImageFont.load_default()
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            branding_font = ImageFont.load_default()

        # 8. Draw Text & Details
        text_x = 800
        draw.text((text_x, 300), "NOW PLAYING", fill=(0, 255, 255), font=heading_font)
        clean_title = clear(title)
        draw.text((text_x, 400), clean_title, fill="white", font=font)
        draw.text((text_x, 530), f"Artist: {channel}", fill="white", font=small_font)
        draw.text((text_x, 600), f"Views: {views}", fill="white", font=small_font)
        draw.text((text_x, 670), f"Duration: {duration}", fill="white", font=small_font)

        # 9. Large Footer Branding
        draw_text_with_glow(draw, (90, 940), "BETA BOT HUB", branding_font, (132, 224, 240), (0, 255, 255, 120))
        draw_text_with_glow(draw, (1480, 940), "👑 THE SHIV", branding_font, (255, 60, 160), (255, 0, 170, 120))

        # 10. Cleanup & Save
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
            
        if user_photo_path and os.path.exists(user_photo_path):
            try:
                os.remove(user_photo_path)
            except:
                pass
                
        background = background.convert("RGB")
        background.save(final_path, "PNG", quality=95)  # Changed to PNG
        return final_path

    except Exception as e:
        print(f"Thumbnail Error: {e}")
        # Clean up temp files if error occurs
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        if user_photo_path and os.path.exists(user_photo_path):
            try:
                os.remove(user_photo_path)
            except:
                pass
        return YOUTUBE_IMG_URL
