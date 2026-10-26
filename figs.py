import json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon, Arc, FancyArrowPatch
from matplotlib import font_manager as fm

fm.fontManager.addfont('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf')
fm.fontManager.addfont('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf')
plt.rcParams.update({'font.family': 'Liberation Sans', 'font.size': 8})
R = json.load(open('/home/claude/seeder/results.json'))
INK, MUT, ACC, GRD = '#0b0b0b', '#52514e', '#2a78d6', '#9a9890'
OUT = '/home/claude/seeder/'

def dim(ax, p1, p2, txt, off=0, vertical=False, fs=7):
    (x1, y1), (x2, y2) = p1, p2
    if vertical:
        x1 += off; x2 += off
    else:
        y1 += off; y2 += off
    ax.annotate('', xy=(x1, y1), xytext=(x2, y2),
                arrowprops=dict(arrowstyle='<->', lw=0.6, color=MUT, shrinkA=0, shrinkB=0))
    xm, ym = (x1+x2)/2, (y1+y2)/2
    if vertical:
        ax.text(xm+12, ym, txt, rotation=90, va='center', ha='left', fontsize=fs, color=MUT)
    else:
        ax.text(xm, ym+10, txt, ha='center', va='bottom', fontsize=fs, color=MUT)

def save(fig, name):
    fig.savefig(OUT+name, dpi=220, bbox_inches='tight', facecolor='white')
    plt.close(fig)

# ---------------------------------------------------------------- Fig 1 general arrangement
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 8.4), gridspec_kw=dict(height_ratios=[1.25, 1]))
a = a1
a.axhline(0, color=GRD, lw=0.8)
a.fill_between([-450, 1400], -60, 0, color='#efeee9', zorder=0)
# drive wheel
a.add_patch(Circle((0, 200), 210, fill=False, lw=1.0, color=INK))
a.add_patch(Circle((0, 200), 190, fill=False, lw=0.5, color=INK))
for k in range(16):
    t = 2*math.pi*k/16
    a.plot([190*math.cos(t), 210*math.cos(t)], [200+190*math.sin(t), 200+210*math.sin(t)], color=INK, lw=1.4)
a.add_patch(Circle((0, 200), 97, fill=False, lw=0.6, ls='--', color=ACC))
a.add_patch(Circle((0, 200), 25, fill=False, lw=0.8, color=INK))
# frame rail
a.add_patch(Rectangle((-300, 180), 1150, 40, fill=False, lw=1.0, color=INK))
# motors
a.add_patch(Circle((-130, 230), 50, fill=False, lw=0.8, color=MUT))
# battery + electronics
a.add_patch(Rectangle((-300, 225), 160, 175, fill=False, lw=0.9, color=INK)); a.annotate('battery 25.6 V', xy=(-260, 380), xytext=(-460, 470), fontsize=6.5, arrowprops=dict(arrowstyle='-', lw=0.5, color=MUT))
a.add_patch(Rectangle((-110, 260), 100, 80, fill=False, lw=0.7, color=MUT)); a.annotate('MPPT + motor driver', xy=(-60, 340), xytext=(-460, 560), fontsize=6.5, arrowprops=dict(arrowstyle='-', lw=0.5, color=MUT))
# ballast
a.add_patch(Rectangle((147, 280), 100, 40, fill=True, fc='#d6d4cc', lw=0.7, ec=INK)); a.text(197, 300, 'ballast', ha='center', va='center', fontsize=6)
# canopy
for x in (-200, 800):
    a.plot([x, x], [220, 1000], color=INK, lw=1.0)
