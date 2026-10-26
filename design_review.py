"""Systematic review of the full-size planter modelling guide. Coordinates: R rearward of toolbar centre-line,
H height above ground, S sideways from machine centre-line; s = sideways from a row's own centre-line (mm).
Each check prints PASS / FAIL with the margin. 'GUIDE' = value as written in the guide; 'FIX' = corrected value."""
import math
rows = []
def chk(area, item, margin, need=0.0, note=''):
    ok = margin >= need
    rows.append((area, item, margin, ok, note))
tan55 = math.tan(math.radians(5.5))
R_contact = 550 - 190.5*math.cos(math.radians(45))          # where the discs touch
half_gap = lambda R: (R - R_contact)*tan55                  # disc inner face, s

# ---------------- FRAME
chk('Frame', 'Toolbar underside sits on rail tops (gap, mm; should be 0)', -abs((616-88.9) - (400+127)), -0.05,
    'GUIDE: toolbar underside H527.1, rail top H527.0 -> 0.1 gap. FIX: mate them; toolbar centre H615.9')
leg_ang = math.degrees(math.atan(1500/3200))
chk('Frame', 'Front-leg end cut at nose plate: guide said "cut square"', -1, 0,
    f'FIX: end is cut at {leg_ang:.1f} deg to the tube axis so it lies flat on the crosswise nose plate')
S_leg = 1500*(3200-3050)/3200; half_w = 101.6/2/math.cos(math.radians(leg_ang))
chk('Frame', 'Nose plate covers leg ends (outer face S vs plate edge S130)', 130 - (S_leg + half_w), 3)
Ls = 1500*(3200-1600)/3200 - half_w
chk('Frame', 'Cross brace length between leg faces', 2*Ls, 0, f'{2*Ls:.1f} mm; end cut {90-leg_ang:.1f} deg')
chk('Frame', 'Pivot-sleeve hole (r50) edge to rail end, GUIDE rail end R1460', 1460 - 1400 - 50, 25,
    'only 10 mm of rail wall behind the hole. FIX: extend rail rear section to R1500 (50 mm) + 10 mm doubler plates')
# PV frame vs panel frame
edge_f, edge_r = -1817, -683
for lab, rail_c in (('GUIDE front rail R-1750', -1750), ('GUIDE rear rail R-750', -750)):
    inner = abs(rail_c - (edge_f if rail_c < -1250 else edge_r))
    chk('Frame', f'{lab}: rail under the panel frame flange (35 wide from edge)', 35 - (inner - 25.4), 0,
        f'rail spans {inner-25.4:.0f}-{inner+25.4:.0f} mm from panel edge: panel would rest on its back sheet. '
        'FIX: rail centres 20 mm inside the edges (R-1797, R-703); posts moved to match')
for R in (-1797, -703):
    print(f'  [info] leg centre-line at R{R}: S±{1500*(R+3200)/3200:.1f}')
# braces with posts at R-1797 / -703
Hb, Ht = 527.0, 1554.6
pf, pr = 1500*(3200-1797)/3200, 1500*(3200-703)/3200
side = math.dist((-1797, pf, Ht), (-703, pr, Hb)); front = math.dist((0, -pf, Ht), (0, pf, Hb)); rear = math.dist((0, -pr, Ht), (0, pr, Hb))
print(f'  [info] FIX brace lengths: side {side:.0f} (x2), front cross {front:.0f}, rear cross {rear:.0f}')
H_at = Hb + (Ht-Hb)*(pf-300)/(2*pf)
chk('Frame', 'Front cross brace above electronics box top (H740) at box corner S300', H_at - 740, 20)
chk('Frame', 'Electronics tray supported on two sides (guide: only the cross brace)', -1, 0,
    'FIX: add a 50.8 x 50.8 x 4.76 crosswise bar between the legs at R-1350 as the tray\'s second support')
# ballast bolts
chk('Frame', 'M16x260 through 3 plates + beam (needs 120+101.6+2x3 washers+16 nut+3 thread)', 260 - (120+101.6+6+16+3), 0)
chk('Frame', 'M16x220 through 2 plates + beam', 220 - (80+101.6+6+16+3), 0)
# ballast-beam strut: corrected end points (strut top end inside the beam end, centred S1710)
s_top, s_bot, h_top, h_bot = 1710, 1551, 598.4, 450
ang = math.atan((h_top-h_bot)/(s_top-s_bot))
H_c = h_bot + (h_top-h_bot)*(1640-s_bot)/(s_top-s_bot); low = H_c - 50.8/math.cos(ang)
chk('Frame', 'Strut lower edge over row-1750 closing wheels at +100 mm float (top H430)', low - 430, 15,
    f'strut centre-line from (S{s_top},H{h_top}) to (S{s_bot},H{h_bot}); GUIDE put its top at the beam corner S1761, '
    'which leaves half the tube sticking out past the beam end. Closing-wheel spring hardware height must be checked on the bought part')

