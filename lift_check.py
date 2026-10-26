"""Transport lift: the frame pivots about the hitch pin, so the toolbar rises less than the wheels drop.
Frame coordinates: R rearward of toolbar, H height (frame-fixed, working position)."""
import math
x_h = -3200.0
def rise_at(R, x_w, dw):            # rise of frame point R when the wheel drops dw relative to the frame
    return dw*(R - x_h)/(x_w - x_h)
print('--- Guide as written: pivot R1400, arm 600, 28.8 deg ---')
x_w = 2000; dw = 289
for R, lab in ((0, 'toolbar'), (550, 'opener discs'), (-1250, 'PV canopy')):
    print(f'{lab}: rises {rise_at(R, x_w, dw):.0f} mm (guide said 289)')
print('disc bottom in transport, row unit at a 75 mm down-stop: '
      f'{-50 + rise_at(550, x_w, dw) - 75:.0f} mm above ground')

print('\n--- Required lift for disc bottoms >= 200 mm above ground (row units hang 75 mm on their down-stop) ---')
need = 50 + 75 + 200
for L in (600, 750, 900):
    x_w = 1400 + L
    dw = need*(x_w - x_h)/(550 - x_h)
    th = math.degrees(math.asin(dw/L)) if dw < L else float('nan')
    print(f'arm {L}: wheel must drop {dw:.0f} mm relative to frame -> arm rotation {th:.1f} deg')

# chosen: arm 750, search rod-lug position for best worst-case lever; base pin fixed at (1150, 740)
L = 750; piv = (1400.0, 401.5); x_w = piv[0] + L
dw = need*(x_w - x_h)/(550 - x_h); th = math.asin(dw/L)
base = (1150.0, 740.0)
def rod(rel, a):
    c, s = math.cos(-a), math.sin(-a)
    return (piv[0] + rel[0]*c - rel[1]*s, piv[1] + rel[0]*s + rel[1]*c)
def lever(rel, a):
    p = rod(rel, a); Lc = math.dist(p, base)
    ux, uz = (p[0]-base[0])/Lc, (p[1]-base[1])/Lc
    return abs(ux*(piv[1]-base[1]) - uz*(piv[0]-base[0])), Lc
best = None
for d in range(150, 451, 10):
    for h in range(75, 301, 5):
        rel = (d, h)
        levs = [lever(rel, th*i/20) for i in range(21)]
        lmin = min(l for l, _ in levs); Lw, Lt = levs[0][1], levs[-1][1]
        # body (r40) must clear arm-pivot tube top (H 401.5+55) at R1400 in both end positions
        ok = True
        for a in (0, th):
            p = rod(rel, a); uz = (p[1]-base[1])/(p[0]-base[0])
            if base[1] + uz*(1400-base[0]) - 40 < 401.5 + 55 + 10: ok = False
        if ok and (best is None or lmin > best[0]):
            best = (lmin, rel, Lw, Lt)
lmin, rel, Lw, Lt = best
Nw = 11.3e3
F = Nw*L*math.cos(th)/1000/(lmin/1000)    # worst-case force at minimum lever (conservative)
print(f'\nchosen: arm {L} mm, rotation {math.degrees(th):.1f} deg, wheel drop {dw:.0f} mm, axle at R{x_w:.0f}')
print(f'rod lug {rel[0]} mm behind pivot, {rel[1]} mm above arm axis; minimum lever {lmin:.0f} mm')
print(f'pin-to-pin {Lw:.0f} (work) -> {Lt:.0f} (transport), stroke used {Lt-Lw:.0f} mm')
for bore in (76.2, 88.9, 101.6):
    cap = math.pi/4*(bore/1000)**2*17.5e6
    print(f'  bore {bore}: capacity {cap/1000:.0f} kN vs need {F/1000:.0f} kN (upper bound, uses minimum lever)')
# tyre in transport vs rail end and closing wheels
c_t = (piv[0] + L*math.cos(th), piv[1] - dw)
for name, p in (('rail end bottom corner (R1460,H273)', (1460, 273)), ('rail end bottom corner if extended (R1500,H273)', (1500, 273))):
    print(f'tyre (transport) vs {name}: {math.dist(c_t, p) - 401.5:.0f} mm')