a.plot([-200, 200], [1000, 220], color=MUT, lw=0.6); a.plot([800, 400], [1000, 220], color=MUT, lw=0.6)
a.add_patch(Rectangle((-250, 1000), 1156, 30, fc='#cfe0f5', ec=INK, lw=0.9))
a.text(328, 1060, 'PV canopy: 2 x 100 W modules (865 x 578 x 30 each), 1156 long', ha='center', fontsize=6.5)
# row unit
a.add_patch(Rectangle((380, 150), 220, 30, fill=False, lw=0.7, color=MUT))
a.add_patch(Polygon([(430, 180), (560, 180), (560, 120), (500, 60), (440, 60)], closed=True, fill=False, lw=0.8, color=INK))
a.add_patch(Arc((470, 85), 250, 250, theta1=-180+47, theta2=360-47-180+180, lw=1.0, color=INK))
a.add_patch(Circle((470, 85), 125, fill=False, lw=0.6, ls=':', color=INK))
a.add_patch(Circle((510, 100), 100, fill=False, lw=0.9, color=ACC))
a.add_patch(Circle((520, 330), 70, fill=False, lw=0.9, color=INK)); a.text(520, 330, 'meter', ha='center', va='center', fontsize=6)
a.add_patch(Polygon([(460, 420), (580, 420), (630, 600), (410, 600)], closed=True, fill=False, lw=0.9, color=INK)); a.text(520, 520, 'hopper\n3 L', ha='center', va='center', fontsize=6)
a.plot([520, 525, 535], [260, 100, -30], color=ACC, lw=1.2)
# press wheel + arm
a.plot([820, 880], [200, 125], color=INK, lw=1.2)
a.add_patch(Circle((880, 125), 125, fill=False, lw=0.9, color=INK))
# handlebar
a.plot([850, 1250], [200, 900], color=INK, lw=1.4); a.plot([1250, 1330], [900, 900], color=INK, lw=2.0)
# labels
a.text(0, -110, 'drive wheel\nØ420 over lugs', ha='center', va='top', fontsize=6.5)
a.text(470, -110, 'opener Ø250\n+ gauge wheel Ø200', ha='center', va='top', fontsize=6.5)
a.text(880, -110, 'press wheel\nØ250 (swivel-lock)', ha='center', va='top', fontsize=6.5)
dim(a, (0, -270), (880, -270), 'wheelbase 880 (drive axle to press wheel)')
dim(a, (-300, 1130), (1330, 1130), 'overall length ≈ 1630 (handle grips)')
dim(a, (1370, 0), (1370, 1030), 'height 1030', vertical=True)
a.annotate('travel', xy=(-300, 1180), xytext=(-120, 1180), arrowprops=dict(arrowstyle='->', color=INK, lw=1.0), fontsize=7, va='center')
a.set_xlim(-470, 1440); a.set_ylim(-320, 1230); a.set_aspect('equal'); a.axis('off')
a.set_title('Side view (mm). Origin: drive-axle centre line at ground level; x positive rearward.', fontsize=8, loc='left')
# top view
a = a2
for zs in (1, -1):
    a.add_patch(Rectangle((-300, zs*110 if zs > 0 else -150), 1150, 40, fill=False, lw=1.0, color=INK))
    a.add_patch(Rectangle((-210, 200 if zs > 0 else -300), 420, 100, fill=False, lw=1.0, color=INK))
for x in (-280, 260, 380, 600, 830):
    a.add_patch(Rectangle((x-20, -110), 40, 220, fill=False, lw=0.8, color=INK))
a.add_patch(Rectangle((-250, -432.5), 1156, 865, fill=False, lw=0.7, ls='--', color=ACC))
a.plot([-450, 1400], [0, 0], color=GRD, lw=0.6, ls='-.')
a.plot([470-125*math.cos(math.radians(5)), 470+125*math.cos(math.radians(5))],
       [-125*math.sin(math.radians(5)), 125*math.sin(math.radians(5))], color=INK, lw=2.0)
a.add_patch(Rectangle((460, 20), 100, 50, fill=False, lw=0.8, color=ACC))
a.add_patch(Rectangle((850, -30), 60, 60, fill=False, lw=0.8, color=INK))
a.plot([850, 1250], [130, 200], color=INK, lw=1.2); a.plot([850, 1250], [-130, -200], color=INK, lw=1.2)
a.plot([1250, 1250], [-200, 200], color=INK, lw=1.0)
dim(a, (-380, -250), (-380, 250), 'track 500', vertical=True)
dim(a, (-250, 470), (906, 470), 'canopy 1156 x 865 (dashed)')
dim(a, (1000, -150), (1000, 150), 'frame 300', vertical=True)
a.text(560, -360, 'opener at 5° gang angle; gauge wheel (blue)', ha='center', fontsize=6.5)
a.text(1290, 0, 'row\ncentre', fontsize=6, va='center', color=MUT)
a.set_xlim(-470, 1400); a.set_ylim(-560, 560); a.set_aspect('equal'); a.axis('off')
a.set_title('Top view (mm). Wheels run on inter-row mid-lines (±250 mm), never on a seed row.', fontsize=8, loc='left')
save(fig, 'fig1_ga.png')

# ---------------------------------------------------------------- Fig 2 seed plate
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.6), gridspec_kw=dict(width_ratios=[1.5, 1]))
Ro, dep, Lc = 70, 6.0, 15.5
ang_half = math.degrees(Lc/2/Ro)
pts = []
for k in range(12):
    c = 90 - k*30
    for t in [c+15-0.01*0, ]:
        pass