# ---------------- ROW UNIT
chk('Row unit', 'Links clear of hopper front (hopper R540, link end R561, link top H730 vs hopper H760)', 760-730, 15)
chk('Row unit', 'Spring (dia 50) beside upper link: GUIDE s±30 -> overlaps lugs (s40-50)', (40) - (30+25), 0,
    'FIX: springs outside the links at s±90 (spans 65-115; links at 50-60)')
chk('Row unit', 'Spring at s±90 vs link outer face (s60)', (90-25) - 60, 3)
# gauge arm pivot vs gauge wheel
La = math.hypot(590-470, 345-190.5)
chk('Row unit', 'GUIDE gauge pivot shaft (r10) vs gauge-wheel tyre (r190.5): arm 195.6', La - 190.5 - 10, 10,
    'the Ø20 cross-shaft passes through the gauge-wheel band and cuts 5 mm into the tyre at every depth. '
    'FIX: pivot at R450 H360, arm 219.8')
Pn = (450, 360); La2 = math.hypot(590-Pn[0], 190.5-Pn[1])
chk('Row unit', 'FIX gauge pivot shaft vs gauge-wheel tyre', La2 - 190.5 - 10, 10)
chk('Row unit', 'FIX gauge pivot shaft vs disc rim', math.hypot(Pn[0]-550, Pn[1]-140.5) - 190.5 - 10, 10)
for d in (25, 75):
    z = 140.5 + d; x = Pn[0] + math.sqrt(La2**2 - (Pn[1]-z)**2)
    print(f'  [info] FIX gauge-wheel axle at depth {d}: R{x:.0f} H{z:.1f}')
# gauge wheel parallel to travel vs disc splay
disc_out_rear = half_gap(740.5) + 5
chk('Row unit', 'GUIDE gauge wheel inner face s±25 (parallel to travel) vs disc outer face at its rear edge', 25 - disc_out_rear, 2,
    f'the disc splays out to s±{disc_out_rear:.1f} at its rear, inside the gauge-wheel circle. FIX: toe each gauge wheel 5.5° to run parallel to its disc, 3 mm off it')
# hub recess in gauge wheel (relative motion with depth)
x25 = Pn[0] + math.sqrt(La2**2 - (Pn[1]-165.5)**2); x75 = Pn[0] + math.sqrt(La2**2 - (Pn[1]-215.5)**2)
off_max = max(math.hypot(x25-550, 165.5-140.5), math.hypot(x75-550, 215.5-140.5))
print(f'  [info] disc hub centre moves up to {off_max:.0f} mm from the gauge-wheel centre over 25-75 mm depth')
print(f'  [info] FIX recess in gauge wheel inner face: Ø >= {2*(off_max+60+5):.0f}, depth >= 65 (hub 39 + nut/cap ~23 + 3)')
chk('Row unit', 'GUIDE recess spec (Ø250 x 45) vs need', 250 - 2*(off_max+60+5), 0,
    'hub sticks out ~62 mm (bearings, nut, cap) and moves relative to the gauge wheel with depth')
# rocker vs lower links
low_link_min = 520 - 30 - 19
chk('Row unit', 'GUIDE rocker (H495) vs lower links (bottom H490, -19 swing)', low_link_min - (495+7.5), 5,
    'FIX: tab 90 mm up from the new pivot, rocker at H450, moved by an M10 screw')
chk('Row unit', 'FIX rocker top H457.5 vs lower link lowest H471', low_link_min - 457.5, 5)
# meter motor vs gauge wheel at 75 depth (gauge centre moves to R616)
chk('Row unit', 'Meter gearmotor underside (H425) vs gauge-wheel top at 75 mm depth', 425 - (215.5+190.5), 10)
# spindle block, bolts, seed tube
chk('Row unit', 'Spindle-block puck (r30) inside bolt-head ring (r47.5 - head r7)', 47.5 - 7 - 30, 5)
chk('Row unit', 'Seed tube (R582-597) behind puck rear edge R580', 582 - 580, 2)
head_tip = half_gap(590) - 4.4
chk('Row unit', 'Bolt-head tips vs 16 mm seed tube at R590', head_tip - 8, 3)
chk('Row unit', 'Bolt-head tips vs 20 mm seed tube at R590 (guide before last fix)', head_tip - 10, 3)
chk('Row unit', 'Facing bolt heads of the two discs at front bolt position', 2*(half_gap(516.4) - 4.4), 5)
# shank box bottom vs disc tops
disc_top = 140.5 + 190.5
chk('Row unit', 'Shank box bottom plate (H340) vs disc tops (H331)', 340 - disc_top, 5)
chk('Row unit', 'Closing-arm pivot inside the box corner (guide: R700 H300, box edge H298 there)', -2, 0,
    'FIX: pivot on a 10 mm lug pair hanging below the box corner, hole at R700 H270')

# ---------------- WHEEL / LIFT (from lift_check.py)
chk('Wheel', 'GUIDE: "everything rises 289 in transport" - discs actually rise', 208 - 289, 0,
    'the frame pivots about the hitch pin. With 75 mm row-unit droop, discs end only 83 mm above ground. '
    'FIX: arm 750 mm (150x100x10), lift 38.2°, toolbar rises 277, disc bottoms 200 above ground')
