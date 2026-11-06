# Генератори графіки INCON

Скрипти, якими зроблено банер YouTube-каналу і анімацію «Підписатися» для сайту.
Потрібні Python 3 з Pillow, шрифт Inter (`/usr/share/fonts/opentype/inter/`) і ffmpeg.
Вхідний файл — логотип INCON (червоні слоники на білому, JPG/PNG).

## Банер YouTube-каналу (2560×1440)

```bash
python3 youtube_banner.py logo.jpg youtube-banner-incon-2560x1440.png preview.png
```

`preview.png` — зменшена копія з зеленою рамкою зони, яку видно на телефоні.

## Анімація «Підписатися» (показ 960×150, файл 1920×300)

```bash
python3 subscribe_gif.py logo.jpg frames
ffmpeg -framerate 25 -i frames/f%03d.png -vf "palettegen=max_colors=256:stats_mode=full" pal.png
ffmpeg -framerate 25 -i frames/f%03d.png -i pal.png -lavfi "paletteuse=dither=sierra2_4a:diff_mode=rectangle" -loop 0 incon-pidpyshis-youtube.gif
ffmpeg -framerate 25 -i frames/f%03d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -movflags +faststart incon-pidpyshis-youtube.mp4
```

Код для сайту (відео чіткіше й легше за GIF):

```html
<a href="https://www.youtube.com/@incon.seminar?sub_confirmation=1" target="_blank" rel="noopener">
  <video src="/wp-content/uploads/incon-pidpyshis-youtube.mp4" autoplay loop muted playsinline
         width="960" height="150" style="max-width:100%;height:auto;display:block"></video>
</a>
```