# build outline
import numpy as np
outline = []
for k in range(12):
    c = 90 - k*30
    a0, a1_ = c+ang_half, c-ang_half
    # land from previous cell end to this cell start
    prev_end = c + 30 - ang_half
    for t in np.linspace(prev_end, a0, 12):
        outline.append((Ro*math.cos(math.radians(t)), Ro*math.sin(math.radians(t))))
    # notch (rounded bottom)
    rb = Ro-dep
    for t in np.linspace(a0, a1_, 8):
        outline.append((rb*math.cos(math.radians(t)), rb*math.sin(math.radians(t))))
outline.append(outline[0])
xs, ys = zip(*outline)
a.plot(xs, ys, color=INK, lw=1.0)
a.add_patch(Circle((0, 0), 6, fill=False, lw=0.8, color=INK))
for k in range(3):
    t = math.radians(90+120*k)
    a.add_patch(Circle((15*math.cos(t), 15*math.sin(t)), 2.2, fill=False, lw=0.7, color=INK))
a.add_patch(Circle((0, 0), 15, fill=False, lw=0.4, ls='-.', color=MUT))
a.add_patch(Circle((0, 0), 70.75, fill=False, lw=0.5, ls='--', color=ACC))
dim(a, (-70, -88), (70, -88), 'Ø140.0 OD')
a.text(0, -26, 'bore Ø12 H7', ha='center', fontsize=6.5)
a.text(24, 17, '3x Ø4.5 on PCD 30', fontsize=6.5)
a.text(-128, 92, 'cell (x12, 30° pitch):\nlength 15.5 along rim\nradial depth 6.0\nfull plate width 10.5\nR1.5 lead-in edges', fontsize=6.5, va='top')
a.text(48, 62, 'housing shroud\n(radial clearance 0.75)', fontsize=6, color=ACC)
a.annotate('rotation', xy=(55, -50), xytext=(68, -30), arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.3', color=INK), fontsize=6.5)
a.text(-28, 30, 'FILL ZONE\n(hopper above)', fontsize=6, color=MUT, ha='center')
a.text(0, -48, 'DISCHARGE\n(6 o\'clock)', fontsize=6, color=MUT, ha='center')
a.set_xlim(-130, 110); a.set_ylim(-100, 100); a.set_aspect('equal'); a.axis('off')
a.set_title('Front view (mm)', fontsize=8, loc='left')
# section
b.add_patch(Rectangle((0, -70), 10.5, 140, fill=False, lw=1.0, color=INK))
b.add_patch(Rectangle((0, 64), 10.5, 6, fc='white', ec=INK, lw=0.6, hatch=None))
b.add_patch(Rectangle((0, -6), 10.5, 12, fc='#e6e5e0', ec=INK, lw=0.6))
b.add_patch(Rectangle((-8, -15), 8, 30, fill=False, lw=0.8, color=ACC))
b.text(-4, -22, 'Al hub\nflange', ha='center', va='top', fontsize=6, color=ACC)
dim(b, (0, 82), (10.5, 82), '10.5')
dim(b, (16, 64), (16, 70), '6', vertical=True)
b.text(14, -40, 'POM-C\n(acetal)\nor PETG print\nfor first trials', fontsize=6.5)
b.set_xlim(-25, 50); b.set_ylim(-100, 95); b.set_aspect('equal'); b.axis('off')
b.set_title('Section A-A', fontsize=8, loc='left')
save(fig, 'fig2_plate.png')

# ---------------------------------------------------------------- Fig 3 opener + gauge
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.8), gridspec_kw=dict(width_ratios=[1.45, 1]))
a.axhline(0, color=GRD, lw=0.8); a.fill_between([-200, 260], -90, 0, color='#efeee9', zorder=0)
d = 40
a.add_patch(Circle((0, 125-d), 125, fill=False, lw=1.1, color=INK))
a.add_patch(Circle((0, 125-d), 50, fill=False, lw=0.6, ls='--', color=MUT))
a.add_patch(Circle((40, 100), 100, fill=False, lw=1.0, color=ACC))
a.plot([0], [125-d], 'k+', ms=6); a.plot([40], [100], '+', color=ACC, ms=6)
dim(a, (-150, 0), (-150, -d), f'd = {d}', vertical=True)
a.text(150, 92, 'Δ = 15 mm\n(gauge axle above\ndisc axle)', fontsize=6, color=ACC, va='center')
a.add_patch(Rectangle((25, 60), 30, 90, fill=False, lw=0.7, color=ACC, ls='--'))
a.plot([40, 40], [150, 215], color=ACC, lw=1.0); a.text(46, 205, 'M10x1.5 depth screw\n1.5 mm depth / turn', fontsize=6, color=ACC)

