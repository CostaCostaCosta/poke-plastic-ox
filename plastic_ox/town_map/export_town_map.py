#!/usr/bin/env python3
"""Regenerate SVG masters, PNGs, and a fixed 16-color GBA-size concept preview."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from PIL import Image, ImageOps
import render_town_map

OUT = Path(__file__).resolve().parent
PALETTE = ['b8e4ec', '69adbd', 'cfeeaf', 'e2b98f', '929d8d', 'fffbe9',
           '769795', 'e96350', '658dcc', '826bb6', '737f73', '66b77c',
           '425e54', '7eb682', '91c9d6', 'e7f1cc']


def main():
    render_town_map.main()
    chrome = shutil.which('google-chrome') or shutil.which('chromium')
    if not chrome:
        raise SystemExit('PNG export needs Chrome or Chromium; SVG masters were generated.')
    with tempfile.TemporaryDirectory(prefix='plastic-ox-town-map-') as temp:
        for suffix in ('', '_unlabeled'):
            svg = OUT/f'plastic_ox_town_map{suffix}.svg'
            png = svg.with_suffix('.png')
            html = Path(temp)/f'preview{suffix}.html'
            html.write_text('<body style="margin:0;overflow:hidden">'
                            f'<img width="1600" height="1100" src="{svg.as_uri()}"></body>')
            subprocess.run([chrome, '--headless', '--no-sandbox', '--disable-gpu',
                            '--hide-scrollbars', f'--screenshot={png}',
                            '--window-size=1600,1100', html.as_uri()],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    image = Image.open(OUT/'plastic_ox_town_map_unlabeled.png').convert('RGB')
    small = ImageOps.contain(image, (240,160), Image.Resampling.LANCZOS)
    offset = ((240-small.width)//2, (160-small.height)//2)
    canvas = Image.new('RGB', (240,160), '#b8e4ec')
    canvas.paste(small, offset)
    # A fixed palette preserves small red/blue town markers; an adaptive
    # quantizer otherwise spends its palette on large land and sea areas.
    palette = Image.new('P', (1,1))
    rgb = [int(color[i:i+2], 16) for color in PALETTE for i in (0,2,4)]
    palette.putpalette(rgb + rgb[:3]*(256-len(PALETTE)))
    canvas = canvas.quantize(palette=palette, dither=Image.Dither.NONE)
    canvas.save(OUT/'town_map_240x160.png', bits=4)
    canvas.resize((960,640), Image.Resampling.NEAREST).save(OUT/'town_map_240x160_preview.png')
    data = json.loads((OUT/'layout.json').read_text())
    data['gba_preview'] = {'size':[240,160], 'palette': PALETTE, 'nodes':[
        {'name':node['name'], 'position':[
            round(node['position'][0]*small.width/1600+offset[0]),
            round(node['position'][1]*small.height/1100+offset[1])]}
        for node in data['nodes']]}
    (OUT/'layout.json').write_text(json.dumps(data, indent=2)+'\n')
    print('Exported labeled PNG, unlabeled PNG, and 16-color 240×160 preview.')


if __name__ == '__main__':
    main()