print(f'tyre most-forward point in transport: R{c_t[0]-401.5:.0f} (closing wheels end R1315, laterally clear anyway)')
print(f'frame pitch in transport: {math.degrees(math.atan(dw/(x_w - x_h))):.1f} deg nose-down; canopy rises {rise_at(-1250, x_w, dw):.0f}; toolbar rises {rise_at(0, x_w, dw):.0f}')
# arm bending, 150x100x10
I = (100*150**3 - 80*130**3)/12; S = I/75
M = 2.5*Nw*L/1000
print(f'arm 150x100x10: M={M/1000:.1f} kN.m, sigma={M*1e3/S:.0f} MPa, n={355/(M*1e3/S):.2f}')

print('\n--- Refined search: standard 203 mm stroke cylinder (closed length assumed 420-460 mm) ---')
best = None
for bx in range(1080, 1221, 10):
    for bz in range(720, 821, 10):
        base = (float(bx), float(bz))
        for d in range(150, 451, 10):
            for h in range(75, 201, 5):
                rel = (d, h)
                def lev(a):
                    p = rod(rel, a); Lc = math.dist(p, base)
                    ux, uz = (p[0]-base[0])/Lc, (p[1]-base[1])/Lc
                    return abs(ux*(piv[1]-base[1]) - uz*(piv[0]-base[0])), Lc, p
                vals = [lev(th*i/20) for i in range(21)]
                Lw, Lt = vals[0][1], vals[-1][1]
                if not (420 <= Lw <= 460 and Lt - Lw <= 195): continue
                ok = True
                for a in (0, th):
                    p = rod(rel, a); uz = (p[1]-base[1])/(p[0]-base[0])
                    if base[1] + uz*(1400-base[0]) - 40 < 401.5 + 55 + 10: ok = False
                if not ok: continue
                lmin = min(v[0] for v in vals)
                if best is None or lmin > best[0]:
                    best = (lmin, base, rel, Lw, Lt)
lmin, base, rel, Lw, Lt = best
F = Nw*L*math.cos(th)/(lmin/1000)/1000
print(f'base pin R{base[0]:.0f} H{base[1]:.0f}; rod lug {rel[0]} behind pivot, {rel[1]} above arm axis '
      f'(lug pin at R{piv[0]+rel[0]:.0f} H{piv[1]+rel[1]:.0f} when working)')
print(f'pin-to-pin {Lw:.0f} -> {Lt:.0f} (stroke used {Lt-Lw:.0f}); minimum lever {lmin:.0f} mm; worst force {F/1000:.0f} kN; 76.2 bore gives 80 kN')
p_t = rod(rel, th)
print(f'rod pin in transport: R{p_t[0]:.0f} H{p_t[1]:.0f}')

print('\n--- Final layout used in the guide: base pin R1200 H820, rod lug 220 behind pivot, 200 above arm axis ---')
base = (1200.0, 820.0); rel = (220, 200)
vals = []
for i in range(21):
    a = th*i/20; p = rod(rel, a); Lc = math.dist(p, base)
    ux, uz = (p[0]-base[0])/Lc, (p[1]-base[1])/Lc
    vals.append((abs(ux*(piv[1]-base[1]) - uz*(piv[0]-base[0])), Lc, p))
lmin = min(v[0] for v in vals)
print(f'pin-to-pin {vals[0][1]:.0f} -> {vals[-1][1]:.0f}; min lever {lmin:.0f}; force {Nw*L*math.cos(th)/(lmin/1000)/1e6:.0f} kN')
for a, lab in ((0, 'work'), (th, 'transport')):
    p = rod(rel, a); uz = (p[1]-base[1])/(p[0]-base[0])
    print(f'{lab}: cylinder body bottom at R1400 = H{base[1] + uz*(1400-base[0]) - 40:.0f} (pivot tube top H457); '
          f'at beam rear edge R1226: H{base[1] + uz*(1226-base[0]) - 40:.0f} (beam top H700)')
