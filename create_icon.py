from PIL import Image, ImageDraw

# 1024x1024 のアイコン画像を作成
img = Image.new('RGB', (1024, 1024), color='#2196F3')
draw = ImageDraw.Draw(img)

# 簡単なテキストを描画
from PIL import ImageFont
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 200)
except:
    font = ImageFont.load_default()

text = "G"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (1024 - text_width) // 2
y = (1024 - text_height) // 2

draw.text((x, y), text, fill='white', font=font)

# PNG として保存
img.save('resources/icons/app_icon.png')
print("✅ アイコン画像を作成しました: resources/icons/app_icon.png")
