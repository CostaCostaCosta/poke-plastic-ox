#!/usr/bin/env python3
"""Author the high-level Plastic Ox town-map artwork; no ROM data is modified.

Coordinates are diagram positions, not tile coordinates. Numbered corridors
summarize regional routes; dotted passages summarize the guided story journey.
The full data-level topology remains in ../region_layout.svg.
"""
from html import escape
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
W, H = 1600, 1100
# name, x, y, marker class, label dx/dy, text anchor
NODES = [
    ('Pallet Town', 235, 880, 'town', 0, 53, 'middle'),
    ('Oldale Town', 235, 735, 'town', -30, -32, 'end'),
    ('Cherrygrove City', 445, 735, 'city', 0, 53, 'middle'),
    ('Dark Cave', 440, 550, 'cave', 0, -35, 'middle'),
    ('Ilex Forest', 625, 610, 'forest', 0, -37, 'middle'),
    ('Rustboro City', 680, 830, 'city', 0, 54, 'middle'),
    ('Mt. Moon', 835, 735, 'cave', 0, -37, 'middle'),
    ('Goldenrod City', 870, 530, 'city', 32, 54, 'start'),
    ('National Park', 680, 390, 'forest', -32, 8, 'end'),
    ('Ecruteak City', 870, 270, 'city', 0, -38, 'middle'),
    ('Fortree City', 1100, 365, 'city', 0, -38, 'middle'),
    ('Lavender Town', 1190, 530, 'town', 0, -38, 'middle'),
    ('Cinnabar Island', 1120, 875, 'city', 0, 53, 'middle'),
    ('Whirl Islands', 890, 955, 'cave', 0, 46, 'middle'),
    ('Mossdeep City', 1415, 810, 'city', 0, 53, 'middle'),
    ('Saffron City', 1415, 575, 'city', 0, -38, 'middle'),
    ('Blackthorn City', 1390, 365, 'city', 0, -38, 'middle'),
    ('Victory Road', 1255, 200, 'cave', -30, 8, 'end'),
    ('Indigo Plateau', 1440, 160, 'league', 0, -42, 'middle'),
]
# Each line is a simplified corridor. Route badges are explicitly placed below.
ROADS = [
    ('M235 880 V735', ['Route101']),
    ('M235 735 H445', ['Route29_hns']),
    ('M445 735 V610 H440 V550', ['Route30_hns', 'Route31_hns']),
    ('M340 735 V550 H440', ['Route46_hns', 'DarkCave_SouthSide_hns']),
    ('M445 610 H625', ['Route31_hns', 'Gate_AzaleaTown_IlexForest_hns']),
    ('M625 610 H735 V530 H870', ['Route34_hns']),
    ('M680 830 V735 H835', ['Route2_hns', 'Route3_hns']),
    ('M835 735 H1000 V635', ['Route4_hns']),
    ('M870 530 H1010 V450', ['Route14_hns']),
    ('M870 530 V455 H680 V390', ['Route35_hns', 'NationalPark_Normal_hns']),
    ('M680 390 H870 V270', ['Route36_hns', 'Route37_hns']),
    ('M870 270 H665', ['Route38_hns']),
    ('M235 735 V655', ['Route103']),
    ('M680 830 H575', ['Route104']),
    ('M680 830 H785', ['Route116']),
    ('M1100 365 H1025 V430', ['Route119']),
    ('M1100 365 H1170 V425', ['Route120']),
    ('M1415 810 H1330 V755', ['Route124']),
    ('M1415 810 V735', ['Route125']),
    ('M1415 810 V930', ['Route127']),
]
PASSAGES = [
    ('M1000 635 H870 V530', 'Route 4', 'Goldenrod City'),
    ('M625 610 V685 H585 V830 H680', 'Ilex Forest', 'Rustboro City'),
    ('M870 270 H995 Q1020 270 1020 295 V315 Q1020 340 1045 340 H1100 V365', 'Ecruteak City', 'Fortree City'),
    ('M1100 365 V465 H1190 V530', 'Fortree City', 'Lavender Town'),
    ('M1190 530 V705 Q1190 735 1160 735 H1150 Q1120 735 1120 765 V875', 'Lavender Town', 'Cinnabar Island'),
    ('M1120 875 V955 H890', 'Cinnabar Island', 'Whirl Islands'),
    ('M1120 875 H1280 Q1310 875 1310 845 V835 Q1310 810 1335 810 H1415', 'Cinnabar Island', 'Mossdeep City'),
    ('M1415 810 V575', 'Mossdeep City', 'Saffron City'),
    ('M1415 575 V430 H1390 V365', 'Saffron City', 'Blackthorn City'),
    ('M1390 365 V270 H1255 V200', 'Blackthorn City', 'Victory Road'),
    ('M1255 200 H1340 V160 H1440', 'Victory Road', 'Indigo Plateau'),
]
BADGES = [(235,809,'101'), (337,735,'29'), (445,669,'30'), (537,610,'31'),
          (340,638,'46'), (736,571,'34'), (680,778,'2'), (749,735,'3'),
          (934,735,'4'), (1010,480,'14'), (773,455,'35'), (773,390,'36'),
          (870,333,'37'), (756,270,'38'), (235,659,'103'), (584,830,'104'),
          (777,830,'116'), (1030,410,'119'), (1170,409,'120'),
          (1330,755,'124'), (1415,735,'125'), (1415,923,'127')]