chk('Wheel', 'Cylinder spec in guide ("closed <=530, stroke >=120") admits cylinders that cannot reach 637', -1, 0,
    'FIX (new layout): pin-to-pin 473 -> 636; choose stroke 203 with closed length 435-470')
chk('Wheel', 'FIX tyre (transport) vs rail end bottom corner R1500', 192, 25)
chk('Wheel', 'Arm front tip (R1325) vs closing wheels (R1315)', 10, 5, 'depends on the bought closing-wheel assembly')
chk('Wheel', 'Hitch vertical load in transport (kg) vs a typical compact-tractor drawbar', -1, 0,
    '1,208 kg with full hoppers: the T4 drawbar rating is unpublished; plant with hoppers emptied for road '
    'transport or add a transport wheel/caster at the hitch')

w = max(len(r[1]) for r in rows)
for area, item, m, ok, note in rows:
    print(f'{"PASS" if ok else "FAIL"}  {area:9s} {item:{w}s}  margin {m:7.1f}')
    if note and not ok: print(f'      -> {note}')
    elif note and 'info' not in note and ok and note.startswith('the'): print(f'      -> {note}')
print(f'\n{sum(1 for r in rows if not r[3])} FAIL / {len(rows)} checks')

print('\n=== Gauge-wheel rework: pivot R430 H345, depth range 25-60 mm ===')
rows.clear()
P = (430.0, 345.0); A50 = (590.0, 190.5); La = math.dist(P, A50)
chk('Gauge', f'pivot shaft vs gauge tyre (arm {La:.1f})', La - 190.5 - 10, 10)
chk('Gauge', 'pivot shaft vs disc rim', math.dist(P, (550, 140.5)) - 190.5 - 10, 10)
axle = {}
for d in (25, 50, 60):
    z = 140.5 + d; axle[d] = (P[0] + math.sqrt(La**2 - (P[1]-z)**2), z)
    print(f'  [info] gauge axle at depth {d}: R{axle[d][0]:.0f} H{z:.1f}')
off = max(math.dist(a, (550, 140.5)) for a in axle.values())
print(f'  [info] recess needed in gauge-wheel inner face: Ø >= {2*(off+65):.0f}, depth >= 65')
top60 = axle[60][1] + 190.5
chk('Gauge', 'GUIDE shank box bottom (H340) vs gauge-wheel tops (box sides at s40-50 are inside the gauge-wheel band)', 340 - top60, 5,
    'FIX: raise the box bottom to H400; only the meter housing (s±20), neck and closing-arm lugs go lower, between the gauge wheels')
chk('Gauge', 'FIX box bottom H400 vs gauge-wheel top at 60 mm depth', 400 - top60, 5)
gi = lambda R: half_gap(R) + 5 + 3                           # gauge-wheel inner face (toed, 3 mm off disc)
chk('Gauge', 'meter housing (s±20) vs gauge inner face at housing bottom R620', gi(620) - 20, 3)
chk('Gauge', 'spindle-block neck (rear edge R570, half-thick 12.9) vs gauge inner face', gi(570) - 12.9, 2)
chk('Gauge', 'GUIDE closing-arm lugs (s±40-50, H270 at R700) inside gauge-wheel band', gi(700) - 50, 0,
    'FIX: closing-arm lugs at s±20-30, between the gauge wheels')
chk('Gauge', 'FIX closing-arm lugs s±30 vs gauge inner face at R700', gi(700) - 30, 3)
# gauge pivot bracket: centre plate s±10, vertical leg R420-440 from H315, horizontal leg H400-430 to box front R500
disc_top = lambda R: 140.5 + math.sqrt(190.5**2 - (550-R)**2)
chk('Gauge', 'pivot bracket leg bottom (H315) vs disc tops at R420-440', 315 - max(disc_top(420), disc_top(440)), 10)
gtop = lambda c, R: c[1] + math.sqrt(max(0, 190.5**2 - (c[0]-R)**2))
chk('Gauge', 'pivot bracket horizontal leg (H400) vs gauge-wheel tops R420-500', 400 - max(gtop(axle[60], R) for R in (420, 460, 500)), 5)
link_low = lambda R: 520 - 30 - 0.25*(531 - R)
chk('Gauge', 'pivot bracket top (H430) vs lower-link sweep at R430-500', min(link_low(R) for R in (430, 465, 500)) - 430, 5)
tab_tip = P[1] + 90
chk('Gauge', 'rocker top (tab tip H435 + 7.5) vs lower-link sweep at R420', link_low(420) - (tab_tip + 7.5), 5)
chk('Gauge', 'meter gearmotor underside H425 vs gauge-wheel top at 60 mm depth', 425 - top60, 10)
ratio = (A50[0]-P[0])/90
print(f'  [info] depth change per mm of tab travel: {ratio:.2f}; M10 adjuster (1.5 mm/turn) = {1.5*ratio:.1f} mm depth per turn')
w = max(len(r[1]) for r in rows)
for area, item, m, ok, note in rows:
    print(f'{"PASS" if ok else "FAIL"}  {item:{w}s}  margin {m:6.1f}')
    if note and not ok: print(f'      -> {note}')
