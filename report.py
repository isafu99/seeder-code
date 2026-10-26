import json, math
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, Image, KeepTogether, PageBreak, ListFlowable, ListItem)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FD = '/usr/share/fonts/truetype/liberation/'
pdfmetrics.registerFont(TTFont('LSans', FD+'LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LSans-B', FD+'LiberationSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LSans-I', FD+'LiberationSans-Italic.ttf'))
pdfmetrics.registerFont(TTFont('LSans-BI', FD+'LiberationSans-BoldItalic.ttf'))
from reportlab.lib.fonts import addMapping
addMapping('LSans', 0, 0, 'LSans'); addMapping('LSans', 1, 0, 'LSans-B')
addMapping('LSans', 0, 1, 'LSans-I'); addMapping('LSans', 1, 1, 'LSans-BI')

R = json.load(open('/home/claude/seeder/results.json'))
S, D, P, E = R['statics'], R['drive'], R['power'], R['energy_avg']
def f(x, n=0): return f'{x:,.{n}f}'

INK = colors.HexColor('#0b0b0b'); MUT = colors.HexColor('#52514e'); ACC = colors.HexColor('#2a78d6')
LINE = colors.HexColor('#c9c7bf'); HEAD = colors.HexColor('#eef3fb')
body = ParagraphStyle('body', fontName='LSans', fontSize=12, leading=18, alignment=TA_JUSTIFY, spaceAfter=6, textColor=INK)
bodyL = ParagraphStyle('bodyL', parent=body, alignment=TA_LEFT)
h1 = ParagraphStyle('h1', fontName='LSans-B', fontSize=15, leading=20, spaceBefore=14, spaceAfter=6, textColor=INK, keepWithNext=1)
h2 = ParagraphStyle('h2', fontName='LSans-B', fontSize=12.5, leading=18, spaceBefore=10, spaceAfter=4, textColor=INK, keepWithNext=1)
cap = ParagraphStyle('cap', fontName='LSans-I', fontSize=10, leading=13, textColor=MUT, spaceBefore=3, spaceAfter=10)
eq = ParagraphStyle('eq', fontName='LSans', fontSize=12, leading=18, leftIndent=24, spaceAfter=6, textColor=INK)
cell = ParagraphStyle('cell', fontName='LSans', fontSize=9.5, leading=12, textColor=INK)
cellB = ParagraphStyle('cellB', parent=cell, fontName='LSans-B')
title = ParagraphStyle('title', fontName='LSans-B', fontSize=20, leading=26, alignment=TA_LEFT, textColor=INK, spaceAfter=8)
sub = ParagraphStyle('sub', fontName='LSans', fontSize=12, leading=18, textColor=MUT)
bul = ParagraphStyle('bul', parent=body, leftIndent=0)

story = []
def p(t, st=body): story.append(Paragraph(t, st))
def H1(t): story.append(Paragraph(t, h1))
def H2(t): story.append(Paragraph(t, h2))
def EQ(t): story.append(Paragraph(t, eq))
def bullets(items):
    story.append(ListFlowable([ListItem(Paragraph(i, bul), leftIndent=14, value='•', bulletFontName='LSans') for i in items],
                              bulletType='bullet', start='•', leftIndent=14, bulletFontName='LSans'))