def render(labels=True):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
           '<title id="title">Plastic Ox town map</title>',
           '<desc id="desc">A schematic regional map showing towns, numbered route corridors, forests, caves, and guided passages.</desc>',
           '<defs><pattern id="sea" width="36" height="36" patternUnits="userSpaceOnUse"><path d="M4 22 Q9 17 14 22 T24 22" fill="none" stroke="#91c9d6" stroke-width="1.4" opacity=".32"/></pattern></defs>',
           '<rect width="1600" height="1100" fill="#b8e4ec"/><rect width="1600" height="1100" fill="url(#sea)"/>',
           # Coastline and inland terrains.
           '<path d="M55 135 Q140 65 325 125 Q435 152 565 110 Q710 45 890 80 Q980 100 1055 83 Q1250 30 1530 85 L1570 640 Q1515 691 1470 681 Q1375 695 1330 655 Q1260 610 1225 660 Q1170 720 1060 753 Q1015 785 965 855 Q865 936 764 912 Q714 895 685 942 Q618 1015 525 951 Q467 914 404 938 Q292 1000 186 937 Q124 907 122 814 Q103 739 145 675 Q177 619 120 570 Q44 524 88 443 Q142 347 68 287 Q28 234 55 135Z" fill="#cfeeaf" stroke="#69adbd" stroke-width="4"/>',
           '<path d="M55 135 Q165 73 330 125 Q399 156 477 141 Q454 223 369 244 Q272 276 287 372 Q307 445 229 481 Q147 506 88 443 Q138 349 68 287 Q28 234 55 135Z" fill="#e2b98f"/>',
           '<path d="M1170 76 Q1330 45 1530 85 L1570 418 Q1493 472 1450 435 Q1410 389 1358 418 Q1298 445 1280 365 Q1250 305 1158 316 Q1100 311 1113 259 Q1165 205 1137 160Z" fill="#e2b98f"/>',
           '<path d="M739 637 Q775 600 831 620 Q887 584 918 635 Q962 668 932 720 Q955 767 900 790 Q838 780 801 818 Q755 835 725 781 Q697 738 739 637Z" fill="#e2b98f"/>',
           '<path d="M291 507 Q317 459 381 478 Q455 428 498 486 Q545 533 507 579 Q441 583 414 620 Q351 643 313 595Z" fill="#e2b98f"/>',
           '<path d="M483 252 Q532 222 594 255 Q624 299 589 327 Q555 359 500 336 Q465 305 483 252Z" fill="#b8e4ec" stroke="#69adbd" stroke-width="3"/>',
           '<path d="M1051 819 Q1117 779 1173 831 Q1199 872 1171 915 Q1128 953 1077 920 Q1035 882 1051 819Z" fill="#cfeeaf" stroke="#69adbd" stroke-width="4"/>',
           '<path d="M1348 755 Q1393 710 1456 745 Q1505 784 1481 843 Q1450 898 1382 873 Q1334 848 1348 755Z" fill="#cfeeaf" stroke="#69adbd" stroke-width="4"/>',
           '<path d="M846 927 Q875 900 913 926 Q940 953 912 978 Q877 1000 850 976 Q829 953 846 927Z" fill="#cfeeaf" stroke="#69adbd" stroke-width="3"/>',
           '<ellipse cx="941" cy="988" rx="14" ry="9" fill="#cfeeaf" stroke="#69adbd" stroke-width="2"/><ellipse cx="847" cy="1010" rx="12" ry="8" fill="#cfeeaf" stroke="#69adbd" stroke-width="2"/>']
    # Subtle forest groves: decorative, kept clear of roads and labels.
    for cx, cy, cols, rows in [(515,407,4,3),(560,538,3,2),(955,375,3,2),(110,550,3,2)]:
        for j in range(rows):
            for i in range(cols):
                x,y=cx+i*19+(j%2)*8,cy+j*20
                out.append(f'<path d="M{x} {y-12} l-10 18 h6 l-8 9 h24 l-8 -9 h6Z" fill="#7eb682" opacity=".45"/>')
    for path, maps in ROADS:
        out.append(f'<g><title>{escape(" / ".join(maps))}</title><path d="{path}" fill="none" stroke="#929d8d" stroke-width="18" stroke-linejoin="round" stroke-linecap="square"/><path d="{path}" fill="none" stroke="#fffbe9" stroke-width="10" stroke-linejoin="round" stroke-linecap="square"/></g>')
    for path, a, b in PASSAGES:
        out.append(f'<g><title>{escape(a)} to {escape(b)} — guided passage</title><path d="{path}" fill="none" stroke="#769795" stroke-width="8" stroke-linejoin="round" opacity=".7"/><path d="{path}" fill="none" stroke="#fffbe9" stroke-width="4" stroke-dasharray="8 9" stroke-linejoin="round" stroke-linecap="round"/></g>')
    for name,x,y,kind,dx,dy,anchor in NODES:
        out.append(f'<g id="{name.lower().replace(" ", "-").replace(".", "")}"><title>{escape(name)}</title>')
        if kind in ('city','town','league'):
            fill={'city':'#e96350','town':'#658dcc','league':'#826bb6'}[kind]
            out.append(f'<rect x="{x-19}" y="{y-19}" width="38" height="38" rx="2" fill="{fill}" stroke="#737f73" stroke-width="6"/><path d="M{x-12} {y-11} H{x+11}" stroke="#fff" stroke-width="3" opacity=".35"/>')
        else:
            out.append(f'<circle cx="{x}" cy="{y}" r="20" fill="#66b77c" stroke="#737f73" stroke-width="6"/>')
            if kind=='cave':
                out.append(f'<path d="M{x-10} {y+9} V{y-1} Q{x} {y-19} {x+10} {y-1} V{y+9}Z" fill="#425e54"/><path d="M{x-13} {y+10} H{x+13}" stroke="#d5e6bb" stroke-width="3"/>')
            else:
                out.append(f'<path d="M{x} {y-12} l-10 16 h7 v8 h6 v-8 h7Z" fill="#e7f1cc"/>')
        if labels:
            out.append(f'<text x="{x+dx}" y="{y+dy}" text-anchor="{anchor}" class="place">{escape(name)}</text>')
        out.append('</g>')
    if labels:
        out.append('<style>text{font-family:"DejaVu Sans",sans-serif;fill:#263e3e}.place{font-size:23px;font-weight:700;paint-order:stroke;stroke:#e6efcf;stroke-width:5px;stroke-linejoin:round}.route{font-size:18px;font-weight:750;text-anchor:middle;dominant-baseline:central}</style>')
        for x,y,t in BADGES:
            width=22+len(t)*9
            out.append(f'<rect x="{x-width/2}" y="{y-14}" width="{width}" height="28" rx="6" fill="#fffbea" stroke="#a9ad98" stroke-width="1.5"/><text x="{x}" y="{y+1}" class="route">{t}</text>')
        out.extend([
            '<text x="78" y="79" font-size="34" font-weight="800" letter-spacing="5">PLASTIC OX</text><text x="79" y="109" font-size="15" letter-spacing="5">TOWN MAP</text>',
            '<g transform="translate(112 259)"><path d="M0 -55 L9 -9 L0 0 L-9 -9Z" fill="#334e4d"/><path d="M0 55 L-9 9 L0 0 L9 9Z" fill="#fffbea" stroke="#334e4d" stroke-width="2"/><path d="M-40 0 L0 -7 L40 0 L0 7Z" fill="#334e4d"/><circle r="4" fill="#fffbea"/><text y="-65" text-anchor="middle" font-size="19" font-weight="700">N</text><text x="-55" y="6" text-anchor="middle" font-size="14">W</text><text x="55" y="6" text-anchor="middle" font-size="14">E</text></g>',
            '<g transform="translate(78 1040)"><rect x="-23" y="-30" width="1448" height="67" rx="12" fill="#eff5df" fill-opacity=".88" stroke="#8eb6af"/><rect x="0" y="-9" width="18" height="18" fill="#e96350" stroke="#737f73" stroke-width="3"/><text x="30" y="7" font-size="17">City</text><rect x="122" y="-9" width="18" height="18" fill="#658dcc" stroke="#737f73" stroke-width="3"/><text x="152" y="7" font-size="17">Town</text><circle cx="273" cy="0" r="11" fill="#66b77c" stroke="#737f73" stroke-width="3"/><text x="297" y="7" font-size="17">Landmark / cave</text><path d="M488 0 H534" stroke="#929d8d" stroke-width="12"/><path d="M488 0 H534" stroke="#fffbe9" stroke-width="6"/><text x="550" y="7" font-size="17">Route</text><path d="M662 0 H710" stroke="#769795" stroke-width="7"/><path d="M662 0 H710" stroke="#fffbe9" stroke-width="3" stroke-dasharray="6 6"/><text x="726" y="7" font-size="17">Guided passage</text><text x="1387" y="7" text-anchor="end" font-size="15" fill="#607c75">REGIONAL OVERVIEW · NOT TO SCALE</text></g>'
        ])
    out.append('</svg>')
    return '\n'.join(out)


def main():
    (OUT/'plastic_ox_town_map.svg').write_text(render(True))
    (OUT/'plastic_ox_town_map_unlabeled.svg').write_text(render(False))
    (OUT/'layout.json').write_text(json.dumps({'canvas':[W,H], 'nodes':[{'name':n,'position':[x,y],'kind':k} for n,x,y,k,*_ in NODES], 'route_corridors':[{'path':p,'maps':m} for p,m in ROADS], 'guided_passages':[{'path':p,'from':a,'to':b} for p,a,b in PASSAGES]},indent=2)+'\n')
    print(OUT/'plastic_ox_town_map.svg')

if __name__=='__main__':
    main()
