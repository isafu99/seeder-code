"""Clearance and geometry checks for the full-size planter, in the frame's coordinates.
R = distance rearward of toolbar centre-line (mm), H = height above ground (mm), S = sideways from centre-line (mm).
Checks the ORIGINAL report wheel layout and the REVISED layout used in the modelling guide."""
import math

def circ_pt_dist(c, r, p):
    return math.hypot(p[0]-c[0], p[1]-c[1]) - r      # >0: point outside circle

def tyre_centres(piv, L, lift_deg, n=41):
    return [(piv[0] + L*math.cos(math.radians(-a)), piv[1] + L*math.sin(math.radians(-a)))
            for a in [lift_deg*i/(n-1) for i in range(n)]]

r_tyre, w_tyre, S_lane = 401.5, 209.0, 1500.0
rail_out, rail_in = 1500 + 50.8, 1500 - 50.8
rail_bot, rail_top = 273.0, 527.0
print('--- ORIGINAL REPORT LAYOUT: pivot R1300 H400, arm 450, lift 40 deg, rail to R1350 ---')
cs = tyre_centres((1300, 400), 450, 40)
corner = (1350, rail_bot)
d = min(circ_pt_dist(c, r_tyre, corner) for c in cs)
print(f'rail end bottom corner vs tyre (both in the S1449-1551 band): {d:.0f} mm  ->', 'CLASH' if d < 0 else 'ok')
d2 = min(circ_pt_dist(c, r_tyre, (1300, 400)) for c in cs)
print(f'pivot centre to tyre surface: {d2:.1f} mm (any bracket in the tyre band larger than this radius clashes)')

print('\n--- REVISED LAYOUT: pivot R1400 H401.5, arm 600, lift 28.8 deg, rail to R1460 ---')
piv = (1400, 401.5); L = 600; lift = math.degrees(math.asin(289/600))
cs = tyre_centres(piv, L, lift)
for name, p in (('rail end bottom corner', (1460, rail_bot)), ('rail end top corner', (1460, rail_top)),
                ('pivot sleeve edge (r=50)', None), ('arm pivot tube edge (r=55)', None)):
    if p is None:
        rr = 50 if 'sleeve' in name else 55
        dd = min(circ_pt_dist(c, r_tyre, piv) for c in cs) - rr
    else:
        dd = min(circ_pt_dist(c, r_tyre, p) for c in cs)
    print(f'{name} vs tyre: {dd:.0f} mm ->', 'CLASH' if dd < 0 else 'ok')
print(f'lift angle for 289 mm: {lift:.1f} deg')
# tyre lateral band vs closing wheels (S1140-1360 and 1640-1860, R985-1315, H0-330)
tyre_S = (S_lane - w_tyre/2, S_lane + w_tyre/2)
print(f'tyre band S {tyre_S[0]:.1f}-{tyre_S[1]:.1f}; closing wheels end at S1360 / start at S1640 -> lateral gaps {tyre_S[0]-1360:.1f} / {1640-tyre_S[1]:.1f} mm')
fwd_tyre_transport = min(c[0] for c in cs) - r_tyre
print(f'most-forward tyre point (any lift position): R {fwd_tyre_transport:.0f} (closing wheels end at R1315)')
# arm (S1620-1720, H 326.5-476.5, front end rounded r75 about pivot) vs closing wheel of row 1.75 (S1640-1860, R<=1315, H<=330)
print(f'arm front end at R {piv[0]-75:.0f} vs closing wheel rear R1315 -> {piv[0]-75-1315:.0f} mm')
print(f'arm inner face S1620 vs tyre outer sidewall S{tyre_S[1]:.1f} -> {1620-tyre_S[1]:.1f} mm')
# cylinder: base pin (1200,700), rod pin on arm top 250 behind pivot (rel (250,95))
base = (1150, 740); rel = (250, 95)   # base pin on the extended ballast-beam end (R1150, H740)
def rod_pt(a):
    t = math.radians(-a)
    return (piv[0] + rel[0]*math.cos(t) - rel[1]*math.sin(t), piv[1] + rel[0]*math.sin(t) + rel[1]*math.cos(t))
for lab, a in (('work', 0.0), ('transport', lift)):
    rp = rod_pt(a); Lc = math.hypot(rp[0]-base[0], rp[1]-base[1])
    ux, uz = (rp[0]-base[0])/Lc, (rp[1]-base[1])/Lc
    lever = abs(ux*(piv[1]-base[1]) - uz*(piv[0]-base[0]))
    Hline = base[1] + uz*((piv[0]-base[0])/ux)
    print(f'cylinder {lab}: rod pin at R{rp[0]:.0f} H{rp[1]:.0f}; pin-to-pin {Lc:.0f} mm; lever about pivot {lever:.0f} mm; '
          f'cylinder axis height above pivot point R1400: H{Hline:.0f} (body bottom {Hline-40:.0f} vs arm pivot tube top {piv[1]+55:.0f})')