def table(rows, widths, head=True, fs=None):
    data = [[Paragraph(str(c), cellB if (head and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    st = [('GRID', (0, 0), (-1, -1), 0.4, LINE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
          ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
          ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5)]
    if head: st.append(('BACKGROUND', (0, 0), (-1, 0), HEAD))
    t.setStyle(TableStyle(st))
    story.append(t); story.append(Spacer(1, 8))
def fig(path, w, caption):
    from PIL import Image as PI
    im = PI.open(path); ratio = im.size[1]/im.size[0]
    story.append(KeepTogether([Image(path, width=w, height=w*ratio), Paragraph(caption, cap)]))

W = A4[0] - 5*cm

# ------------------------------------------------------------------ title
p('Solar-Assisted Precision Seeder for Maize: Engineering Viability and Detailed Design of a Physical Proof of Concept', title)
p('Technical report based on: Vicentini, I. F. L.; Vidal, J. M.; Savi, N. C. <i>Desenvolvimento de um modelo de semeadora movida a energia solar para a otimização do plantio de milho no Sudeste brasileiro</i>. Brazilian International School, 2023.', sub)
p('Prepared 25 October 2026. All dimensions in millimetres unless stated. Every number in this report is either taken from a cited source, stated as an explicit assumption, or calculated from those two; assumptions are flagged so they can be replaced by measured values.', sub)
story.append(Spacer(1, 6))

H1('1. Executive summary')
p(f'<b>Verdict: the physical seeder is viable as a single-row, walk-behind, electrically driven proof of concept</b> that plants maize at the agronomic targets the research defines (0.50 m rows, ~80,000 plants/ha, 3–5 cm depth in a tilled Southeast-Brazil seedbed). It is <b>not</b> viable as a machine powered only by the solar panels it carries at commercial planting speeds, and the report quantifies why. The design below is built from commercial power components (two 24 V geared DC motors, a 200 W photovoltaic canopy, an MPPT charger, a LiFePO<sub>4</sub> battery and an Arduino controller) plus four custom parts that are fully dimensioned and verified: the 12-cell vertical gravity seed plate, the depth-gauged opener disc, the chassis weldment and the lugged drive wheel.')
bullets([
 f'<b>Size.</b> About 1.63 m long (to the handle grips), 0.87 m wide (PV canopy), 1.03 m high, track 500 mm, drive-axle-to-press-wheel base 880 mm. Operating mass ≈ {f(S["mtot"])} kg including {f(S["mb"])} kg of removable steel ballast.',
 f'<b>The limiting physics is traction, not power.</b> The opener needs ~{f(S["R_row"])} N of downforce and up to 131 N of pull in soil. A light machine slips; the ballast and its position were calculated so that both the opener downforce and the drive-wheel traction are met simultaneously (traction reserve {S["traction_margin"]:.2f}× with a conservative net traction ratio of 0.35).',
 f'<b>Power and energy.</b> Planting at 0.5 m/s on flat ground draws ≈ {f(E["P_el"])} W electrical. At 1000 W/m² the 200 W canopy actually delivers ≈ {f(R["solar"]["P_1000"])} W because the cells run at ≈ {f(R["solar"]["Tc_1000"])} °C, i.e. about {f(E["solar_frac_peak"]*100)}% of demand at noon. Over an average Southeast day the canopy harvests ≈ {f(R["solar"]["E_pv"])} Wh, enough for ≈ {E["hrs_solar"]:.1f} h of planting (≈ {E["ha_day"]:.2f} ha/day); a full battery adds ≈ 2 h.',
 f'<b>Seed metering.</b> A 140 mm, 12-cell acetal plate turns at {R["meter_nom"]["rpm"]:.1f} rpm at 0.5 m/s (rim speed {R["meter_nom"]["v_periph"]:.2f} m/s), far below the 0.34 m/s limit reported for precision meters, and is driven electronically from a non-driven gauge-wheel encoder so that drive-wheel slip does not distort spacing.',
 'All custom parts show safety factors ≥ 2.7 against yield or fatigue under a 2.5× dynamic load factor; one real dynamic hazard was found (canopy resonance with the wheel lugs at ≈ 0.7 m/s) and is removed by four diagonal braces.'])

H1('2. What the research specifies, and what had to be corrected')
p('The research provides the agronomic basis for the design. The values carried directly into the calculations are:')
table([
 ['Parameter', 'Value used', 'Source in the research'],
 ['Row spacing', '0.50 m', 'Fig. 1 and text, citing Cruz et al. (2007): 50 cm rows outperform 80 cm at high density'],
 ['Plant population', '80,000 plants/ha', '"convergência ideal de ~80.000 pl/ha", model section'],
 ['Seeding depth', '3–5 cm (design 4 cm)', 'Fagundes (1975), Bresolin (1993) for clay soils of the Southeast'],
 ['Planter type', 'conventional (tilled seedbed), precision, mechanical meter', 'model section: gravity-assisted, precision, low cost'],
 ['Planting window', 'October–November', 'Embrapa recommendation cited in the text'],
 ['Control', 'Arduino-timed seed release', 'prototype description, Fig. 2'],
], [3.3*cm, 4.3*cm, W-7.6*cm])
p('Four statements in the research need correction before they can be turned into hardware:')
bullets([
 '<b>Seed spacing vs. row spacing.</b> The text says precision planters keep the spacing between seeds above 40 cm. That figure describes <i>row</i> spacing. With 0.50 m rows and 80,000 plants/ha the in-row spacing is 25 cm between plants (Section 3), and the meter must be designed for that.',
 '<b>Density in Fig. 1.</b> The text reads the figure as showing an optimum between 75,000 and 85,000 plants/ha, but the plotted data stop at about 77,000 plants/ha; the trend is still rising there. 80,000 is a reasonable target but an extrapolation.',
 '<b>"No straw in maize planting."</b> Much of Brazilian grain maize is sown under no-till, where straw is present. This design keeps the research\'s choice of a tilled seedbed and states it as an operating condition; a no-till version would need a straw-cutting coulter and roughly twice the downforce.',
 '<b>"Small panels already power the machine."</b> True only for a small, slow machine. Section 7 shows the canopy covers most, not all, of the demand of a single-row unit at walking speed, and Section 12 shows why the idea does not scale to multi-row planters without off-board charging.'])

H1('3. From agronomy to machine parameters')
a = R['agro']
p('Linear metres of row per hectare at 0.50 m spacing are 10,000/0.50 = 20,000 m, so 80,000 plants/ha means 4.0 plants per metre of row. Assuming 90% field emergence (to be replaced by the germination result printed on the seed lot), the seed rate is:')
EQ(f'seeds per metre = 4.0 / 0.90 = {a["seeds_per_m"]:.3f} seeds/m  →  in-row seed spacing X = {a["X_seed_mm"]:.0f} mm')
p(f'That is {f(a["seeds_per_ha"])} seeds/ha. With an assumed thousand-seed mass of 350 g (typical commercial hybrid range 300–380 g; weigh the actual lot), the rate is {a["seed_kg_ha"]:.1f} kg/ha, and a 3 L hopper (≈ {a["hopper_kg"]:.2f} kg at an assumed 0.72 kg/L bulk density) plants ≈ {a["ha_per_fill"]:.2f} ha per fill.')
p('<b>Ground speed.</b> Commercial precision planters run at 5–10 km/h, but a walk-behind proof of concept must match a walking operator and a small energy budget. The design speed is 0.5 m/s (1.8 km/h) with a maximum of 1.0 m/s. At 0.5 m/s and 0.50 m working width the theoretical capacity is 0.09 ha/h; with an assumed 65% field efficiency (headland turns, hopper refills) the effective capacity is 0.059 ha/h.')
p('<b>Wheel placement.</b> With the seed row on the machine centre line, a 500 mm track puts both wheels 250 mm to each side, exactly on the mid-lines between rows. Because successive passes are 500 mm apart, the wheels always run between rows and never compact a seed row; this is why the track is fixed at 500 mm.')

H1('4. Machine concept and general arrangement')
p('The machine is a two-wheel-drive tool carrier steered by the operator through a handlebar. From front to rear: battery and electronics; the drive axle with two lugged steel wheels, each driven by its own geared motor through a chain; a ballast tray; the row unit (opener disc, depth gauge wheel, seed meter and hopper) hung rigidly under the frame; a spring-loaded press wheel on a swivel-lockable fork; the handlebar. A 1.0 m² PV canopy on four braced posts covers the whole machine and shades the battery and electronics. Two independent motors allow the operator to pivot at headlands by running the wheels at different speeds, which also explains the swivel-lockable rear wheel (Section 5.4).')
table([
 ['Item', 'Dimension / position (x rearward from drive axle, y above ground)'],
 ['Overall length / width / height', '≈ 1630 (to grips) / 865 (canopy) / 1030 (canopy top)'],
 ['Track; wheelbase', '500 between wheel centres; 880 drive axle → press wheel'],
 ['Frame', '1150 × 300 outside, rails 40×40×2, centre line at y = 200 (ground clearance 180)'],
 ['Drive wheels', 'Ø380 rim, Ø420 over lugs, 100 wide, axle at x = 0, y = 200'],
 ['Opener disc / gauge wheel', 'Ø250 at x = 470 (axle y = 85 for 40 mm depth) / Ø200 at x = 510, y = 100'],
 ['Seed meter / hopper', 'plate Ø140 centred x = 520, y = 330 / 3 L, y = 420–600'],
 ['Ballast', f'{f(S["mb"])} kg (4 × 5 kg plates) centred x = {f(S["xb"])}, y = 300'],
 ['Press wheel', 'Ø250 × 60 at x = 880, spring force 60 N'],
 ['PV canopy', '2 modules 865 × 578 × 30, total 1156 × 865, top at y = 1030, centred x = 328'],
 ['Centre of gravity (frame + row unit)', f'x = {f(S["xcg"])}, y = {f(S["ycg"])}'],
], [5.0*cm, W-5.0*cm])
fig('/home/claude/seeder/fig1_ga.png', 0.80*W, 'Figure 1. General arrangement. Side view (top) and top view (bottom). Blue: gauge wheel and seed path. The seed row is the machine centre line.')

H1('5. Loads, traction and static equilibrium')
H2('5.1 Soil forces on the opener')
p('Soil-bin measurements on a single-disc opener reported vertical forces of 321.5–373.4 N and draft (horizontal) forces of 92.2–131.3 N across disc angles of 0–20° [2]. Those tests were in no-till soil; forces are lower in loose, drier soil [3], so using the upper ends of the measured ranges for a tilled seedbed is conservative. Design values: draft D<sub>o</sub> = 131 N; vertical soil reaction V<sub>o</sub> = 321–373 N; side force at the 5° gang angle assumed 150 N (no measured value was available; this should be checked in the first field test).')
p(f'For the depth gauge to control depth, the gauge wheel must stay loaded. Requiring at least 30 N of gauge load at the worst case gives a required row-unit vertical reaction R<sub>row</sub> = 373 + 30 = {f(S["R_row"])} N, which leaves {f(S["G_at_Vmin"])} N on the gauge wheel when soil resistance is at the low end.')
H2('5.2 Traction requirement')
p('The drive wheels must pull the opener draft, the rolling resistance of the gauge and press wheels, a 3% field slope and a 0.2 m/s² start-up acceleration:')
EQ(f'F<sub>req</sub> = D<sub>o</sub> + ρ<sub>g</sub>G + ρ<sub>p</sub>N<sub>p</sub> + W·sin θ + m·a = {f(S["F_req"],1)} N  (steady, without acceleration: {f(S["steady_req"],1)} N)')
p(f'Wheel performance was estimated with the Brixius traction model adopted in ASABE D497 [4], using the mobility number B<sub>n</sub> = (CI·b·d/W)·(1+5δ/h)/(1+3b/d). Assumptions: cone index CI = 600 kPa (within the 450–900 kPa range quoted for loose to tilled soils [4]); rigid wheel, δ/h = 0; slip s = 0.15. For the drive wheels (b = 0.10 m, d = 0.42 m, W = {f(S["Nd_per_wheel"])} N per wheel) this gives B<sub>n</sub> = {S["Bn"]:.1f}, gross traction ratio {S["GT"]:.3f}, motion resistance ratio {S["MR"]:.3f} and net traction ratio {S["NTR_brixius"]:.3f}. The Brixius equations were derived for pneumatic tyres and deviate by up to 35% from measured axle torque on tractors [4]; a rigid lugged wheel in loose soil is outside their calibration. The design therefore uses a net traction ratio of <b>0.35</b>, about 63% of the model value, and adds a 10% reserve:')
EQ(f'N<sub>d,req</sub> = 1.10 × F<sub>req</sub> / 0.35 = {f(1.10*S["F_req"]/0.35)} N;  with ballast rounded up to whole plates, actual N<sub>d</sub> = {f(S["Nd"])} N ({f(S["Nd_per_wheel"])} N per wheel)')
m = R['mohr']
p(f'A second, independent check uses Mohr–Coulomb soil shear under the lugs, H<sub>max</sub> = A·c + W·tan φ, with assumed tilled-soil strength c = 3 kPa and φ = 28°, a 20 mm rut and contact length l = 2√(2Rz − z²) = {m["l_contact"]*1000:.0f} mm. Maximum thrust is {f(m["H_max_wheel"])} N per wheel against {f(m["H_req_wheel"])} N needed (gross, including the wheel\'s own motion resistance), i.e. {m["util"]*100:.0f}% utilisation, with {m["lugs_engaged"]:.1f} lugs in the soil at any instant. Soil strength values are typical textbook ranges, not site measurements; a cone penetrometer and shear vane reading at the test plot should replace them.')
H2('5.3 Static equilibrium and ballast')
p('All horizontal ground forces (traction, draft, rolling resistance) act within a few centimetres of ground level, so they produce negligible pitching moment; the vertical equilibrium of the frame-plus-row-unit body is governed by weights alone. Taking the press-wheel spring as a known force P = 60 N, the frame is statically determinate with two unknown supports (drive axle and row unit):')
EQ('ΣF<sub>y</sub> = 0:  N<sub>d</sub> + R<sub>row</sub> + P = W<sub>0</sub> + m<sub>b</sub>g')
EQ('ΣM<sub>axle</sub> = 0:  R<sub>row</sub>·x<sub>row</sub> + P·x<sub>p</sub> = W<sub>0</sub>·x<sub>0</sub> + m<sub>b</sub>g·x<sub>b</sub>')
p(f'With the component masses of Table 2 (W<sub>0</sub> = {f(S["W0"])} N, x<sub>0</sub> = {f(S["x0"])} mm), x<sub>row</sub> = 485 mm and x<sub>p</sub> = 880 mm, the two equations give a required ballast of {S["mb_req"]:.1f} kg, rounded up to <b>{f(S["mb"])} kg (four 5 kg plates)</b>, centred at <b>x<sub>b</sub> = {f(S["xb"])} mm</b>. With that ballast N<sub>d</sub> = {f(S["Nd"])} N and R<sub>row</sub> = {f(S["R_row"])} N exactly, and the available net traction is {f(S["F_avail"])} N against {f(S["F_req"])} N required. The material choice for the frame follows from this result: mass is useful here, so steel (cheap, weldable, three times stiffer than aluminium) is preferred, and any later weight reduction would simply move into the ballast tray.')
rows = [['Component', 'Mass (kg)', 'x (mm)', 'y (mm)']]
for n, mm_, x, y in R['items']:
    rows.append([n, f'{mm_:.2f}', f'{x:.0f}', f'{y:.0f}'])
rows.append(['<b>Total (frame + row unit + ballast)</b>', f'<b>{S["Wf"]/9.81:.1f}</b>', f'<b>{S["xcg"]:.0f}</b>', f'<b>{S["ycg"]:.0f}</b>'])
table(rows, [W-6.6*cm, 2.2*cm, 2.2*cm, 2.2*cm])
p('Table 2. Mass budget. Masses of purchased items marked "assumed" must be replaced by weighed values; the ballast position is then recomputed with the two equations above. The press-wheel assembly (≈ 4.5 kg) rests on its own wheel and is excluded from the frame balance.', cap)
H2('5.4 Headland turns: why the rear wheel must swivel')
t = R['turn']
p(f'At the headland the operator lifts the row unit with a hand lever. The frame then rests on the drive wheels and the press wheel, which carries N = W·x<sub>cg</sub>/x<sub>p</sub> + its own weight ≈ {f(t["N_press_raised"])} N. If that wheel could not swivel, pivoting would have to scrub it sideways: with a lateral friction coefficient of 0.6 the yaw moment is {f(t["scrub_moment"])} N·m, requiring {f(t["diff_force_each"])} N of opposite thrust at each drive wheel against {f(t["traction_each"])} N available. The machine could not turn. A commercial swivel caster with a swivel lock, used as the press wheel, removes that resistance; it is locked straight while planting.')

H1('6. Drive train')
mo, mx = R['motor_nom'], R['motor_max']
p(f'<b>Motor.</b> Two MY1016Z3 brushed 24 V gear-reduction motors (350 W, internal reduction 9.78:1). Retail listings disagree on the output specification; the conservative values used here are 300 rpm rated output speed, 110 kgf·cm (10.8 N·m) rated torque, 350 kgf·cm (34.3 N·m) stall torque, 19 A rated current and 2.2 A no-load current [12]. These must be confirmed on the purchased units (a simple brake test on the bench is enough).')
p(f'<b>Final drive ratio.</b> At 1.0 m/s with 15% slip the wheel turns at n = v/[(1−s)·2πr] = {mx["n_wheel"]:.1f} rpm, so the ratio must be ≈ 300/56 = 5.3. The motor ships with a 9-tooth sprocket for 1/2-inch-pitch chain; a 48-tooth driven sprocket gives i = {D["i"]:.3f}. Pitch diameters are {D["PD9"]:.1f} mm and {D["PD48"]:.1f} mm (PD = p/sin(180°/N)). At a nominal centre distance of 130 mm the chain length formula gives {D["L_links_calc"]:.1f} pitches, rounded to {D["links"]} links, which sets the actual centre distance at {D["C_actual_mm"]:.1f} mm; the motor plate has slotted holes for tensioning.')
p(f'<b>Torque check.</b> Steady wheel torque is {D["T_wheel_op"]:.1f} N·m per wheel (gross thrust × 0.20 m rolling radius), so each motor delivers {mo["T_motor_out"]:.2f} N·m at its output, 42% of rated, drawing ≈ {mo["I_motor"]:.1f} A. Rated torque corresponds to {D["F_wheel_rated"]:.0f} N of thrust per wheel, 2.2 times the steady requirement, which covers clods, slopes and start-up. Running well below rated current keeps copper losses (which scale with I²) at about a quarter of rated, so continuous operation does not overheat the motors.')
H2('6.1 Stub axles, keys and bearings')
sh, k, b = R['shaft'], R['key'], R['bearing']
p(f'Each wheel sits on its own 25 mm stub axle (AISI 1045 cold drawn, S<sub>u</sub> = 630 MPa, S<sub>y</sub> = 530 MPa [15]) carried by two 2-bolt flange bearing units (UCFL205, 25 mm bore) bolted to 6 mm axle plates on the inside and outside of the side rail, 82 mm apart. The wheel overhangs the outer bearing by 79 mm and the 48T sprocket overhangs the inner bearing by 29 mm.')
p(f'<b>Static (worst credible) case:</b> 2.5 × the wheel load at the overhang plus a lateral force of 0.5 × wheel load at the tyre contact (side slope or skid), M = {sh["M_static"]:.1f} N·m, combined with the full motor stall torque transmitted through the chain, T = {sh["T_stall"]:.0f} N·m (a wheel jammed against an obstacle). Bending stress {sh["sigma_b"]:.1f} MPa, shear {sh["tau"]:.1f} MPa, von Mises {sh["svm"]:.1f} MPa, safety factor against yield <b>{sh["n_static"]:.1f}</b>.')
p(f'<b>Fatigue:</b> rotating bending from 1.5 × the nominal wheel load (M<sub>a</sub> = {sh["Ma"]:.1f} N·m) with steady operating torque T<sub>m</sub> = {sh["Tm"]:.1f} N·m. Marin factors k<sub>a</sub> = {sh["ka"]:.3f} (machined), k<sub>b</sub> = {sh["kb"]:.3f} (25 mm), k<sub>e</sub> = 0.814 (99% reliability) give S<sub>e</sub> = {sh["Se"]:.0f} MPa. Using the keyseat stress concentrations K<sub>f</sub> = 2.14 (bending) and K<sub>fs</sub> = 3.0 (torsion) in the DE-Goodman criterion gives a fatigue safety factor of <b>{sh["n_fatigue"]:.2f}</b>.')
p(f'<b>Key:</b> 8 × 7 × 45 mm parallel key (DIN 6885 size for 22–30 mm shafts). At stall torque: shear {k["tau"]:.1f} MPa, bearing pressure {k["crush"]:.1f} MPa, both well inside the capacity of a medium-carbon key steel. <b>Bearings:</b> the larger reaction is {b["R_out"]:.0f} N at the outer bearing; with a basic dynamic rating of about 14 kN for a UC205 insert (typical catalogue value; confirm for the chosen brand) the L<sub>10</sub> life exceeds 10<sup>6</sup> hours. The bearing size is set by the shaft diameter, not by load.')

H1('7. Energy and thermodynamics')
so = R['solar']
p(f'<b>PV modules.</b> Two Renogy CORE 100 W 12 V modules (865 × 578 × 30 mm, 5.9 kg, V<sub>mp</sub> 19.97 V, V<sub>oc</sub> 22.79 V, NOCT 47 °C, power temperature coefficient −0.32%/°C [10]) are wired in series: V<sub>mp</sub> = {so["Vmp"]:.1f} V, and V<sub>oc</sub> at a cold 5 °C morning is ≈ {so["Voc_cold"]:.0f} V, inside the 75 V limit of a Victron SmartSolar MPPT 75/15, which charges 24 V batteries from up to 440 W of PV [11]. Module efficiency at standard conditions is 200 W / 1.0 m² = 20%.')
p(f'<b>Cell temperature (first law applied to the module).</b> Of the 1000 W of sunlight falling on 1.0 m² of module, only the electrical output leaves as work; the rest (≈ {f(so["heat_rejected_1000"])} W) must be rejected by convection and radiation, so the cells run hot. The NOCT method gives T<sub>c</sub> = T<sub>a</sub> + (NOCT − 20)/800 × G. For a 30 °C afternoon at 1000 W/m², T<sub>c</sub> = {so["Tc_1000"]:.1f} °C and output falls to 200 × [1 − 0.0032 × ({so["Tc_1000"]:.1f} − 25)] = <b>{so["P_1000"]:.0f} W</b>. Mounting the modules on an open canopy, with air flowing underneath, is therefore a thermal design choice, not only a structural one; the same canopy keeps the battery in shade, which matters because LiFePO<sub>4</sub> packs typically stop charging above about 45 °C.')
p(f'<b>Daily energy.</b> The 2nd edition of the Brazilian Solar Energy Atlas (INPE) puts the Southeast\'s mean daily global horizontal irradiation at about 5.0–5.2 kWh/m² [9]; 5.0 kWh/m² is used (monthly values for October at the test site should replace it). With a daytime-average temperature factor of {so["fT_day"]:.3f}, MPPT efficiency 0.96, soiling 0.95 and wiring 0.98, the canopy harvests <b>{f(so["E_pv"])} Wh/day</b>. A 25.6 V, 20 Ah LiFePO<sub>4</sub> battery used to 80% depth stores {f(so["E_bat"])} Wh and acts as the buffer between the sun\'s output and the machine\'s demand.')
table([
 ['Operating case', 'Electrical demand', 'Planting time from one day of sun', 'Area per day'],
 ['Flat field, mid-range draft (111 N), 0.5 m/s', f'{f(E["P_el"])} W', f'{E["hrs_solar"]:.1f} h (+{(E["hrs_with_full_bat"]-E["hrs_solar"]):.1f} h if battery starts full)', f'{E["ha_day"]:.2f} ha'],
 ['3% slope, upper-bound draft (131 N), 0.5 m/s', f'{f(P["P_el_nom"])} W', f'{so["hrs_solar"]:.1f} h', f'{so["ha_day_solar"]:.2f} ha'],
 ['3% slope, upper-bound draft, 1.0 m/s', f'{f(P["P_el_max"])} W', 'battery-limited (≈ 20 A, 1C)', '—'],
], [5.4*cm, 2.8*cm, 4.6*cm, W-12.8*cm])
p(f'Electrical demand was built up as wheel-axle power / (chain 0.95 × motor-and-gearbox 0.60 × controller 0.97), plus 12 W for the meter stepper and 6 W for electronics. The motor-plus-gearbox efficiency of 0.60 is an assumption for a small brushed motor at part load and is the largest single uncertainty in the energy budget; measuring battery current during the first field run will settle it. Figure 6 shows the full energy cascade: of every 1000 W of sunlight on the canopy, about {R["cascade"][-1][1]:.0f} W ({R["cascade_overall"]*100:.1f}%) ends up as useful pull on the opener.')
fig('/home/claude/seeder/fig6_energy.png', W, 'Figure 6. Energy cascade from sunlight to drawbar pull at 1000 W/m² and design speed. The largest losses are photovoltaic conversion (thermodynamically unavoidable at the module level) and the small geared motors.')

H1('8. Custom part 1: 12-cell vertical gravity seed plate')
mn, mxm = R['meter_nom'], R['meter_max']
p('<b>Working principle.</b> The plate rotates in a vertical plane inside a close-fitting housing. Seed from the hopper rests on the upper part of the plate (the fill zone, roughly 10 to 2 o\'clock), where each cell faces upward and a seed drops into it by gravity. A brush singulator in the direction of rotation sweeps off any second seed. The housing shroud holds the seed in its cell as the cell turns downward; at 6 o\'clock the shroud is open and the seed falls by gravity into the seed tube. A spring-steel ejector finger at the discharge point knocks out any seed that sticks. This is the classic vertical-plate arrangement in which cells pick up seed from a container above and discharge it below when inverted [US 3,498,241].')
p(f'<b>Cell geometry from seed geometry.</b> Large flat hybrid seeds are concentrated at 11–14 mm long and 8–10 mm wide, with thickness around 4–6 mm [5]. Plate makers advise sizing cells to the largest seed in the lot, slightly longer and deeper than the seed, and that for flat seed the cell length runs along the rim [6]. Design: cell length along the rim 15.5 mm (1.1 × 14), plate thickness (cell width) 10.5 mm (≥ 10 mm seed width plus clearance), radial depth 6.0 mm (≥ 5.5 mm thickness). Singulation is geometric: a second seed cannot fit because 6.0 mm < 2 × 4 mm minimum thickness and 15.5 mm < 2 × 11 mm minimum length. The cell ends get R1.5 lead-in radii to avoid cracking seed at the singulator.')
p(f'<b>Diameter and number of cells.</b> With 12 cells on a Ø140 plate, the cell pitch on the rim is π·140/12 = {R["meter_geom"]["cell_pitch_mm"]:.1f} mm, leaving a 21 mm land between cells. Plate speed n = v·(seeds/m)/12: <b>{mn["rpm"]:.1f} rpm at 0.5 m/s, {mxm["rpm"]:.1f} rpm at 1.0 m/s</b>. Rim speed is {mn["v_periph"]:.3f} m/s and {mxm["v_periph"]:.3f} m/s. Laboratory work found 0.34 m/s to be the upper limit of plate peripheral speed for good singulation of maize [7], and tests on Brazilian meters showed the share of acceptable spacings falling steadily as peripheral speed rose from 0.09 to 0.38 m/s [8]; the design operates at the slow end of that range. Seed release frequency, {mxm["seed_rate"]:.1f} seeds/s at most, is far below the 16 seeds/s limit reported in [7].')
p(f'<b>Why gravity works here (dynamics).</b> The ratio of centripetal to gravitational acceleration at the cell is ω²r/g = {mn["Froude"]:.4f} at 0.5 m/s and {mxm["Froude"]:.3f} at 1.0 m/s. Gravity dominates by a factor of 27 or more, so seeds settle into the cells in the fill zone and drop out cleanly at the bottom; a vacuum or finger pick-up is unnecessary at these speeds.')
p(f'<b>Drive and synchronisation.</b> The plate is driven by a NEMA 17 stepper motor with a ~5:1 planetary gearbox. Design torque is {R["meter_drive"]["T_design"]:.1f} N·m (seed-pool friction, brush drag and seal drag estimated at 0.25 N·m, × 4). Ground speed is measured by a 600-pulse/rev encoder on the <i>gauge wheel</i>, which is not driven and therefore does not slip (resolution {R["meter_drive"]["enc_res_mm"]:.2f} mm of travel). If speed were taken from the drive wheels, their 15% slip would place seeds 15% too close. With 1/8 microstepping the Arduino issues 8,288 steps per plate revolution, i.e. {f(R["meter_drive"]["steps_per_m"])} steps per metre of travel, at most ≈ 3,100 steps/s at 1.0 m/s.')
p(f'<b>Material and thermal clearance.</b> Acetal copolymer (POM-C) is chosen for low friction against seed, low moisture uptake and easy machining; a PETG print is acceptable for first trials. Acetal expands about five times more than aluminium (≈ 110 vs 23 × 10<sup>−6</sup>/K). For a 30 K temperature rise in the sun the plate grows {R["thermal_plate"]["dD_diam_mm"]:.2f} mm more in diameter than an aluminium housing, so the radial clearance to the shroud is set at 0.75 mm at 20 °C: it stays positive when hot and is still far smaller than any seed.')
p(f'<b>Seed delivery.</b> The discharge sits 300 mm above the furrow floor. Free-fall time is √(2h/g) = {R["drop"]["t_fall"]:.3f} s. Assuming ±15% variation in tube transit time (bounces), the placement error is ±{R["drop"]["spacing_err_mm_nom"]:.0f} mm at 0.5 m/s ({R["drop"]["spacing_err_mm_nom"]/225*100:.0f}% of spacing) and ±{R["drop"]["spacing_err_mm_max"]:.0f} mm at 1.0 m/s, inside the 0.5X–1.5X band used to classify doubles and misses [16]. The plate turns so that the cell moves rearward at the discharge point, which reduces the seed\'s horizontal velocity relative to the ground.')
fig('/home/claude/seeder/fig2_plate.png', W, 'Figure 2. Seed plate. Twelve cells at 30° pitch, plate bolted to an aluminium flange hub on the gearbox output shaft.')
H2('8.1 SolidWorks modelling procedure (seed plate)')
bullets([
 'New part, MMGS units, material "Acetal Copolymer" (create a custom material if absent: E ≈ 2.8 GPa, ρ = 1410 kg/m³, α ≈ 110 × 10<sup>−6</sup>/K).',
 'Front Plane: sketch a Ø140 circle and a Ø12 concentric circle; Extruded Boss, Mid Plane, 10.5 mm.',
 'Front face: sketch one cell profile on the rim, a slot 15.5 long (chord along the rim, symmetric about the vertical construction line) and 6.0 deep radially, with the bottom as an arc concentric with the plate; Extruded Cut, Through All.',
 'Fillet the two cell entry edges R1.5 (do not fillet the cell floor).',
 'Circular Pattern of the cut and fillet: axis = plate axis, 12 instances, 360°, equal spacing.',
 'Hole Wizard: 3 × Ø4.5 through on a Ø30 PCD (clearance for M4); add an H7 tolerance to the Ø12 bore via DimXpert.',
 'Add a configuration with 3D-print adjustments (bore +0.2 mm) for PETG trials.',
 'Assembly check: mate to the housing; Interference Detection with the shroud modelled at Ø141.5; run Evaluate → Mass Properties to update Table 2.'])

H1('9. Custom part 2: depth-gauged opener disc')
dg = R['disc_geom']
p(f'<b>Disc.</b> Flat disc Ø250 × 4 mm with a 15° single bevel on the outer 10 mm, set at a 5° gang angle to the direction of travel and vertical (0° tilt), so that it opens a narrow V-slot. The literature shows draft and vertical force rising with disc angle [2]; 5° is close to the minimum that still opens a slot. At 40 mm depth the disc engages the soil over a central angle of 2·acos[(125−40)/125] = {2*dg[1][1]:.0f}°, a chord of {dg[1][2]:.0f} mm. Commercial disc blades are typically heat-treated medium/high-carbon or boron steel for abrasion resistance; specify a carbon spring steel (e.g. SAE 1065/65Mn) through-hardened to 40–45 HRC.')
p(f'<b>Strength.</b> The side force (150 N assumed) acts at the centroid of the engaged band, about r = 115 mm, and bends the disc about the edge of its Ø100 clamp flange. Treating a 60° sector at the clamp edge as a cantilever, with a 2.5 dynamic factor: M = {R["disc"]["M"]:.1f} N·m, σ = 6M/(b·t²) = {R["disc"]["sigma"]:.0f} MPa. A 40–45 HRC spring steel has a yield strength well above 1,000 MPa (safety factor &gt; 5); even an un-hardened plate would survive, so hardness is specified for wear, not strength. A 3 mm disc would see 310 MPa with the same model, which is why 4 mm was chosen.')
p(f'<b>Hub.</b> Two 6203-2RS deep-groove bearings (17 × 40 × 12) 24 mm apart in a steel hub housing on a 17 mm spindle. The side-force moment adds a couple of ±{R["disc_bearing"]["R_max"]-R["disc_bearing"]["P"]/2:.0f} N to the bearings, giving a worst reaction of {R["disc_bearing"]["R_max"]:.0f} N. With C = 9.95 kN (SKF catalogue value for 6203) the L<sub>10</sub> life is ≈ {f(R["disc_bearing"]["L10_Mrev"])} million revolutions, more than 10,000 km of travel.')
p('<b>Depth gauge.</b> A commercial 200 × 50 mm ball-bearing rubber wheel rolls on the soil surface beside the disc, 3 mm from its face, centred 40 mm behind the disc axle so that it controls depth close to the seed-drop point. With the ground surface as datum, depth d = R<sub>disc</sub> − R<sub>gauge</sub> + Δ = 125 − 100 + Δ, where Δ is the height of the gauge axle above the disc axle. The gauge axle is carried by a slider block in a vertical 35 mm slot, positioned by an M10 × 1.5 adjusting screw (1.5 mm of depth per turn) and locked by two M8 clamp bolts; Δ = 5 → 25 mm gives d = 30 → 50 mm, covering the research\'s 3–5 cm range with margin. A scale engraved every 5 mm on the slot plate gives the depth directly.')
p(f'<b>Why the row unit is rigid.</b> Because the row unit is bolted rigidly to the frame, the machine stands on three supports (drive axle, gauge wheel, press-wheel spring). As long as the gauge wheel stays loaded (minimum {f(S["G_at_Vmax"])} N, Section 5.1), it, not the drive wheels, sets the disc height. Drive-wheel sinkage of 20 mm tilts the frame by only 20/485 rad (2.4°), which changes the disc\'s pitch slightly but not the depth. The shank plate (8 mm S235) carries the side force out of plane: σ = {R["shank"]["sigma"]:.0f} MPa with the 2.5 factor, safety factor {R["shank"]["n"]:.1f}. Its four M10 class 8.8 mounting bolts see at most {f(R["mountbolt"]["F"])} N each against a recommended preload of {f(R["mountbolt"]["Fi"])} N, so the joint never separates.')
fig('/home/claude/seeder/fig3_opener.png', W, 'Figure 3. Opener disc and depth gauge. Left: side view at 40 mm depth. Right: plan view showing the 5° gang angle and the gauge wheel beside the disc.')
H2('9.1 SolidWorks modelling procedure (opener assembly)')
bullets([
 '<b>Disc part:</b> Right Plane sketch, Ø250 and Ø17.5 circles; Extrude 4 mm. Revolved Cut (or Chamfer 10 × 15°) on one face of the outer edge to form the bevel, leaving a 0.5 mm edge land. Hole Wizard: 4 × Ø8.5 on a Ø75 PCD for the clamp bolts. Material: "AISI 1065" or custom 65Mn; note hardness 40–45 HRC on the drawing.',
 '<b>Hub housing:</b> Revolve a stepped profile (bearing bores Ø40 H7 × 12 deep from each side, central spacer land, Ø100 × 8 flange). Tap 4 × M8 on Ø75 PCD in the flange. Material AISI 1045.',
 '<b>Shank plate:</b> 8 mm plate, sketch outline 300 × 220 with the spindle hole Ø17 at the disc-axle position, the 35 × 10.5 vertical slot for the gauge slider, 4 × Ø10.5 mounting holes and a lightening cut; Extrude. Use Sheet Metal (8 mm, no bends) to get a flat pattern for laser cutting.',
 '<b>Gauge slider:</b> block 40 × 30 × 20 with a tapped M10 vertical hole for the adjusting screw and a Ø12 stub axle; mate "Distance" between slider and slot bottom, driven by a global variable Δ, so that changing Δ updates depth.',
 '<b>Assembly:</b> insert the commercial gauge-wheel and bearing models (6203-2RS from the SOLIDWORKS Toolbox, or McMaster CAD). Rotate the disc 5° about the vertical axis with an Angle mate to the frame centre-plane. Add a sketch on the Right Plane with the ground line and a driven dimension "depth" between ground and the disc bottom; confirm d = 30/40/50 mm for Δ = 5/15/25 mm.',
 'Run SOLIDWORKS Simulation on the disc: fixed at the clamp annulus, 375 N lateral (2.5 × 150 N) distributed over the engaged rim arc; expect a peak stress near the clamp edge in the order of the hand result above or lower (the hand model ignores hoop stiffness).'])

H1('10. Custom part 3: chassis frame weldment')
fr = R['frame']
p(f'<b>Members.</b> Two side rails 40×40×2 (1150 long) at ±130 mm from the centre line; five cross-members 40×40×2 of 220 mm between the rails at x = −280 (front), 260, 380, 600 (row-unit hanger) and 830 (rear, carries the press-wheel arm pivot and handlebar sockets); four 6 mm axle plates (160 × 140) welded inside and outside each rail at x = 0; motor plates (6 mm, slotted) on the inner face of each rail; a 6 mm ballast tray bolted across the rails at x = 150–250; four canopy-post sockets. Canopy posts 25×25×2 (780 long), two longitudinal canopy rails and three cross-bars 25×25×2, and four diagonal braces 25×25×2.')
p(f'<b>Material.</b> Square structural tube to ASTM A500 Gr. B or the Brazilian equivalent in SAE 1010/1020; a yield strength of 235 MPa is used conservatively. Section properties (sharp-corner approximation): I = {f(fr["I40"])} mm⁴, S = {f(fr["S40"])} mm³ for 40×40×2 (2.39 kg/m); I = {f(fr["I25"])} mm⁴, S = {f(fr["S25"])} mm³ for 25×25×2.')
p(f'<b>Bending.</b> The frame was modelled as a beam along x carrying every mass of Table 2 at its position, the soil reaction R<sub>row</sub> and the press spring force, supported at the drive axle (planting case), and again with the row unit raised and the press wheel carrying the rear (headland case). The largest moment is {fr["Mmax"]:.0f} N·m at x ≈ {fr["x_Mmax"]} mm in the headland case. Shared by two rails and multiplied by a 2.5 dynamic factor, σ = {fr["sigma"]:.1f} MPa; safety factor against yield <b>{fr["n"]:.1f}</b>. The canopy posts carry about 100 N each in compression against an Euler buckling load of {f(fr["Pcr_post"]/1000,1)} kN (fixed-free).')
v = R['vib']
p(f'<b>Vibration (dynamics).</b> The canopy (≈ {v["m_can"]:.1f} kg on four 780 mm cantilever posts) has a lateral stiffness of 4 × 3EI/L³ = {v["k_unbr"]/1000:.1f} N/mm and a natural frequency of {v["f_unbr"]:.1f} Hz. The 16 wheel lugs hit the ground at 16 × (wheel speed): {v["f_lug_nom"]:.1f} Hz at 0.5 m/s and {v["f_lug_max"]:.1f} Hz at 1.0 m/s. The two frequencies coincide at ≈ {v["v_resonance"]:.2f} m/s, inside the operating range, which would shake the panels and loosen fasteners. Four diagonal braces (two longitudinal, two transverse) add axial-member stiffness and raise the canopy\'s first mode to roughly {v["f_br"]:.0f} Hz, about ten times the highest excitation frequency.')
st = R['stab']
p(f'<b>Stability.</b> The centre of gravity is {f(S["ycg"])} mm above ground. The tipping axis on a side slope runs from a drive-wheel contact to the rear wheel; the CG lies {st["d_tip"]:.0f} mm from it in plan, giving a static tipping angle of atan({st["d_tip"]:.0f}/{f(S["ycg"])}) = {st["tip_angle"]:.0f}°. The machine should not be used across slopes steeper than about half that (≈ 12°, 21%), far beyond normal planting ground.')
p('<b>Welds.</b> 3 mm fillet welds (GMAW, ER70S-6 wire) all around every tube joint; 4 mm fillets on the axle plates. The most loaded weld (axle plate to rail, 2 × 140 mm long) carries the dynamic wheel load at a stress of a few MPa. Weld distortion, not strength, is the practical concern: tack the frame on a flat table and weld symmetrically.')
fig('/home/claude/seeder/fig4_frame.png', W, 'Figure 4. Chassis weldment, plan view. Canopy posts, braces and handlebar are omitted for clarity.')
H2('10.1 SolidWorks modelling procedure (frame)')
bullets([
 'New part; on the Top Plane draw a 3D sketch (or 2D layout sketch) of member centre lines with the x-positions of Figure 4: rails 1150 long at ±130, cross-members at x = −280, 260, 380, 600, 830.',
 'Insert → Weldments → Structural Member: Standard "iso", Type "square tube", Size "40 x 40 x 2" (add a custom profile if your library lacks it). Select rail lines as Group 1, cross-member lines as Group 2; set corner treatment "end butt" with cross-members trimmed to the rails (Trim/Extend).',
 'Second 3D sketch for the canopy: vertical post lines (780) at x = −200 and 800, ±130; top rails and cross-bars at y = 1000 above ground; braces from post tops to rail points 400 mm away. Structural Member 25 × 25 × 2.',
 'Plates: Extruded Boss "Merge result" off for the axle plates (6 mm, 160 × 140), motor plates (6 mm, with slots 10.5 × 30 for chain tension) and ballast tray; add them to the Cut List as plate items.',
 'Add Weldments → Fillet Bead (3 mm, full length) on tube joints and 4 mm on plates; End Caps 2 mm on open tube ends.',
 'Hole Wizard for all bolt holes (Section 13); Cut List Properties for length and mass; check total mass against Table 2.',
 'Simulation: Beam study on the weldment (joints auto-detected), loads from Table 2 × 2.5, fixed at the axle-plate bores, remote load for the row unit; compare with the hand result. Frequency study on the canopy with and without braces to confirm Section 10 (≈ 10 Hz vs. &gt; 100 Hz).'])

H1('11. Custom part 4: lugged drive wheel')
wm, wh = R['wheel_mass'], R['wheel']
p(f'<b>Geometry.</b> Rim band 100 × 3 mm, rolled to Ø380 outside and butt-welded; central web disc 4 mm (Ø374) with four Ø80 lightening and mud-relief holes on a Ø220 PCD; hub tube Ø50 × 60 long with a Ø25 H7 bore and an 8 mm keyway; sixteen transverse lugs 20 high × 5 thick × 100 long at 22.5° pitch, giving Ø420 over the lugs and an effective rolling radius of about 200 mm. Material: S235/ASTM A36 plate and flat bar, MIG welded, zinc-rich primer.')
fig('/home/claude/seeder/fig5_wheel.png', W, 'Figure 5. Drive wheel. Front view and half section.')
p(f'<b>Why these numbers.</b> The 100 mm width and 420 mm diameter set the contact area that keeps B<sub>n</sub> above 40 (Section 5.2); larger wheels would raise traction slightly but also raise the frame and the CG. Sixteen lugs give a lug pitch of 2π·210/16 = {m["lug_pitch"]*1000:.0f} mm, so {m["lugs_engaged"]:.1f} lugs are always in the 179 mm contact patch and thrust is continuous. The 20 mm lug height matches the assumed rut depth so lugs engage undisturbed soil below the surface layer. Mass per wheel is {wm["total"]:.2f} kg (rim {wm["rim"]:.2f}, web {wm["web"]:.2f}, hub {wm["hub"]:.2f}, lugs {wm["lugs"]:.2f}); it counts toward the drive-axle load.')
p(f'<b>Strength.</b> Lug bending: with two lugs engaged and a 2.5 factor, each lug carries {wh["F_lug"]:.0f} N at mid-height, σ = {wh["sigma_lug"]:.1f} MPa. Torque transfer at motor stall ({D["T_wheel_stall"]:.0f} N·m): web shear at the hub {wh["tau_web"]:.1f} MPa; 4 mm fillet welds around the hub on both sides {wh["tau_hubweld"]:.1f} MPa. All are an order of magnitude below the material limits; the wheel is sized for stiffness, wear and manufacturability.')
H2('11.1 SolidWorks modelling procedure (drive wheel, as a multibody weldment part)')
bullets([
 'Right Plane: sketch the rim cross-section as a 100 × 3 rectangle with its inner edge at R187; Revolve 360° → body "Rim".',
 'Same plane: web as a 4 × (25 → 187) rectangle centred on the rim width; Revolve, "Merge result" off → body "Web". Front face: four Ø80 circles on a Ø220 PCD (Circular Pattern), Extruded Cut through the web body only (Feature Scope).',
 'Hub: revolve a 60 × 12.5 rectangle from R12.5 to R25 → body "Hub". Cut the 8 × 3.3 keyway along the bore (Extruded Cut from the Top Plane, Feature Scope = Hub).',
 'Lug: on a plane tangent to the rim at the top, sketch 100 × 5 and extrude 20 mm radially → body "Lug"; Circular Pattern, 16 instances, bodies to pattern.',
 'Weldments → Fillet Bead: 4 mm hub–web both sides, 3 mm web–rim both sides, 3 mm each lug. Assign material "Plain Carbon Steel"/A36; Mass Properties should read about 7.5 kg.',
 'In the drive assembly: mate the hub bore concentric with the stub axle, insert the key (Toolbox, DIN 6885 A 8 × 7 × 45), and limit axial play with a shaft collar.'])

H1('12. Viability beyond the prototype')
p(f'For the proof of concept, all four engineering checks close: the agronomic targets can be met mechanically, the soil forces can be carried with adequate safety factors, traction is assured by calculated ballast, and the energy balance works with a battery buffer. The energy result also limits the concept. The planted area needs ≈ {f(E["Wh_per_ha"]/1000,1)} kWh/ha of electricity at walking speed, and the machine can carry only about 1 m² of modules, which deliver at most ≈ 175 W. A commercial planter is several metres wide and runs three to five times faster, so its power demand grows with width × speed, while the panel area it can carry grows only with its footprint. For multi-row machines, solar energy is more realistically harvested by a stationary array and stored in swappable batteries, with on-board panels supplying a fraction. That conclusion strengthens rather than weakens the research\'s environmental argument, because it moves the solar collection to where its efficiency is highest.')

H1('13. Bill of materials')
H2('13.1 Custom (to be manufactured)')
table([
 ['#', 'Part', 'Qty', 'Material / process', 'Key dimensions'],
 ['C1', 'Seed plate, 12 cells', '1 (+1 spare)', 'POM-C, CNC (or PETG print)', 'Ø140 × 10.5, cells 15.5 × 6.0, bore Ø12 H7'],
 ['C2', 'Seed meter housing + shroud + brush holder', '1', 'PETG print or 6061-T6', 'shroud ID Ø141.5, discharge port 20 × 12'],
 ['C3', 'Opener disc', '1', 'SAE 1065/65Mn, 40–45 HRC, laser cut + bevel', 'Ø250 × 4, 15° bevel, 4 × Ø8.5 on Ø75'],
 ['C4', 'Disc hub housing + 17 mm spindle', '1', 'AISI 1045, turned', 'bores Ø40 H7, flange Ø100 × 8'],
 ['C5', 'Shank plate + gauge slider', '1', 'S235 8 mm laser cut; slider AISI 1045', '300 × 220; slot 35 × 10.5'],
 ['C6', 'Chassis weldment incl. canopy and handlebar', '1', 'A500 Gr. B / SAE 1020 tube, GMAW', 'Section 10'],
 ['C7', 'Drive wheel', '2', 'S235 plate and flat bar, GMAW', 'Ø380 rim, Ø420 lugs, 100 wide'],
 ['C8', 'Stub axle', '2', 'AISI 1045 CD, turned', 'Ø25 h6 × 245, keyways 8 × 4 both ends'],
 ['C9', 'Ballast plates', '4', 'S235, flame cut', '250 × 160 × 16 (5.0 kg each), 2 × Ø11 holes'],
 ['C10', 'Press-wheel arm, row-unit lift lever, seed boot', '1 set', 'S235 / PETG', 'arm 200 long; boot for Ø25 tube'],
], [0.9*cm, 4.3*cm, 1.7*cm, 4.5*cm, W-11.4*cm])
H2('13.2 Commercial components')
table([
 ['Component', 'Qty', 'Specification used in the calculations'],
 ['Gear motor MY1016Z3', '2', '24 V, 350 W, 9.78:1, ~300 rpm out, 10.8 N·m rated, 34.3 N·m stall [12]; 9T sprocket 1/2" pitch'],
 ['Driven sprocket 48T, 1/2" pitch', '2', 'bore 25 H7 with 8 mm keyway; match chain width to motor sprocket'],
 ['Roller chain 1/2" pitch', '2 × 54 links', 'matching the motor sprocket; min. tensile strength ≥ 5 × stall pull (≈ 1.8 kN), i.e. ≥ 9 kN'],
 ['Flange bearing unit UCFL205', '4', '25 mm bore, set-screw locking; bolt holes per housing drawing'],
 ['Deep-groove bearing 6203-2RS', '2', '17 × 40 × 12'],
 ['PV module Renogy CORE 100 W 12 V', '2', '865 × 578 × 30, 5.9 kg, NOCT 47 °C, −0.32%/°C [10]; wired in series'],
 ['MPPT Victron SmartSolar 75/15', '1', '75 V max PV, 15 A, 440 W at 24 V [11]'],
 ['LiFePO₄ battery 25.6 V 20 Ah with BMS', '1', '≥ 30 A continuous discharge; mass assumed 6 kg'],
 ['Dual motor driver Cytron SmartDriveDuo MDDS30', '1', '7–35 V, 30 A continuous / 80 A (1 s) per channel [13]'],
 ['Arduino Mega 2560 (or Uno)', '1', 'reads throttle, encoder, current sensors; drives meter stepper and motor driver'],
 ['NEMA 17 stepper + ~5:1 planetary + driver', '1', 'output ≥ 1.0 N·m at ≤ 30 rpm; standard M3 mounting on 31 mm square'],
 ['Incremental encoder 600 ppr', '1', 'on gauge-wheel axle'],
 ['Hall current sensors 30 A', '2', 'firmware current limit (protects chain/shaft against stall torque)'],
 ['Gauge wheel 200 × 50, ball bearing', '1', 'rubber tread; axle bolt to suit wheel bore'],
 ['Swivel caster Ø250 with swivel lock', '1', 'used as press wheel; top-plate bolt pattern per caster datasheet'],
 ['Press spring', '1', 'compression spring giving 60 N at installed length'],
 ['Safety and wiring', '1 set', 'E-stop on handlebar, 40 A fuse, main isolator, 6 mm² cable, throttle potentiometer, IP65 enclosure'],
 ['Shaft collars Ø25, keys 8 × 7', '4 / 4', 'collars beside outer bearings; keys DIN 6885 A'],
 ['Seed tube', '1', 'smooth-bore PU, Ø25 OD, ≈ 300 mm'],
], [5.2*cm, 1.9*cm, W-7.1*cm])
H2('13.3 Fasteners (McMaster-Carr, with SolidWorks models)')
p('McMaster-Carr provides downloadable SOLIDWORKS models for each part number and a SOLIDWORKS add-in. Part numbers below marked "verified" were read from McMaster-Carr catalogue pages [14]. For socket head screws only the product family (91290A, black-oxide alloy steel, ISO 898-1 Class 12.9) was verified; the full number is fixed when the length is selected on the product page. Black-oxide screws rust outdoors, so oil them or switch to a zinc-plated family for field use.')
table([
 ['Joint', 'Fastener', 'Qty', 'McMaster part number'],
 ['Flange bearings + axle plates (through both)', 'Hex head screw M12 × 1.75 × 100, Class 8.8, zinc (size per housing holes)', '4', 'select on McMaster (not verified)'],
 ['', 'Nylon-insert locknut M12, DIN 985, Class 10, zinc', '4', '94645A230 (verified)'],
 ['', 'Washer M12, ISO 7089, zinc', '8', '91455A150 (verified)'],
 ['Row-unit hanger to CM3/CM4', 'Hex head screw M10 × 1.5 × 30, Class 8.8', '4', 'select on McMaster'],
 ['', 'Locknut M10 / washer M10', '4 / 8', '94645A220 / 91455A140 (verified)'],
 ['Disc to hub flange', 'Socket head screw M8 × 1.25 × 20, Class 12.9', '4', '91290A family'],
 ['Disc spindle to shank', 'Locknut M12 / washer M12', '1 / 2', '94645A230 / 91455A150'],
 ['Gauge slider clamp', 'Socket head screw M8 × 30 + locknut M8 + 2 washers', '2', '91290A family / 94645A210 / 91455A130'],
 ['Depth adjusting screw', 'Hex head screw M10 × 80 fully threaded + locknut M10 as jam nut', '1', 'select on McMaster / 94645A220'],
 ['Seed plate to hub', 'Socket head screw M4 × 12 + locknut M4', '3', '91290A family / 94645A101 (verified)'],
 ['Meter housing halves; meter to shank', 'Socket head screw M5 × 16 + locknut M5', '8', '91290A family / 94645A102 (verified)'],
 ['Stepper to meter housing', 'Socket head screw M3 × 8 (tapped housing)', '4', '91290A family'],
 ['Motors to motor plates', 'Socket head screw M6 × 16 + washer M6 (check motor thread)', '8', '91290A family / 91455A120 (verified)'],
 ['PV modules to cross-bars', 'Hex/socket screw M6 × 20 + locknut M6 + 2 washers', '8', '94645A205 / 91455A120 (verified)'],
 ['Canopy posts to sockets; handlebar', 'Hex head screw M8 × 50 / M8 × 60, Class 8.8 + locknut M8 + 2 washers', '8 / 4', 'select / 94645A210 / 91455A130 (verified)'],
 ['Ballast stack to tray', 'Hex head screw M10 × 90 fully threaded + locknut M10 + washers', '2', 'select / 94645A220 / 91455A140'],
 ['Press arm pivot; caster to arm plate', 'Hex screw M12 × 80 + locknut; M8 × 25 + locknuts (caster pattern)', '1 / 4', 'select / 94645A230, 94645A210'],
 ['Ballast tray to rails', 'Socket head screw M8 × 60 + locknut M8 + washers', '4', '91290A family / 94645A210 / 91455A130'],
], [4.3*cm, 6.4*cm, 1.3*cm, W-12.0*cm])
bt = R['bolts']
table([
 ['Size', 'Stress area (mm²)', 'Class 8.8: preload / torque', 'Class 12.9: preload / torque'],
] + [[k, f'{v["As"]}', f'{v["Fi_88"]/1000:.1f} kN / {v["T_88"]:.0f} N·m', f'{v["Fi_129"]/1000:.1f} kN / {v["T_129"]:.0f} N·m'] for k, v in bt.items()],
 [2.0*cm, 3.2*cm, (W-5.2*cm)/2, (W-5.2*cm)/2])
p('Table 4. Tightening torques from T = K·F<sub>i</sub>·d with K = 0.2 (plain/zinc, dry) and F<sub>i</sub> = 0.75 × proof load (proof strength 580 MPa for Class 8.8 and 970 MPa for Class 12.9). Nylon-insert locknuts and joints clamping 3D-printed parts must be tightened far less: snug plus a quarter turn for printed parts.', cap)

H1('14. Assumptions to verify and test plan')
table([
 ['Assumption', 'Value used', 'How to verify'],
 ['Soil cone index; c, φ', '600 kPa; 3 kPa, 28°', 'cone penetrometer and shear vane at the plot before testing'],
 ['Opener forces (tilled seedbed)', 'draft ≤ 131 N, vertical ≤ 373 N, side 150 N', 'spring balance on a tow rope; gauge-wheel load cell or scale under gauge wheel'],
 ['Net traction ratio', '0.35 at 15% slip', 'mark wheel, count revolutions over 20 m with and without the opener in the soil'],
 ['Motor-gearbox efficiency', '0.60', 'log battery current and voltage at 0.5 m/s'],
 ['Purchased masses (motors, battery)', '3.0 kg, 6.0 kg', 'weigh; rerun the ballast equations'],
 ['Seed size and thousand-seed mass', 'L ≤ 14, W ≤ 10, T 4–5.5 mm; 350 g', 'calliper 100 seeds of the actual lot; size cells to the largest'],
 ['Field emergence', '90%', 'seed-lot germination test'],
 ['Irradiation', '5.0 kWh/m²·day', 'INPE monthly value for the test site and month'],
], [4.6*cm, 4.6*cm, W-9.2*cm])
p('<b>Test sequence.</b> (1) Bench test of the meter on a sticky belt or grease board at 11 and 22 rpm, measuring doubles, misses and the coefficient of variation of spacing against the Kachman–Smith indices [16]; adjust brush and cell size before going to the field. (2) Static checks: weigh the machine on two bathroom scales (front and rear) to confirm N<sub>d</sub> and R<sub>row</sub>. (3) Field run on 20 m strips at 0.5, 0.7 and 1.0 m/s, digging up 50 seeds per strip to measure depth and spacing. (4) A full-day energy log to confirm Section 7.')

H1('References')
refs = [
 '[1] Vicentini, I. F. L.; Vidal, J. M.; Savi, N. C. Desenvolvimento de um modelo de semeadora movida a energia solar para a otimização do plantio de milho no Sudeste brasileiro. Brazilian International School, Semana do Conhecimento, Guarulhos, 2023 (and the sources it cites: Cruz et al., Embrapa Milho e Sorgo, 2007/2010; Fagundes, 1975; Bresolin, 1993).',
 '[2] Disc angle and tilt angle effects on forces acting on a single-disc type no-till seeder opener. Soil &amp; Tillage Research, 194, 2019.',
 '[3] Aydın, Y.; Çelik, A.; Malaslı, M. Z. Comparison of single-disc furrow openers of direct seeders in terms of furrow profile and acting forces. Harran Tarım ve Gıda Bilimleri Dergisi, 28(2), 345–356, 2024.',
 '[4] Brixius, W. W. Traction prediction equations for bias ply tires. ASAE Paper 87-1622, 1987, as adopted in ASABE D497; summary of coefficients and cone-index ranges in arXiv:2604.17991 (EcoTIM, 2026); model deviation of up to 35% in Kumar, A. A.; Tewari, V. K. J. Agriculture and Food Research, 5, 100180, 2021.',
 '[5] Optimization design on pickup finger of precision maize seed metering device. International Journal of Agricultural and Biological Engineering (ijabe.org), maize seed dimension distributions.',
 '[6] Lincoln Ag Products. Plate sizing support document (cell length along the plate edge; size to the largest seed).',
 '[7] An evaluation of seed spacing accuracy of a vacuum type precision metering unit based on theoretical considerations and experiments. Turkish Journal of Agriculture and Forestry, 36(2), 2012.',
 '[8] Peripheral speed of the plate in seed meters of corn and soybean. Ciência Rural (UFSM), SciELO Brazil.',
 '[9] Pereira, E. B. et al. Atlas Brasileiro de Energia Solar, 2ª ed. INPE, São José dos Campos, 2017; regional means reported in Revista Pesquisa FAPESP, "Para aproveitar o sol".',
 '[10] Renogy CORE 12 V 100 W rigid solar panel (16BB N-type), specifications as listed by Outback Marine (AU).',
 '[11] Victron Energy SmartSolar MPPT 75/15, specifications as listed by retailers (max. PV Voc 75 V; 440 W at 24 V).',
 '[12] MY1016Z / MY1016Z3 24 V 350 W gear motor, retailer specifications (Zbotic; Robu; Flipkart). Listings disagree; conservative values used.',
 '[13] Cytron SmartDriveDuo MDDS30, specifications, RobotShop.',
 '[14] McMaster-Carr online catalogue: metric washers (91455A), DIN 985 nylon-insert locknuts (94645A), socket head screws ISO 898-1 (91290A).',
 '[15] Budynas, R. G.; Nisbett, J. K. Shigley\'s Mechanical Engineering Design. McGraw-Hill (material properties of AISI 1045 CD, Marin factors, keyseat stress concentration, chain length).',
 '[16] Kachman, S. D.; Smith, J. A. Alternative measures of accuracy in plant spacing for planters using single seed metering. Transactions of the ASAE, 38(2), 379–387, 1995.',
 '[US 3,498,241] Fischer, R. C. Vertical seed plate planter. US Patent 3,498,241.',
]
for r_ in refs: p(r_, ParagraphStyle('ref', parent=bodyL, fontSize=11, leading=15))

def onpage(c, doc):
    c.saveState(); c.setFont('LSans', 9); c.setFillColor(MUT)
    c.drawString(2.5*cm, 1.4*cm, 'Solar-assisted maize seeder: engineering viability and detailed design')
    c.drawRightString(A4[0]-2.5*cm, 1.4*cm, f'Page {doc.page}')
    c.restoreState()
doc = BaseDocTemplate('/home/claude/seeder/Solar_Seeder_Engineering_Report.pdf', pagesize=A4,
                      leftMargin=2.5*cm, rightMargin=2.5*cm, topMargin=2.3*cm, bottomMargin=2.3*cm,
                      title='Solar-Assisted Precision Seeder: Engineering Viability and Detailed Design',
                      author='Engineering analysis of Vicentini, Vidal & Savi (2023)', initialFontName='LSans', initialFontSize=12)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')
doc.addPageTemplates([PageTemplate(id='p', frames=[frame], onPage=onpage)])
doc.build(story)
print('built')