a.plot([60, 75], [-d, -d+10], color=ACC, lw=1.2); a.text(70, -60, 'seed boot outlet\n10 mm above furrow floor', fontsize=6, color=ACC)
a.text(-175, -75, 'Disc Ø250 x 4, hardened steel, 15° single bevel; clamp flange Ø100', fontsize=6)
a.set_xlim(-200, 260); a.set_ylim(-90, 240); a.set_aspect('equal'); a.axis('off')
a.set_title('Side view at 40 mm depth (mm)', fontsize=8, loc='left')
# top view gang angle
t = math.radians(5)
b.plot([-125*math.cos(t), 125*math.cos(t)], [-125*math.sin(t), 125*math.sin(t)], color=INK, lw=2.4)
b.plot([-150, 150], [0, 0], color=GRD, lw=0.6, ls='-.')
b.add_patch(Rectangle((-10, 8), 100, 50, fill=False, lw=1.0, color=ACC))
b.add_patch(Arc((0, 0), 260, 260, theta1=0, theta2=5, color=MUT, lw=0.7)); b.text(132, -12, '5°', fontsize=7)
b.annotate('', xy=(-140, -40), xytext=(-60, -40), arrowprops=dict(arrowstyle='->', color=INK)); b.text(-100, -55, 'travel', ha='center', fontsize=6.5)
b.text(-150, 100, 'gauge wheel 200 x 50,\n3 mm from disc face', fontsize=6.5, color=ACC, va='top')
b.text(-150, -88, 'depth  d = R_disc − R_gauge + Δ = 125 − 100 + Δ\nΔ = gauge-axle height above disc axle\n(5 → 25 mm gives d = 30 → 50 mm)', fontsize=6.5, va='top')
b.set_xlim(-160, 160); b.set_ylim(-140, 110); b.set_aspect('equal'); b.axis('off')
b.set_title('Top view: gang angle', fontsize=8, loc='left')
save(fig, 'fig3_opener.png')

# ---------------------------------------------------------------- Fig 4 frame
fig, a = plt.subplots(figsize=(7.2, 3.6))
def tube(x, z, L, W, horiz=True, lab=None):
    if horiz: a.add_patch(Rectangle((x, z), L, W, fill=False, lw=1.0, color=INK))
    else: a.add_patch(Rectangle((x, z), W, L, fill=False, lw=1.0, color=INK))
tube(-300, 110, 1150, 40); tube(-300, -150, 1150, 40)
cms = [(-300, 'CM1'), (240, 'CM2'), (360, 'CM3'), (580, 'CM4'), (810, 'CM5')]
for x, n in cms:
    a.add_patch(Rectangle((x, -110), 40, 220, fill=False, lw=0.9, color=INK))
    a.text(x+20, 0, n, rotation=90, ha='center', va='center', fontsize=6.5)
for zs in (1, -1):
    a.add_patch(Rectangle((-70, zs*150 if zs > 0 else -156), 140, 6, fc=ACC, ec=ACC))
    a.add_patch(Rectangle((-70, zs*104 if zs > 0 else -110), 140, 6, fc=ACC, ec=ACC))
    for x in (-200, 800):
        a.add_patch(Rectangle((x-12.5, zs*130-12.5), 25, 25, fc='#d6d4cc', ec=INK, lw=0.6))
a.add_patch(Rectangle((147, -150), 90, 300, fill=False, lw=0.7, ls='--', color=MUT)); a.text(192, 175, 'ballast tray (on top of rails)', ha='center', va='bottom', fontsize=6, color=MUT)
for xm, zm in ((-130, 30), (110, -40)):
    a.add_patch(Circle((xm, zm), 50, fill=False, lw=0.7, ls=':', color=MUT)); a.text(xm, zm, 'motor', ha='center', va='center', fontsize=6, color=MUT)
a.add_patch(Rectangle((380, -60), 220, 120, fill=False, lw=0.7, ls=':', color=MUT)); a.text(490, 75, 'row-unit hanger', ha='center', fontsize=6, color=MUT)
dim(a, (-300, 200), (850, 200), '1150 side rails (40x40x2)')
dim(a, (-360, -150), (-360, 150), '300 o/s', vertical=True)
dim(a, (950, -110), (950, 110), '220 CM length', vertical=True)
for x, n in cms:
    a.text(x+20, -175, f'{x+20}', ha='center', fontsize=6, color=MUT)