# canopy brace geometry
posts = {'FL': (-1750, -680), 'FR': (-1750, 680), 'RL': (-750, -1148.4), 'RR': (-750, 1148.4)}
Hb, Ht = 527.0, 1554.6
def L3(a, b): return math.dist(a, b)
side = L3((-1750, 680, Ht), (-750, 1148.4, Hb)); front = L3((-1750, -680, Ht), (-1750, 680, Hb)); rear = L3((-750, -1148.4, Ht), (-750, 1148.4, Hb))
print(f'\ncanopy: post length {Ht-Hb:.1f}; brace lengths side {side:.0f} (x2), front cross {front:.0f}, rear cross {rear:.0f}')
E = 200e9; A = (50.8**2 - 41.28**2)*1e-6; m = 96.0
k_lat = E*A/(front/1000)*(1360/front)**2 + E*A/(rear/1000)*(2296.8/rear)**2
k_fa = 2*E*A/(side/1000)*(1000/side)**2
print(f'canopy lateral mode ~{math.sqrt(k_lat/m)/(2*math.pi):.0f} Hz, fore-aft mode ~{math.sqrt(k_fa/m)/(2*math.pi):.0f} Hz (braces axial only; joints will lower this)')
# gauge arm geometry
P = (470, 345); disc_c, disc_r = (550, 140.5), 190.5
for dmm in (25, 50, 75):
    z = 140.5 + dmm; La = math.hypot(590-470, 190.5-345)
    x = P[0] + math.sqrt(La**2 - (P[1]-z)**2)
    print(f'gauge arm (length {La:.1f}): depth {dmm} mm -> gauge axle at R{x:.0f} H{z:.1f}')
print(f'gauge pivot shaft (r10) clearance to disc rim: {math.hypot(P[0]-disc_c[0], P[1]-disc_c[1]) - disc_r - 10:.0f} mm')
# disc gap and seed tube
toe = math.radians(5.5); x_conv = 190.5*math.cos(math.radians(45))
for dx in (0, 25, 50):
    print(f'gap between disc inner faces {dx} mm behind disc axle: {2*(x_conv+dx)*math.tan(toe):.1f} mm')
# hanger plate vs gusset; rail vs gauge wheels; hopper vs rail
print(f'\nrail inner face S{rail_in:.1f} vs row-1.25 gauge-wheel envelope S1415 -> {rail_in-1415:.1f} mm')
print(f'hanger plates of rows 1.25/1.75 end at S1360 / start at S1640; gusset (12 thick) at S1494-1506 -> {1494-1360} / {1640-1506} mm')
print(f'hopper bottom H760 vs rail top H{rail_top:.0f} -> {760-rail_top:.0f} mm; vs upper link top H730 -> 30 mm (+/-19 mm link swing)')
t = math.sqrt(2*0.450/9.81); print(f'seed drop with meter centre at H470: 450 mm, {t:.3f} s, spacing scatter +/-{0.15*t*1.667*1000:.0f} mm at 6 km/h')
print(f'meter gearmotor bottom H{470-45} vs gauge-wheel top at 75 mm depth H{215.5+190.5:.0f}')

# row-unit float: closing wheels (top H330) rising 100 mm, vs anything above them in S1640-1860, R985-1315
print(f"\nclosing wheel top at +100 mm float: H430; ballast-beam strut at S1640 is at H{450 + 148*(1640-1551)/210:.0f}; beam end bottom H598")
# ballast-beam end with cylinder clevis: stresses (2.5 x transport cylinder force), strut takes the vertical part
F = 48.2e3*2.5
Fx, Fz = F*0.81, F*0.585
M_v = Fx*0.16; T = Fx*(0.740-0.649)
S_v = 128226e-9; Am_t = 146.05*95.25*6.35*2*1e-9
sig = M_v/S_v/1e6; tau = T/Am_t/1e6
print(f"beam end: bending {sig:.0f} MPa, torsion {tau:.0f} MPa, von Mises {math.sqrt(sig**2+3*tau**2):.0f} MPa vs Fy 317")
L_s = math.hypot(210, 148); print(f"strut length {L_s:.0f} mm at {math.degrees(math.atan(148/210)):.0f} deg; axial force {Fz/math.sin(math.atan(148/210))/1000:.0f} kN")