a.text(-300, -205, 'x-position of cross-member centre lines (mm from drive axle; CM1/CM5 flush with rail ends). Blue: 6 mm axle plates. Grey: canopy post sockets.', fontsize=6, color=MUT)
a.set_xlim(-400, 1010); a.set_ylim(-220, 240); a.set_aspect('equal'); a.axis('off')
a.set_title('Chassis frame weldment, plan view (mm)', fontsize=8, loc='left')
save(fig, 'fig4_frame.png')

# ---------------------------------------------------------------- Fig 5 drive wheel
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.8), gridspec_kw=dict(width_ratios=[1.3, 1]))
a.add_patch(Circle((0, 0), 190, fill=False, lw=1.0, color=INK)); a.add_patch(Circle((0, 0), 187, fill=False, lw=0.5, color=INK))
for k in range(16):
    th = 2*math.pi*k/16
    a.plot([190*math.cos(th), 210*math.cos(th)], [190*math.sin(th), 210*math.sin(th)], color=INK, lw=2.2)
for k in range(4):
    th = math.radians(45+90*k)
    a.add_patch(Circle((110*math.cos(th), 110*math.sin(th)), 40, fill=False, lw=0.8, color=INK))
a.add_patch(Circle((0, 0), 25, fill=False, lw=1.0, color=INK)); a.add_patch(Circle((0, 0), 12.5, fill=False, lw=0.8, color=INK))
a.add_patch(Rectangle((-4, 12.5-0.5), 8, 4.3, fill=False, lw=0.6, color=INK))
a.add_patch(Circle((0, 0), 110, fill=False, lw=0.4, ls='-.', color=MUT))
dim(a, (-210, -235), (210, -235), 'Ø420 over lugs')
dim(a, (-190, 230), (190, 230), 'Ø380 rim OD')

a.text(-340, 200, 'hub Ø50\nbore Ø25 H7\nkeyway 8 x 3.3\n(DIN 6885)\n\nweb holes\n4x Ø80\non PCD 220', fontsize=6, va='top')
a.text(200, 200, '16 lugs\n20 x 5 x 100\n22.5° pitch', fontsize=6)
a.set_xlim(-345, 300); a.set_ylim(-260, 260); a.set_aspect('equal'); a.axis('off')
a.set_title('Front view (mm)', fontsize=8, loc='left')
b.add_patch(Rectangle((0, 187), 100, 3, fc='#d6d4cc', ec=INK, lw=0.7))
b.add_patch(Rectangle((0, 190), 100, 20, fill=False, ec=INK, lw=0.8))
b.add_patch(Rectangle((48, 25), 4, 162, fc='#d6d4cc', ec=INK, lw=0.7))
b.add_patch(Rectangle((20, 12.5), 60, 12.5, fc='#d6d4cc', ec=INK, lw=0.7))
b.plot([-30, 130], [0, 0], color=GRD, lw=0.6, ls='-.')
dim(b, (0, 225), (100, 225), '100 rim width')
dim(b, (20, -25), (80, -25), '60 hub')
dim(b, (110, 190), (110, 210), '20 lug', vertical=True)
b.text(55, 110, 'web 4 mm\n(centred)', fontsize=6.5)
b.text(-30, 150, 'rim band\n3 mm, rolled\nand butt-welded', fontsize=6.5)
b.text(84, 40, 'fillet\nwelds 4 mm\nboth sides', fontsize=6)
b.set_xlim(-40, 150); b.set_ylim(-35, 250); b.set_aspect('equal'); b.axis('off')
b.set_title('Half section (mm)', fontsize=8, loc='left')
save(fig, 'fig5_wheel.png')

# ---------------------------------------------------------------- Fig 6 energy cascade (single series bar)
casc = R['cascade']
fig, a = plt.subplots(figsize=(7.2, 2.9))
labels = [c[0] for c in casc][::-1]; vals = [c[1] for c in casc][::-1]
bars = a.barh(range(len(vals)), vals, color=ACC, height=0.6)
for i, v in enumerate(vals):
    a.text(v+12, i, f'{v:.0f} W', va='center', fontsize=7, color=INK)
a.set_yticks(range(len(vals))); a.set_yticklabels(labels, fontsize=7, color=INK)
a.set_xlim(0, 1150); a.set_xlabel('Power (W), 1000 W/m² on 1.0 m² of modules, nominal speed', fontsize=7, color=MUT)
for s in ('top', 'right'): a.spines[s].set_visible(False)
for s in ('left', 'bottom'): a.spines[s].set_color(GRD)
a.tick_params(colors=MUT, labelsize=7)
a.xaxis.grid(True, color='#e6e5e0', lw=0.5); a.set_axisbelow(True)
save(fig, 'fig6_energy.png')
print('ok')
