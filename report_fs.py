import json, math
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, Image, KeepTogether, ListFlowable, ListItem)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

FD = '/usr/share/fonts/truetype/liberation/'
for n, f in (('LSans', 'Regular'), ('LSans-B', 'Bold'), ('LSans-I', 'Italic'), ('LSans-BI', 'BoldItalic')):
    pdfmetrics.registerFont(TTFont(n, FD+f'LiberationSans-{f}.ttf'))
addMapping('LSans', 0, 0, 'LSans'); addMapping('LSans', 1, 0, 'LSans-B')
addMapping('LSans', 0, 1, 'LSans-I'); addMapping('LSans', 1, 1, 'LSans-BI')

R = json.load(open('/home/claude/seeder/results_fs.json'))
A, M, S_, T, E = R['agro'], R['mass'], R['soil'], R['tractor'], R['energy']
def f(x, n=0): return f'{x:,.{n}f}'
INK = colors.HexColor('#0b0b0b'); MUT = colors.HexColor('#52514e'); LINE = colors.HexColor('#c9c7bf'); HEAD = colors.HexColor('#eef3fb')
body = ParagraphStyle('body', fontName='LSans', fontSize=12, leading=18, alignment=TA_JUSTIFY, spaceAfter=6, textColor=INK)
bodyL = ParagraphStyle('bodyL', parent=body, alignment=TA_LEFT)
h1 = ParagraphStyle('h1', fontName='LSans-B', fontSize=15, leading=20, spaceBefore=14, spaceAfter=6, textColor=INK, keepWithNext=1)
h2 = ParagraphStyle('h2', fontName='LSans-B', fontSize=12.5, leading=18, spaceBefore=10, spaceAfter=4, textColor=INK, keepWithNext=1)
cap = ParagraphStyle('cap', fontName='LSans-I', fontSize=10, leading=13, textColor=MUT, spaceBefore=3, spaceAfter=10)
eq = ParagraphStyle('eq', fontName='LSans', fontSize=12, leading=18, leftIndent=24, spaceAfter=6, textColor=INK)
cell = ParagraphStyle('cell', fontName='LSans', fontSize=9.5, leading=12, textColor=INK)
cellB = ParagraphStyle('cellB', parent=cell, fontName='LSans-B')
title = ParagraphStyle('title', fontName='LSans-B', fontSize=20, leading=26, textColor=INK, spaceAfter=8)
sub = ParagraphStyle('sub', fontName='LSans', fontSize=12, leading=18, textColor=MUT)
story = []
def p(t, st=body): story.append(Paragraph(t, st))
def H1(t): story.append(Paragraph(t, h1))
def H2(t): story.append(Paragraph(t, h2))
def EQ(t): story.append(Paragraph(t, eq))
def bullets(items):
    story.append(ListFlowable([ListItem(Paragraph(i, body), leftIndent=14, value='•', bulletFontName='LSans') for i in items],
                              bulletType='bullet', start='•', leftIndent=14, bulletFontName='LSans'))
def table(rows, widths, head=True):
    data = [[Paragraph(str(c), cellB if (head and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    st = [('GRID', (0, 0), (-1, -1), 0.4, LINE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
          ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
          ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5)]
    if head: st.append(('BACKGROUND', (0, 0), (-1, 0), HEAD))
    t.setStyle(TableStyle(st)); story.append(t); story.append(Spacer(1, 8))
def fig(path, w, caption):
    from PIL import Image as PI
    im = PI.open(path); r_ = im.size[1]/im.size[0]
    story.append(KeepTogether([Image(path, width=w, height=w*r_), Paragraph(caption, cap)]))
W = A4[0] - 5*cm
D = '/home/claude/seeder/'
mn, mx = R['meter_nom'], R['meter_max']
tb, rl, wh, ru, cn, pe, st_ = R['toolbar'], R['rail'], R['wheel'], R['ru'], R['canopy'], R['planter_el'], R['station']
cases = R['downforce']['cases']
tr = R['transport']

# ------------------------------------------------------------------------------------------------
p('Full-Size Solar-Electric Maize Planter: Engineering Viability and Detailed Design for SolidWorks', title)
p('Companion to the proof-of-concept report. Based on: Vicentini, I. F. L.; Vidal, J. M.; Savi, N. C. <i>Desenvolvimento de um modelo de semeadora movida a energia solar para a otimização do plantio de milho no Sudeste brasileiro</i>. Brazilian International School, 2023.', sub)
p('Prepared 25 October 2026. Dimensions in millimetres unless stated. Every value is either cited, flagged as an assumption, or calculated from those; the calculation scripts are available on request so any assumption can be replaced and the design re-run.', sub)
story.append(Spacer(1, 6))

H1('1. Answer and executive summary')
p('<b>Yes, a full-size tractor-drawn version is viable, and it can be built from commercial power equipment that is on sale today.</b> The configuration that closes every engineering check is:')
bullets([
 f'<b>Planter:</b> a 12-row, 0.50 m row-spacing, rigid-frame, trailed precision planter (6.0 m working width), which sits at the top of the 7–12-row range of Brazilian mechanical-meter planters such as the Tatu Marchesan PST4 [3]. It keeps the research\'s choices: tilled seedbed, 80,000 plants/ha, 3–5 cm depth, gravity seed metering.',
 '<b>Seeding system powered by the sun:</b> each row has an electrically driven 12-cell vertical seed plate. The meters, controller and sensors run from a 820 W photovoltaic canopy and a 25.6 V battery carried on the planter itself, with no electrical connection to the tractor.',
 f'<b>Traction from a grid- and solar-charged battery-electric tractor:</b> the New Holland T4 Electric Power (55 kW rated, 110 kWh, 400 V, cab, commercially available) [8]. At {f(A["C_eff"],2)} ha/h effective capacity it plants about {f(E["ha_charge"])} ha per charge, or about {f(E["ha_day_2charges"])} ha in a day with one fast recharge, using ≈ {f(E["kWh_ha"],1)} kWh/ha.',
 f'<b>Where the solar energy comes from:</b> the tractor battery is charged from a farm photovoltaic array. Grid-connected under Brazil\'s net-metering law (Lei 14.300/2022), about {f(st_["kWp_net"],1)} kWp covers the energy of planting 1,000 ha a year; charging directly from the sun in season needs about {f(st_["kWp_direct"])} kWp plus stationary storage.'])
p('A solar-diesel hybrid tractor is not needed for this planter, and I found none on the market. Two commercial diesel-electric tractors can supply 100 kW of electricity to an implement: the John Deere 8R 410 eAutoPowr [10] and the autonomous AgXeed AgBot 5.115T2 [11]. Both are the right answer only for much larger planters, or for planters with fertilizer shanks. Section 3 explains why.')
p(f'The design below gives every dimension, the material of every custom part, the calculations behind them, and a SolidWorks modelling procedure for the four requested parts: the 12-cell vertical gravity seed disc, the depth-gauged opener, the chassis frame and the drive (ground) wheel. Under a 2.5× dynamic load factor, all custom structural parts show safety factors of 2.1 or more against yield or fatigue. The design analysis also uncovered three real constraints, which are treated explicitly: the frame needs {f(M["ballast"])} kg of ballast to react the row-unit downforce; the PV canopy needs bracing to avoid resonance with the tractor tyre lugs; and the 6.1 m width exceeds Brazil\'s 2.60 m road limit.')

H1('2. What a normal industrial corn planter looks like, and the size chosen')
p('Commercial corn planters span a very wide range. In Brazil, mid-size mechanical-meter planters such as the Tatu Marchesan PST4 are offered with 7 to 12 rows, use 15" × 15" offset double-disc seed openers, run on 7.00 × 16 tyres, and need about 100–115 cv for 12 rows with fertilizer [3]. Large planters with pneumatic (vacuum) meters run from about 22 to 45 rows (Baldan, Jumil, John Deere DB74) and need 180–340 cv [2]. Mechanical meters are generally limited to 4–6 km/h, while vacuum meters reach 10–12 km/h [2].')
p('<b>Choice: 12 rows at 0.50 m.</b> The research specifies a gravity (mechanical) meter, which limits speed. Twelve rows is the largest standard size in the mechanical-meter class [3]. Above it, manufacturers switch to vacuum meters and folding frames, which would contradict the research. The 0.50 m spacing comes directly from the research (Fig. 1, Cruz et al.).')
p('<b>Seed only, tilled seedbed.</b> Brazilian planters are normally seed-fertilizer planters with a fertilizer shank ("facão") for no-till, and that shank is what drives their 100+ cv power requirement. The research specifies a conventionally tilled seedbed and does not discuss fertilizer, so this planter places seed only (fertilizer pre-applied or broadcast). Section 13 shows what changes if a fertilizer shank is added.')

H1('3. Power source: what exists commercially and what was chosen')
table([
 ['Option (status, Oct 2026)', 'Power / energy', 'Fit for this 12-row seed-only planter'],
 ['New Holland T4 Electric Power, battery-electric, grid/solar charged; on sale [8]', '74 hp (55 kW) rated, 65 hp PTO; 110 kWh, 400 V; ~4 h typical use; ~1 h fast charge to 100%; ≈ 4,900 kg; cab; exportable 110/220 V power', '<b>Chosen.</b> Draft need is about 5 kN at 6 km/h (Section 7); traction, power and runtime all close. It is not adequate for fertilizer-shank planters.'],
 ['John Deere E-Power, battery-electric; prototype, US production planned 2027 [9]', '130 hp; up to 5 × 39 kWh packs', 'Would fit a 12-row planter with fertilizer shank once it ships.'],
 ['John Deere 8R 410 eAutoPowr, diesel-electric power-split CVT; on sale [10]', '410 hp; up to 100 kW external electrical power (480 V, 3-phase)', 'Oversized by about 4×. Appropriate for 24–45-row electric-drive planters.'],
 ['AgXeed AgBot 5.115T2, diesel engine feeding an electric drive train; autonomous, no cab [11]', '115 kW Deutz diesel; optional 100 kW, 700 V electrical output to implements; 7.8 t', 'Power matches a fertilizer-shank 12-row planter, but it is not "drivable"; no operator station.'],
], [5.2*cm, 5.0*cm, W-10.2*cm])
p('Electric tractors on sale rarely exceed 100–130 hp [8]. No commercial tractor uses on-board solar as a prime mover. The physics explains why: the T4 needs about 22 kW at the battery while planting, and the entire roof area of a tractor plus planter could hold perhaps 10 m² of modules, about 2 kW at noon. So the realistic "solar-powered" machine is solar-charged. That architecture is exactly the T4\'s, which New Holland states can be charged from grid, solar, biodigester or wind power [8].')

H1('4. From agronomy to machine parameters')
p(f'With 0.50 m rows and 80,000 plants/ha, there are 4.0 plants per metre of row. Allowing 90% emergence (an assumption to replace with the lot\'s germination test) gives {f(A["seeds_m"],3)} seeds/m, i.e. an in-row seed spacing of <b>{f(A["X_mm"])} mm</b>, and {f(A["seed_kg_ha"],1)} kg/ha of seed at an assumed thousand-seed mass of 350 g. Each row carries a 56 L hopper (≈ {f(A["hop_kg"],1)} kg of seed at an assumed 0.72 kg/L), so the machine plants about {f(A["ha_per_fill"],1)} ha per fill.')
p(f'<b>Speed.</b> Design speed is 6 km/h (1.67 m/s), with 7 km/h maximum, the upper end of the mechanical-meter range [2]. Working width is 6.0 m, giving a theoretical capacity of {f(A["C_th"],1)} ha/h and, with the typical 65% field efficiency for row-crop planters in ASABE D497 [4], an effective {f(A["C_eff"],2)} ha/h.')
p('<b>Wheel lanes.</b> Rows sit at ±250, ±750 … ±2,750 mm from the centre-line, so every multiple of 500 mm is a mid-row lane. The two planter wheels run in the lanes at ±1,500 mm. Successive passes are 6.0 m apart, so they never run on a seed row. A tractor with its track set to 1.5 m or 2.0 m also runs in mid-row lanes.')

H1('5. General arrangement')
p('The planter is a trailed implement. An A-frame tongue of two main rails runs from a clevis hitch on the tractor drawbar to the toolbar. The rails continue rearward between rows 1.25 and 1.75 m on each side and end in swing arms carrying the two ground wheels behind the row units. Twelve row units hang from the 7 × 7 in toolbar on parallel linkages. The 820 W PV canopy sits over the A-frame, ahead of the toolbar, which keeps it clear of hopper filling and of the tractor in sharp turns. A ballast bridge over the closing-wheel area carries the steel ballast. Two hydraulic cylinders rotate the swing arms to raise the frame 289 mm for headland turns and transport.')
table([
 ['Item', 'Dimension / position (x rearward of toolbar centre-line, y lateral, z above ground)'],
 ['Planter length / width / height', '5,350 (hitch pin to wheel rear) / 6,100 (toolbar) / 1,635 (PV top), hopper lids ≈ 1,100'],
 ['Rows', '12 at 500 mm; y = ±250 … ±2,750; working width 6,000'],
 ['Toolbar', 'HSS 7 × 7 × 1/4 in (177.8 × 177.8 × 6.35), 6,100 long, centre z = 616 working, 905 raised'],
 ['Main rails', 'HSS 10 × 4 × 5/16 in (254 × 101.6 × 7.94) on edge; hitch at x = −3,200, z = 500; rails at y = ±1,500 behind the toolbar to x = 1,350'],
 ['Ground wheels', 'BKT AS 504 7.50-16 8PR, OD 803, axle at x = 1,750, y = ±1,500; swing arm 450'],
 ['Row unit', 'links 400; opener discs Ø381 at x = 550; gauge wheels Ø381 at x = 590; meter Ø140 at (620, 400); closing wheels at x = 1,150'],
 ['PV canopy', '2 modules 1,722 × 1,134, total 3,444 × 1,134, centred x = −1,250, top z = 1,635'],
 ['Masses', f'row unit {f(M["m_ru"])} kg empty + {f(M["m_seed"])} kg seed; frame {f(M["m_frame"])} kg; ballast {f(M["ballast"])} kg; total {f(M["m_total_empty"])} kg empty, {f(M["m_total_full"])} kg full'],
 ['Centre of gravity (full)', f'x = {f(R["cg"]["x"]*1000)}; z = {f(R["cg"]["z_work"]*1000)} working, {f(R["cg"]["z_raised"]*1000)} raised'],
], [4.2*cm, W-4.2*cm])
fig(D+'fs_fig1_ga.png', W, 'Figure 1. General arrangement: side view (top) and plan view (bottom). The tractor outline is schematic.')

H1('6. Loads, downforce and static equilibrium')
H2('6.1 Soil forces')
p(f'<b>Draft.</b> ASABE D497.4 gives row-crop planter draft as D = F<sub>i</sub>(A + B·S) per row, where S is speed in km/h. For a drawn, seeding-only planter in a prepared seedbed, A = 260 N and B = 13 N per km/h, with a ±15% range [4]; the soil factor is 1.0 for fine (clay) soils, which applies to the clayey soils of the Southeast. At 6 km/h this gives {f(S_["D_row_nom"])} N per row nominal and {f(S_["D_row_up"])} N at the upper bound: {f(S_["D_tot_nom"]/1000,2)} kN and {f(S_["D_tot_up"]/1000,2)} kN for 12 rows. The D497 values include implement rolling resistance. For structural design, the upper-bound draft is multiplied by the 2.5 dynamic factor, giving {f(S_["D_struct"])} N per row.')
p('<b>Vertical forces.</b> PAMI\'s evaluation of a John Deere 7000 planter, which uses the same 15 in (381 mm) opener discs and gauge wheels, reported seed-opener vertical forces of 180–280 lb (800–1,250 N) and closing-wheel forces of 40–85 lb (180–380 N) [5]. These ranges are used directly. A minimum gauge-wheel load of 250 N (assumption) keeps depth control.')
H2('6.2 Row-unit downforce budget')
p('Each row unit floats on its parallel linkage. Its weight plus the downforce spring S must equal the sum of the opener, gauge and closing reactions:')
EQ('W<sub>ru</sub> + S = V<sub>o</sub> + G + P<sub>c</sub>,  so  S<sub>req</sub> = V<sub>o</sub> + P<sub>c</sub> + G<sub>min</sub> − W<sub>ru</sub>')
rows_ = [['Hopper fill', 'Soil', 'Row-unit weight (N)', 'Spring needed (N)', 'Setting used (N)', 'Gauge load (N)', 'Wheel load, both (N)', 'Hitch load (N)']]
for c in cases:
    rows_.append([f'{int(c["fill"]*100)}%', 'firm' if c['soil'] == 'firm' else 'loose', f(c['W_ru']), f(c['S_req']), f(c['S_used']), f(c['G']), f(c['N_w']), f(c['V_h'])])
table(rows_, [1.6*cm, 1.3*cm, 2.2*cm, 2.0*cm, 2.0*cm, 1.9*cm, 2.3*cm, W-13.3*cm])
p(f'Table 2. Downforce cases. "Firm" is V<sub>o</sub> = 1,250 N with P<sub>c</sub> = 380 N; "loose" is V<sub>o</sub> = 800 N with P<sub>c</sub> = 180 N. Springs are adjustable 0–900 N in 150 N steps.', cap)
p(f'<b>Why the frame needs ballast.</b> The spring force pushes the row unit down and the frame up. With twelve rows at 600 N, 7.2 kN of the frame\'s weight is transferred to the soil. If the frame is too light, its wheels lift off, the toolbar rises and the downforce collapses; this is the reason commercial planters carry weight or use active weight transfer. The equilibrium equations in Section 6.3 show that without ballast the ground-wheel load would fall below zero in the firm-soil, near-empty-hopper case. Requiring at least 1.5 kN on each wheel gives a ballast of <b>{f(M["ballast"])} kg</b>: a 75 kg transverse ballast bridge at x = 1,100–1,200 (above the closing-wheel area, behind the hoppers) carrying twelve 25 kg steel plates. If a field needs the 900 N spring setting, add plates and rerun the equations.')
H2('6.3 Equilibrium of the whole planter')
p('Taking the whole planter (frame plus row units) as one free body in the side view, with vertical hitch reaction V<sub>h</sub>, total wheel reaction N<sub>w</sub>, row-unit ground reactions, the drawbar pull H at hitch height z<sub>h</sub> = 0.50 m, and the soil draft at ground level:')
EQ('ΣF<sub>z</sub> = 0:  V<sub>h</sub> + N<sub>w</sub> + Σ(V<sub>o</sub> + G + P<sub>c</sub>) = ΣW')
EQ('ΣM<sub>wheel contact</sub> = 0:  V<sub>h</sub>(x<sub>w</sub> − x<sub>h</sub>) = Σ W<sub>i</sub>(x<sub>w</sub> − x<sub>i</sub>) − Σ R<sub>j</sub>(x<sub>w</sub> − x<sub>j</sub>) + H·z<sub>h</sub>')
p(f'With x<sub>h</sub> = −3.20 m and x<sub>w</sub> = +1.75 m, the results in Table 2 follow. The hitch load in work is 4.8–6.3 kN, which also adds traction to the tractor\'s rear axle. In <b>transport</b> (raised, hoppers full, ballast fitted) the hitch carries {f(tr["V_h"]/1000,1)} kN ({f(tr["V_h_kg"])} kg) and each wheel {f(tr["N_wheel_kg"])} kg. That is {f(tr["util_30"]*100)}% of the tyre\'s 1,360 kg rating at 30 km/h [12], so road speed is limited to 30 km/h. The T4\'s drawbar vertical rating is not published in the sources found and must be confirmed before road use; emptying the hoppers before transport reduces both loads.')

H1('7. Tractor matching and energy')
fn, fu, sl = T['flat_nominal'], T['flat_upper'], T['slope3_upper']
p('The T4\'s traction was estimated with the ASABE D497 (Brixius) equations for radial tyres [4]: gross traction ratio 0.88(1 − e<sup>−0.1B<sub>n</sub></sup>)(1 − e<sup>−7.5s</sup>) + 0.04; motion resistance ratio 1/B<sub>n</sub> + 0.04 + 0.5s/√B<sub>n</sub>. Inputs: 4,900 kg [8], wheelbase 2,131 mm [8], a 40/60 static axle split, tyres 280/70R20 front and 420/70R28 rear, and cone index 600 kPa. The axle split, tyres and cone index are assumptions, because the published sources do not give them. Drawbar pull transfers weight from the front axle to the rear, and the hitch load adds to the rear.')
table([
 ['Case at 6 km/h', 'Drawbar pull (kN)', 'Slip', 'Tractive eff.', 'Axle power (kW)', 'Battery power (kW)'],
 ['Flat, nominal draft', f(fn['NT']/1000, 2), f'{fn["s"]*100:.1f}%', f'{fn["TE"]:.2f}', f(fn['P_axle']/1000, 1), f(fn['P_batt']/1000, 1)],
 ['Flat, upper-bound draft', f(fu['NT']/1000, 2), f'{fu["s"]*100:.1f}%', f'{fu["TE"]:.2f}', f(fu['P_axle']/1000, 1), f(fu['P_batt']/1000, 1)],
 ['3% slope, upper-bound draft', f(sl['NT']/1000, 2), f'{sl["s"]*100:.1f}%', f'{sl["TE"]:.2f}', f(sl['P_axle']/1000, 1), f(sl['P_batt']/1000, 1)],
], [5.0*cm, 2.5*cm, 1.5*cm, 2.2*cm, 2.4*cm, W-13.6*cm])
p(f'Battery power is the axle power divided by the driveline (0.90) and motor-plus-inverter (0.92) efficiencies, plus 3 kW of auxiliaries (cooling, cab, hydraulic standby); all three figures are assumptions. Even the slope case uses only about half of the 55 kW rating. Tractive efficiency is low (0.43–0.56) because the tractor spends more energy moving its own 4.9 t than pulling the light planter; for this planter the T4 is limited by weight, not power. Slip stays below 4%.')
p(f'<b>Runtime.</b> Usable battery energy is taken as 90% of 110 kWh = 99 kWh (assumption). Averaging straight work (65% of field time) with turns and refills (35% of the time, assumed at 40% of working power) gives {f(E["P_avg"]/1000,1)} kW, a runtime of <b>{f(E["t_run"],1)} h</b> and <b>{f(E["ha_charge"])} ha per charge</b> ({f(E["kWh_ha"],1)} kWh/ha). New Holland quotes about 4 h for typical use and up to 8 h for light work [8]; light-draft planting sits between those. A working day of two runs with a one-hour fast charge between them plants about {f(E["ha_day_2charges"])} ha.')
fig(D+'fs_fig6_power.png', W, 'Figure 6. Power flow averaged over field time. The seed meters, powered separately by the planter\'s own PV, need only about 30 W of shaft power: seed metering is energetically trivial, and traction is everything.')
p(f'<b>Solar charging station.</b> Two charges a day draw about {f(st_["E_day"])} kWh from the charger (95% efficiency assumed). With 5.0 kWh/m²·day irradiation in the Southeast [16] and a performance ratio of 0.78 (assumption), each kWp of PV yields {f(st_["yield_day"],1)} kWh/day. Two routes:')
bullets([
 f'<b>Grid-connected with net metering (recommended).</b> Under Lei 14.300/2022, surplus generation becomes energy credits valid for up to 60 months, and systems up to 75 kW count as microgeneration [17]. Planting is seasonal, so the array only has to match annual energy: at 1,000 ha/year (an example) the planter tractor uses about {f(st_["E_year"]/1000,1)} MWh, covered by about {f(st_["kWp_net"],1)} kWp, roughly {f(st_["area_net"])} m² of modules.',
 f'<b>Off-grid, charging in season directly from the sun.</b> This needs about {f(st_["kWp_direct"])} kWp (≈ {f(st_["area_direct"])} m²) plus a stationary battery of at least one tractor charge (≈ 110 kWh) to deliver a one-hour fast charge. It is technically possible but costs much more than the grid route.'])

H1('8. Planter electrical system (on-board solar)')
p(f'<b>Loads.</b> Twelve meter drives at an assumed 12 W average each (3.9 W shaft power at the meter plus motor and driver losses), a 40 W controller and display, 12 W of seed sensors and 20 W of lights: {f(pe["P_loads"])} W in total. <b>Supply.</b> Two Canadian Solar HiKu CS6R-410MS modules (1,722 × 1,134 mm, 410 W, V<sub>mp</sub> 31.2 V, V<sub>oc</sub> 37.2 V, NOCT 41 °C, −0.34%/°C power coefficient, −0.26%/°C V<sub>oc</sub> coefficient [14]) are wired in series. V<sub>mp</sub> is {f(pe["Vmp"],1)} V and the cold-morning (5 °C) V<sub>oc</sub> is {f(pe["Voc_cold"],1)} V, inside the 100 V limit of a Victron SmartSolar MPPT 100/30, which accepts up to 880 W into a 24 V battery [15]. Storage is a 25.6 V, 100 Ah LiFePO<sub>4</sub> battery: {f(pe["E_bat"])} Wh usable at 80% depth, i.e. {f(pe["hrs_bat"],1)} h with no sun.')
p(f'<b>Thermal behaviour.</b> At 1,000 W/m² and 30 °C, the NOCT relation T<sub>c</sub> = T<sub>a</sub> + (NOCT − 20)/800 × G gives a cell temperature of {f(pe["Tc"],1)} °C and an output of {f(pe["P_pv_hot"])} W. The modules must reject about {f(pe["heat_rej"]/1000,1)} kW of heat, so they are mounted on an open frame with air below them. Daily harvest is ≈ {f(pe["E_pv_day"]/1000,1)} kWh against ≈ {f(pe["E_need_10h"]/1000,1)} kWh needed for a 10 h day, so the planter is energy-autonomous on average days. As a backup, the T4\'s exportable 110/220 V outlets [8] can run a small charger.')
p('<b>Control.</b> A mobile controller (IP67, CAN) reads ground speed from a 600-pulse/rev encoder on one ground wheel. That wheel is towed and does not slip under drive torque; it is cross-checked against a GNSS speed sensor. The controller commands each meter motor\'s speed in proportion to ground speed, and an optical sensor in each seed tube counts seeds. Individual row shut-off avoids overlap at point rows, a feature mechanical ground-drive planters lack.')

H1('9. Custom part 1: 12-cell vertical gravity seed plate')
p('The plate geometry is the one developed and verified in the proof-of-concept report, because the meter works per row and the seed is the same. Outer diameter is 140 mm, plate thickness 10.5 mm, and there are twelve cells at a 30° pitch. Each cell is 15.5 mm long along the rim and 6.0 mm deep radially, with R1.5 lead-ins. The cells are sized to large flat hybrid seed (11–14 × 8–10 × 4–6 mm) [24], and two seeds cannot fit in one cell, which provides singulation. A brush singulator and a spring ejector work at the discharge point. What changes at full size is the speed:')
table([
 ['Quantity', '6 km/h (design)', '7 km/h (max)', 'Limit / reference'],
 ['Seed release rate', f'{mn["seeds_s"]:.2f} seeds/s', f'{mx["seeds_s"]:.2f} seeds/s', '16 seeds/s upper limit [21]'],
 ['Plate speed', f'{mn["rpm"]:.1f} rpm', f'{mx["rpm"]:.1f} rpm', 'motor range 0.05–200 rpm [13]'],
 ['Rim (peripheral) speed', f'{mn["v_rim"]:.3f} m/s', f'{mx["v_rim"]:.3f} m/s', '0.34 m/s upper limit for good singulation [21]'],
 ['ω²r/g at the cell', f'{mn["Fr"]:.3f}', f'{mx["Fr"]:.3f}', 'much less than 1: gravity governs filling and release'],
 ['Time a cell spends in the 120° fill zone', f'{mn["t_fill"]:.2f} s', f'{mx["t_fill"]:.2f} s', '—'],
], [5.0*cm, 3.0*cm, 3.0*cm, W-11.0*cm])
p('The 140 mm diameter is the largest that stays under the 0.34 m/s rim-speed limit at 7 km/h with twelve cells: D<sub>max</sub> = 2 × 0.34/ω<sub>max</sub> = 150 mm. That is why the research\'s 12-cell gravity plate sets the planter\'s top speed at 7 km/h. Laboratory work on Brazilian meters found that the share of acceptable spacings falls steadily as rim speed rises from 0.09 to 0.38 m/s [21], so the meter should be calibrated on a grease belt before field use.')
p(f'<b>Drive.</b> Each meter is driven by an Oriental Motor BLV Series R Type brushless DC motor (BLMR5100K-GFV-F, 100 W, 24–48 VDC) with a GFV5G20 20:1 gearhead and BLVD-KRD driver. Rated output torque is 50 lb-in (5.65 N·m) over 0.05–200 rpm [13], against a 1.0 N·m design requirement (5.6× margin). The page did not state product status, so confirm availability; any 24 V brushless gearmotor delivering ≥ 1 N·m at 45 rpm with an encoder will do. The plate bolts to an aluminium hub on the gearhead shaft (3 × M4 on a 30 mm PCD).')
p(f'<b>Seed delivery: an honest limitation.</b> The plate discharges 380 mm above the furrow floor. Free fall takes {R["drop"]["t"]:.3f} s, so a ±15% scatter in tube transit time displaces seeds by ±{f(R["drop"]["err_nom"])} mm at 6 km/h, about 31% of the 225 mm spacing. That is inside the 0.5X–1.5X band used to classify doubles and misses [22], but spacing uniformity will be poorer than with a vacuum meter and belt delivery. Mitigations, in order: a curved seed tube whose exit velocity has a rearward component, lowering the meter, or limiting speed to 5 km/h.')
fig(D+'fig2_plate.png', W, 'Figure 2. Seed plate (identical to the proof-of-concept design; one per row, 12 per machine plus spares).')
H2('9.1 SolidWorks modelling procedure')
bullets([
 'New part, MMGS units. Material: create "Acetal copolymer POM-C" (E ≈ 2.8 GPa, ρ = 1,410 kg/m³, α ≈ 110 × 10<sup>−6</sup> /K) if it is not in the library.',
 'Front Plane: sketch Ø140 and Ø12 concentric circles. Extruded Boss, Mid Plane, 10.5 mm.',
 'On the front face, sketch one cell: a slot whose chord along the rim is 15.5 mm, symmetric about a vertical construction line, 6.0 mm deep radially, with its floor an arc concentric with the plate. Extruded Cut, Through All.',
 'Fillet the two cell entry edges R1.5 (not the floor). Circular Pattern of the cut and fillet: 12 instances, 360°, equal spacing.',
 'Hole Wizard: 3 × Ø4.5 through on a Ø30 PCD. Use DimXpert to apply the H7 tolerance to the Ø12 bore.',
 'In the row-unit assembly, model the meter housing shroud at Ø141.5 (0.75 mm radial clearance, kept positive under a 30 K temperature rise) and run Interference Detection.',
 'Make the plate diameter and cell count global variables so the rim-speed check (D ≤ 2 × 0.34/ω) can be repeated for other cell counts.'])

H1('10. Custom part 2: depth-gauged double-disc opener')
dg = R['disc_geom']
p(f'<b>Configuration.</b> The opener uses two flat discs, Ø381 × 5 mm (15 in, the same size as commercial openers [3][5]), each toed in 5.5° about a vertical axis (11° included angle), with the leading disc 12.7 mm ahead. The discs touch at a point {f(ru["x_conv_mm"])} mm ahead of the axle line, which at 50 mm depth is at the soil surface, and they open a V-slot about {f(ru["gap_bottom_mm"])} mm wide at the axle line. A 20 mm wide seed tube fits between them just behind the axle. At 25, 50 and 75 mm depth each disc engages the soil over arcs of {f(dg[0][1])}°, {f(dg[1][1])}° and {f(dg[2][1])}°. Material: carbon spring steel (SAE 1065 / 65Mn class) through-hardened to 40–45 HRC, with a 15° single bevel on the outer 10 mm. Hardness is specified for abrasion life; the strength check passes without it.')
p(f'<b>Disc strength.</b> The soil wedge pushes the discs apart; the lateral force per disc is assumed to be half its vertical share, {f(ru["F_side_disc"])} N (assumption, to be checked in Simulation and field tests). Acting at r = 170 mm about the edge of a Ø120 clamp flange, with the 2.5 dynamic factor, it produces M = {f(ru["M_disc"],1)} N·m. On a 60° sector the stress is σ = 6M/(b·t²) = {f(ru["sig_disc"])} MPa, a safety factor of {ru["n_disc"]:.1f} against an assumed 1,100 MPa yield strength for the hardened steel. A 4 mm disc would reach 513 MPa in the same model, which is why 5 mm was chosen.')
p(f'<b>Hubs.</b> Each disc runs on two 6204-2RS bearings, 25 mm apart. Combining vertical (625 N), draft (194 N) and the side-force couple gives a worst bearing load of {f(ru["R_b"])} N. With C = 13.5 kN (catalogue value for 6204; confirm for the chosen brand), L<sub>10</sub> = {f(ru["L10_Mrev"])} million revolutions, or about {f(ru["L10_km"]/1000)} thousand km of travel. The 25 mm AISI 4140 spindle root carries {f(ru["sig_spd"])} MPa (n = {ru["n_spd"]:.1f}).')
p(f'<b>Depth gauge.</b> Two commercial 381 × 102 mm (15 × 4 in) gauge wheels flank the discs, centred 40 mm behind the disc axle. Because disc and gauge wheel have the same radius, depth simply equals the height of the gauge-wheel axle above the disc axle: <b>d = Δz</b>. Each gauge arm (180 mm, pivoted on the shank) rests on a central rocker under a T-handle with ten notches in 5 mm steps, covering 25–75 mm. The rocker balances the two wheels so that one wheel in a wheel track does not change depth. The highest gauge load in Table 2 is {f(ru["G_max"])} N for the pair; the arm stress (50 × 20 flat bar, 2.5 dynamic factor) is {f(ru["sig_garm"])} MPa.')
p(f'<b>Shank, linkage and mounting.</b> The shank is a welded box (10 mm side plates, S355) carrying the disc spindles, gauge-arm pivot, meter, hopper and closing-arm pivot. The parallel links are 400 mm long with 180 mm vertical spacing. Under structural draft each link carries up to {f(ru["F_link"]/1000,1)} kN, far below its {f(ru["Pcr_link"]/1000)} kN buckling load (60 × 10 flat bar). The row unit clamps to the toolbar with a 12 mm hanger plate and two McMaster square U-bolts (1/2"-13, 7 in inside width). In transport, the row unit\'s moment about the toolbar loads each U-bolt leg to {f(ru["F_leg"]/1000,1)} kN with the dynamic factor, against a proof load of about {f(ru["F_proof_leg"]/1000)} kN for a 1/2" leg in low-carbon steel.')
fig(D+'fs_fig2_rowunit.png', W, 'Figure 3. Row unit in working position.')
fig(D+'fs_fig3_opener.png', W, 'Figure 4. Double-disc opener and depth gauge: side view at 50 mm depth, and plan view of the 11° included angle.')
H2('10.1 SolidWorks modelling procedure')
bullets([
 '<b>Disc (part):</b> Right Plane, Ø381 and Ø40 circles; Extrude 5 mm. Chamfer the outer edge 10 × 15° on one face. Hole Wizard: 4 × Ø10.5 on an 85 mm PCD. Material: AISI 1065 (or a custom 65Mn); note "through-harden 40–45 HRC" on the drawing. Make a mirrored configuration for the left disc.',
 '<b>Hub housing:</b> revolve a stepped profile: bearing bores Ø47 H7 × 14 from each side with a 25 mm spacer land, and a Ø120 × 10 flange with 4 × M10 tapped on an 85 mm PCD. Insert 6204-2RS bearings from the SOLIDWORKS Toolbox.',
 '<b>Spindle:</b> revolve Ø25 root (30 mm long, welded into the shank) → Ø20 k6 bearing seat (45 mm) → M20 × 1.5 thread. Material: AISI 4140 quenched and tempered.',
 '<b>Shank weldment:</b> 3D sketch of the side-plate outline; Sheet Metal base flange 10 mm for each plate (flat patterns for laser cutting); weld in the spindle bosses rotated ±5.5° about the vertical axis. Define the toe angle with a global variable so it can be varied.',
 '<b>Gauge arms:</b> 50 × 20 flat bar, 180 mm between the pivot (Ø20) and the gauge-wheel axle (M16). In the assembly, drive the rocker with a Distance mate equal to the global variable "depth", so changing depth moves both gauge wheels.',
 '<b>Check:</b> add a ground-plane sketch and a driven dimension from ground to the disc bottom; confirm it equals the depth for 25/50/75 mm. Run Simulation on one disc: fixed on the clamp annulus, 781 N lateral plus 1,560 N vertical (2.5 × 625 N) on the engaged rim arc.'])

H1('11. Custom part 3: chassis frame weldment')
p(f'<b>Structure and load path.</b> The frame is a trailed A-frame: two main rails converge on a clevis hitch and pass under the toolbar to the wheel pivots, so the rails, not the toolbar, carry the machine\'s weight to the hitch and wheels. Toolbar loads enter the rails at two nodes (y = ±1,500), keeping toolbar spans short. Members: toolbar HSS 7 × 7 × 1/4 in, 6,100 long ({f(M["m_tb_per_m"],1)} kg/m); main rails HSS 10 × 4 × 5/16 in on edge ({f(M["m_rail_per_m"],1)} kg/m), A-frame legs 3,534 long at 25.1° to the centre-line, rear legs 1,350; cross brace HSS 4 × 4 × 1/4 in, 1,500 long at x = −1,600; hitch clevis of two 25 mm plates for a Ø32 pin; ballast bridge (two HSS 4 × 4 posts and an HSS 6 × 4 beam, 3,000 long, at x = 1,150, top z = 700); PV posts HSS 2 × 2 × 3/16 in, 1,050 high, with four diagonal braces. Material: ASTM A500 Grade B (F<sub>y</sub> = 317 MPa) or the Brazilian equivalent, GMAW with ER70S-6 wire.')
p(f'<b>Rail clearance.</b> Behind the toolbar, each rail (101.6 mm wide) runs between the gauge wheels of rows 1.25 and 1.75 m with {f(rl["clear_gauge_mm"])} mm of clearance on each side, and below the hoppers. This is the tightest clearance on the machine, so check it in SolidWorks with Interference Detection over the full row-unit travel.')
p(f'<b>Toolbar (transport, hoppers full, 2.5× dynamic factor).</b> Treated as a beam on the two rail nodes with 1,550 mm overhangs carrying three row units each ({f(tb["W_full"])} N each): bending moment at the node {f(tb["M_sup"]/1000,2)} kN·m, giving σ = {f(tb["sigma"],1)} MPa. Each row unit hangs {f(tb["e"]*1000)} mm behind the toolbar axis, so the three outboard units twist the toolbar by {f(tb["T_node"]/1000,2)} kN·m, giving τ = T/(2A<sub>m</sub>t) = {f(tb["tau"],1)} MPa. Von Mises stress is {f(tb["vm"],1)} MPa, a safety factor of <b>{tb["n"]:.1f}</b>. In work, draft adds horizontal bending of {f(tb["M_h_work"]/1000,2)} kN·m and torsion of {f(tb["T_work"]/1000,2)} kN·m (von Mises {f(tb["vm_work"],1)} MPa). Static tip deflection is under 1 mm.')
p(f'<b>Main rails.</b> Each rail is a beam simply supported at the hitch and the wheel, loaded by half the row units (at their centre of gravity, x = {f(tb["e"]*1000)}), the toolbar, PV, ballast and its own weight. The maximum moment is {f(rl["M_max"]/1000,1)} kN·m at x ≈ {f(rl["x_at"]*1000)} mm; with the 2.5 factor σ = {f(rl["sigma"])} MPa, safety factor <b>{rl["n"]:.1f}</b>; static deflection is {f(rl["defl_mm"],1)} mm. The rails could be lighter, but their mass is useful: every kilogram of frame is a kilogram less ballast (Section 6.2).')
p(f'<b>Dynamics: canopy vibration.</b> The PV canopy (≈ {f(cn["m"])} kg on four 1,050 mm posts) has a lateral natural frequency of {f(cn["f_un"],1)} Hz without bracing. The tractor\'s tyre lugs (assumed 0.20 m pitch) excite {f(cn["f_lug_6"],1)}–{f(cn["f_lug_7"],1)} Hz while planting and sweep through 13 Hz on the road at about 9.4 km/h, on the way to {f(cn["f_lug_30"])} Hz at 30 km/h. Four diagonal braces raise the first mode to about {f(cn["f_br"])} Hz, well clear of all excitation. <b>Wind:</b> 30 km/h transport plus a 15 m/s gust gives q = {f(cn["q"])} Pa; with a force coefficient of 1.3 the canopy sees {f(cn["F_wind"]/1000,2)} kN, carried by the braces.')
p(f'<b>Stability and transport.</b> Raised and full, the CG is {f(R["cg"]["z_raised"]*1000)} mm high on a 3,000 mm wheel track, a static lateral tipping angle of {f(R["stab"]["tip_deg"])}°. The 6.1 m width exceeds the 2.60 m general width limit on Brazilian roads, so road transport needs an Autorização Especial de Trânsito, or the planter must be moved on a trailer [18]. A folding toolbar (wings hinged at ±1.75 m) is the usual commercial solution and a natural next design step.')
fig(D+'fs_fig4_frame.png', W, 'Figure 5. Chassis weldment, plan view. Ballast bridge, PV posts and braces are listed in the text.')
H2('11.1 SolidWorks modelling procedure')
bullets([
 'New part. On the Top Plane draw a layout sketch of member centre-lines: hitch point (−3,200, 0); rail nodes (0, ±1,500); rail ends (1,350, ±1,500); toolbar line x = 0 from y = −3,050 to +3,050; brace line at x = −1,600 between the rails.',
 'Insert → Weldments → Structural Member. Toolbar: ANSI inch, rectangular tube 7 × 7 × 0.25 (add the profile if missing). Rails: 10 × 4 × 0.3125, rotated so the 254 mm side is vertical, offset down so the rail top touches the toolbar bottom (toolbar centre z = 616, rail centre z = 400). Brace: 4 × 4 × 0.25.',
 'Use Trim/Extend so the rails stop at the underside of the toolbar and continue rearward as separate members, welded with gussets. Add 12 mm gusset plates (Weldments → Gusset) at the four rail–toolbar junctions.',
 'Plates (Merge result off): hitch clevis plates 25 mm with a Ø33 hole; swing-arm pivot lugs 20 mm with a Ø40 hole; cylinder base lugs; 12 row-unit hanger plates 12 mm (Section 13 hole pattern for two 1/2" square U-bolts on a 7.5 in centre distance).',
 'Second layout sketch for the ballast bridge (posts at x = 1,150, y = ±1,500, beam at z = 700) and the PV frame (posts at x = −1,750 and −750 on the rails, rails at z = 1,580, braces at 30°).',
 'Fillet Bead 5 mm on rail and toolbar joints, 4 mm elsewhere; End Caps 3 mm on open tube ends. Cut List: check member lengths and that the total mass matches Table 1.',
 'Simulation: Beam study on the weldment with remote loads for each row unit (1,587 N at x = 589 mm × 2.5), supports at the hitch (pin) and wheel axles (roller). Then a Frequency study of the canopy with and without braces, which should reproduce ≈ 13 Hz vs > 100 Hz.'])

H1('12. Custom part 4: ground wheel ("drive wheel") assembly')
p('On a mechanical Brazilian planter the "roda motriz" drives the seed meters through chains. Here the meters are electric, so the planter wheel supports the frame, provides the speed reference (encoder) and lifts the machine. Traction comes from the tractor. The tyre and rim are commercial; the swing arm, spindle and hub are custom and were sized as follows.')
p(f'<b>Tyre.</b> BKT AS 504, 7.50-16, 8PR: 1,360 kg at 30 km/h and 1,215 kg at 40 km/h, OD 803 mm, section width 209 mm, mass 14 kg [12]. Width is the governing constraint: between the closing-wheel assemblies of rows 1.25 and 1.75 m there is about 280 mm, so the 209 mm tyre leaves ≈ 35 mm each side. A wider flotation tyre would not fit the lane. The transport load of {f(wh["Nw1_kg"])} kg uses {f(tr["util_30"]*100)}% of the 30 km/h rating. Rim: 16 × 5.50F (commercial; obtain the exact profile and bolt pattern from the supplier).')
p(f'<b>Swing arm.</b> Box 120 × 80 × 8 mm (S355), 450 mm between pivot and axle. Transport load with the 2.5 factor gives M = {f(wh["M_arm"]/1000,1)} kN·m, σ = {f(wh["sig_arm"])} MPa, safety factor {wh["n_arm"]:.1f}. <b>Lift cylinder:</b> it acts on the arm with an effective lever of 180 mm, so it must push {f(wh["F_cyl"]/1000,1)} kN statically. A 63.5 mm (2.5 in) bore cylinder gives {f(wh["F_cyl_cap"]/1000)} kN at an assumed 175 bar tractor pressure (the T4\'s relief pressure is not published in the sources found). Rotating the arm 40° raises the frame {f(wh["lift_mm"])} mm, lifting the opener discs from 50 mm deep to about 240 mm above the soil.')
p(f'<b>Spindle.</b> AISI 4140 quenched and tempered (S<sub>y</sub> ≈ 655 MPa, S<sub>u</sub> ≈ 1,020 MPa; typical values to confirm with the mill certificate), cantilevered 120 mm from the arm to the tyre centre-plane, with a root diameter of 70 mm stepping to tapered-roller-bearing seats of 55 mm and 45 mm. Worst case: 2.5 × the vertical load plus a lateral force of 0.5 × wheel load at the tyre radius, M = {f(wh["M_sp"]/1000,2)} kN·m, σ = {f(wh["sig_sp"])} MPa, static safety factor {wh["n_sp"]:.1f}. Fatigue (non-rotating spindle, fluctuating bending, K<sub>f</sub> = 1.7 at the shoulder, S<sub>e</sub> = {f(wh["Se"])} MPa after Marin factors) by modified Goodman: n<sub>f</sub> = {wh["nf_sp"]:.2f}. Hub bearings: a 55 mm bore inner and 45 mm bore outer tapered roller bearing; check L<sub>10</sub> against the chosen catalogue at {f(wh["Nw1"]/1000,1)} kN radial and {f(0.5*wh["Nw1"]/1000,1)} kN axial. The wheel turns {f(wh["rev_per_km"])} revolutions per km, so life is not critical. A 600 ppr encoder on the hub cap gives 6.3 mm of travel per pulse.')
fig(D+'fs_fig5_wheel.png', W, 'Figure 7. Ground wheel assembly: side view in work and transport, and half section through the hub.')
H2('12.1 SolidWorks modelling procedure')
bullets([
 '<b>Rim and tyre (reference parts):</b> revolve the 16 × 5.50F rim cross-section from the supplier drawing, then revolve a tyre envelope (OD 803, section width 209) as a separate part. Both are purchased; they are modelled only for mass and interference.',
 '<b>Hub:</b> revolve a profile with a Ø55 cup bore and a Ø45 cup bore, a grease cavity between them, and a flange matching the rim\'s bolt circle (Hole Wizard, studs per rim). Add an encoder mount on the hub cap.',
 '<b>Spindle:</b> revolve Ø70 × 40 root → Ø55 k6 × 25 → Ø50 × 50 → Ø45 k6 × 22 → M42 × 1.5 thread with a slotted castle nut. Material AISI 4140 QT. Add 2 mm fillets at each shoulder (they set K<sub>f</sub>).',
 '<b>Swing arm:</b> weldment from 120 × 80 × 8 rectangular tube, 450 mm between a Ø40 pivot tube and a Ø70 spindle boss, with a cylinder clevis 200 mm from the pivot.',
 '<b>Assembly:</b> Concentric mates for pivot and spindle; an Angle mate between arm and rail driven by a configuration ("Work" 0°, "Transport" 40°). Check tyre clearance to the neighbouring closing wheels in both configurations, and measure that the frame rises 289 mm.',
 'Simulation: static study on the spindle (fixed at the arm boss, remote load at the tyre contact: 30 kN vertical, 6 kN lateral), then a fatigue study using an S-N curve for 4140 with zero-based loading.'])

H1('13. What changes for other configurations')
bullets([
 '<b>Adding a fertilizer shank (no-till).</b> D497 lists no-till planters with fertilizer at several times the seeding-only draft per row [4], and Tatu specifies 100–115 cv for a 12-row seed-fertilizer machine [3]. That exceeds the T4. The options are the diesel-electric AgXeed 5.115T2 (115 kW, no cab) or a 130 hp battery tractor when the John Deere E-Power ships. The toolbar, rails and row-unit mounts would need re-checking at about three times the draft.',
 '<b>Faster planting (10–12 km/h).</b> This requires a vacuum meter and belt seed delivery, replacing the gravity plate the research specifies; the electric drive and PV architecture stay the same.',
 '<b>Larger planters (24+ rows).</b> These need a folding frame, central bulk hoppers and a tractor in the 300+ hp class. There, the 8R 410 eAutoPowr\'s 100 kW electrical output [10] could power electric row drives and fans directly.'])

H1('14. Bill of materials')
H2('14.1 Custom parts')
table([
 ['#', 'Part', 'Qty', 'Material / process', 'Key dimensions'],
 ['C1', 'Seed plate, 12 cells', '12 (+2)', 'POM-C, CNC', 'Ø140 × 10.5; cells 15.5 × 6.0; bore Ø12 H7'],
 ['C2', 'Meter housing, shroud, brush holder, ejector', '12', '6061-T6 or glass-filled PA, CNC/moulded', 'shroud Ø141.5; discharge port 20 × 12'],
 ['C3', 'Opener disc (L and R)', '24', '65Mn/1065, 40–45 HRC, laser cut + bevel', 'Ø381 × 5; 4 × Ø10.5 on Ø85'],
 ['C4', 'Disc hub housing + spindle', '24', 'AISI 1045 hub; 4140 QT spindle', 'bores Ø47 H7; spindle Ø25/Ø20'],
 ['C5', 'Row-unit shank weldment', '12', 'S355 10 mm laser-cut plate, GMAW', 'Section 10; toe ±5.5°'],
 ['C6', 'Parallel links, gauge arms, depth rocker + T-handle', '12 sets', 'S355 flat bar 60×10, 50×20; pins 4140', 'links 400; arms 180'],
 ['C7', 'Row-unit hanger plate', '12', 'S355 12 mm', '300 × 220; 4 × Ø14 for 1/2" U-bolts'],
 ['C8', 'Chassis weldment (toolbar, rails, brace, hitch, ballast bridge, PV frame)', '1', 'A500 Gr. B HSS, S355 plate, GMAW', 'Section 11'],
 ['C9', 'Swing arm', '2', 'S355 box 120×80×8', '450 pivot-to-axle'],
 ['C10', 'Wheel spindle + hub', '2', '4140 QT spindle; 1045 hub', 'Ø70 root; bearing seats Ø55/Ø45'],
 ['C11', 'Ballast plates', '12', 'S235, flame cut', '25 kg each (e.g. 400 × 200 × 40)'],
], [0.9*cm, 4.6*cm, 1.5*cm, 4.4*cm, W-11.4*cm])
H2('14.2 Commercial components')
table([
 ['Component', 'Qty', 'Specification'],
 ['Tractor: New Holland T4 Electric Power', '1', '55 kW rated, 110 kWh, 400 V, cab, drawbar, remotes [8]; DC fast charger'],
 ['Farm PV array + grid connection (net metering)', '1', f'≈ {f(st_["kWp_net"],1)} kWp per 1,000 ha/year (Section 7)'],
 ['Tyre BKT AS 504 7.50-16 8PR + rim 16 × 5.50F', '2', '1,360 kg at 30 km/h [12]'],
 ['Tapered roller bearings 55 mm and 45 mm bore', '2 + 2', 'with seals and castle nut'],
 ['Hydraulic cylinder 63.5 bore × 203 stroke, double acting', '2', '≥ 175 bar; with hoses, flow divider/rephasing valve'],
 ['Opener bearings 6204-2RS', '48', '20 × 47 × 14'],
 ['Gauge wheels 381 × 102 (15 × 4 in)', '24', 'semi-pneumatic, bearing hub'],
 ['V closing wheel assembly with spring', '12', 'Ø330 wheels, 180–380 N adjustable'],
 ['Downforce springs + adjuster', '24', '0–450 N each (0–900 N per row)'],
 ['Seed hopper 56 L with lid', '12', 'polyethylene'],
 ['Brushless gearmotor Oriental Motor BLV R (BLMR5100K-GFV-F + GFV5G20 + BLVD-KRD)', '12', '100 W, 24–48 VDC, 20:1, 5.65 N·m [13]'],
 ['PV module Canadian Solar CS6R-410MS', '2', '1,722 × 1,134, 410 W [14]'],
 ['MPPT Victron SmartSolar 100/30', '1', '100 V, 30 A, 880 W at 24 V [15]'],
 ['LiFePO₄ battery 25.6 V 100 Ah with BMS', '1', '≥ 100 A continuous'],
 ['Mobile controller (IP67, CAN) + display', '1', 'speed-proportional meter control, row shut-off'],
 ['Seed-tube optical sensors; wheel encoder 600 ppr; GNSS speed sensor', '12 / 1 / 1', '—'],
 ['Hitch jack, safety chain, lights, SMV sign', '1 set', 'road-legal set per local rules'],
], [6.3*cm, 1.6*cm, W-7.9*cm])
H2('14.3 Fasteners (McMaster-Carr; SOLIDWORKS models downloadable per part number)')
p('Part numbers marked "verified" were read from McMaster-Carr catalogue pages [19]. For socket head screws only the family (91290A, Class 12.9 black oxide) was verified, and for hex head screws only the requirement is given; select the length on McMaster to get the full number. For outdoor use, specify zinc-plated or zinc-flake versions.')
table([
 ['Joint', 'Fastener', 'Qty', 'McMaster part number'],
 ['Row-unit hanger to toolbar', 'Square U-bolt 1/2"-13, 7" inside width, 8-5/8" high, zinc (nuts and washers included)', '24', '3060T198 (verified)'],
 ['Opener disc to hub', 'Socket head screw M10 × 25, Class 12.9 + locknut M10 DIN 985', '96', '91290A family / 94645A220 (verified)'],
 ['Disc spindle nut', 'Locknut M20 × 1.5 (fine) or castle nut + split pin', '24', 'select on McMaster'],
 ['Gauge wheel axle', 'Hex head screw M16 × 120, Class 8.8 + locknut M16 + 2 washers', '24', 'select / 94645A250 (verified)'],
 ['Link pins', 'Ø20 pins with M12 end bolts + locknut M12 + washers', '48', '94645A230 / 91455A150 (verified)'],
 ['Meter housing / motor', 'Socket head screw M5 × 16 + locknut M5; M4 × 12 plate screws + locknut M4', '96 / 36', '91290A family / 94645A102, 94645A101 (verified)'],
 ['Hopper bracket, sensors', 'Socket head screw M6 × 20 + locknut M6 + washer M6', '96', '91290A family / 94645A205 / 91455A120 (verified)'],
 ['Swing-arm pivot', 'Ø40 pin with M16 end bolt + locknut M16', '2', '94645A250 (verified)'],
 ['Cylinder clevis pins', 'Ø25 pins with M12 end bolts + locknut M12 + washers', '4', '94645A230 / 91455A150 (verified)'],
 ['Rim to hub', 'Wheel studs and nuts per rim (typically M18 × 1.5)', '12', 'supplied with hub/rim'],
 ['PV modules to frame', 'Hex head screw M8 × 20 + locknut M8 + 2 washers', '8', 'select / 94645A210 / 91455A130 (verified)'],
 ['PV posts, ballast bridge posts', 'Hex head screw M12 × 90, Class 8.8 + locknut M12 + washers', '16', 'select / 94645A230 / 91455A150 (verified)'],
 ['Ballast plates', 'Hex head screw M16 × 260 fully threaded + locknut M16 + washers', '4', 'select / 94645A250 (verified)'],
 ['Hitch clevis pin', 'Ø32 hitch pin with retaining clip', '1', 'commercial hitch pin'],
], [3.6*cm, 6.8*cm, 1.4*cm, W-11.8*cm])
bt = R['bolts']
table([['Size', 'Stress area (mm²)', 'Preload (kN), Class 8.8', 'Torque (N·m), K = 0.2']] +
      [[k, f'{v["As"]}', f'{v["Fi"]/1000:.1f}', f'{v["T"]:.0f}'] for k, v in bt.items()],
      [2.0*cm, 3.4*cm, 4.6*cm, W-10.0*cm])
p('Table 5. Tightening torques for Class 8.8 (T = K·F<sub>i</sub>·d, F<sub>i</sub> = 0.75 × proof load; proof strength 580 MPa up to M16 and 600 MPa for M20–M24). For the U-bolts, use the manufacturer\'s torque, since their steel grade is not stated.', cap)

H1('15. Assumptions to verify in SolidWorks Simulation and field data')
table([
 ['Assumption', 'Value', 'How to verify'],
 ['Draft (seed only, tilled)', 'D497 260 + 13S N/row, +15%', 'drawbar load cell on the tractor; compare with D497'],
 ['Opener side force per disc', '0.5 × vertical share (313 N)', 'SOLIDWORKS Simulation or a DEM model of the furrow; field strain gauge'],
 ['Tractor axle split, tyres, soil cone index', '40/60; 280/70R20 + 420/70R28; 600 kPa', 'dealer data; penetrometer at the site'],
 ['Driveline/motor efficiencies, auxiliaries', '0.90 × 0.92; 3 kW', 'T4 telematics logs during planting'],
 ['Usable battery fraction', '90% of 110 kWh', 'New Holland specification'],
 ['Meter electrical power per row', '12 W average', 'bench measurement of the BLV drive at 37 rpm, 1 N·m'],
 ['PV module mass; tractor drawbar vertical rating; hydraulic pressure', '21.3 kg; not published; 175 bar', 'manufacturer datasheets'],
 ['Seed size, thousand-seed mass, emergence', 'L ≤ 14, W ≤ 10, T 4–6 mm; 350 g; 90%', 'lot measurements and germination test'],
], [5.0*cm, 4.6*cm, W-9.6*cm])
p('The model should be validated in the order the risk sits: (1) the row-unit and rail interference over full row-unit travel; (2) a Simulation Beam study of the frame for the transport case; (3) a motion study of the parallel linkage with springs to confirm the downforce table; (4) frequency studies of the canopy and toolbar. The calculation scripts reproduce every number in this report, so any assumption can be replaced with a measured value and the design rerun.')

H1('References')
refs = [
 '[1] Vicentini, I. F. L.; Vidal, J. M.; Savi, N. C. Desenvolvimento de um modelo de semeadora movida a energia solar para a otimização do plantio de milho no Sudeste brasileiro. Brazilian International School, 2023.',
 '[2] Aegro. Plantadeira de milho: os 5 melhores modelos e 7 dicas para acertar na escolha (Baldan, Jumil, John Deere DB74, Tatu specifications; mechanical 4–6 km/h vs vacuum 10–12 km/h).',
 '[3] Tatu Marchesan. PST4 Flex / Suprema technical leaflet, rev. 08, 10/2021 (7–12 rows; 15" × 15" offset double discs; 7.00 × 16 tyres; 100–115 cv for 12 rows).',
 '[4] ASABE D497.4 (2003), Agricultural Machinery Management Data: Table 1 draft parameters for row-crop planters (drawn, seeding only: A = 260, B = 13, ±15%); field efficiency 50–75%; traction equations (Brixius). Planter coefficients derive from Harrigan, T. M.; Rotz, C. A. Applied Engineering in Agriculture 11(6), 773–783, 1995.',
 '[5] PAMI. Evaluation Report 357: John Deere 7000 Max-Emerge planter (opener vertical force 800–1,250 N; closing wheels 180–380 N; 15 in discs and gauge wheels).',
 '[6] NSW DPI. Primefact: Estimating tractor power needs (10–15% power reserve).',
 '[7] University of Arizona Cooperative Extension. Agricultural Machinery Management (drawbar/PTO ratios; MFWD on tilled soil 0.73).',
 '[8] New Holland T4 Electric Power: Equipment World (74 hp rated, 65 hp PTO, 110 kWh, 400 V, ~4 h typical, ~1 h fast charge, exportable 110/220 V, solar charging); AllMachines (≈ 4,900 kg, 83.9 in wheelbase, Cat I & II hitch, 84.8 L/min); Ritchie Bros. buyer\'s guide (10–80% in about 1 h DC; electric tractors rarely exceed 100–130 hp).',
 '[9] Farmers Weekly. Agritechnica 2025: John Deere goes electric with 130hp EPower (prototype; up to 5 × 39 kWh; US production 2027).',
 '[10] profi. Electric CVT option for John Deere 8R (eAutoPowr; up to 100 kW external electrical power, 480 V AC; 8R 410).',
 '[11] AgXeed. AgBot 5.115T2 specifications (115 kW Deutz diesel, electric drive train, optional 100 kW 700 V electrical output, 7.8 t).',
 '[12] BKT AS 504 7.50-16 8PR listing, Big Tyre (1,360 kg at 30 km/h; 1,215 kg at 40 km/h; OD 803 mm; width 209 mm).',
 '[13] Oriental Motor. BLV Series R Type 100 W, BLMR5100K-GFV-F with GFV5G20 and BLVD-KRD (24–48 VDC; 0.05–200 rpm; 50 lb-in).',
 '[14] Canadian Solar CS6R-410MS listing, Solarproof (1,722 × 1,134 mm; Vmp 31.2 V; Voc 37.2 V; NOCT 41 °C).',
 '[15] Victron SmartSolar MPPT 100/30 listing, Solar Cellz USA (100 V; 30 A; 880 W at 24 V).',
 '[16] Pereira, E. B. et al. Atlas Brasileiro de Energia Solar, 2nd ed., INPE, 2017; regional means as reported by Revista Pesquisa FAPESP.',
 '[17] Lei nº 14.300/2022 (marco legal da micro e minigeração distribuída), summary by Demarest Advogados (microgeneration ≤ 75 kW; credits valid up to 60 months).',
 '[18] CTB Digital, commentary on Art. 101 of the Código de Trânsito Brasileiro (CONTRAN Res. 210/2006 limit of 2.60 m width; AET for larger vehicles).',
 '[19] McMaster-Carr online catalogue: square U-bolts (3060T), DIN 985 nylon-insert locknuts (94645A), ISO 7089 washers (91455A), socket head screws ISO 898-1 (91290A).',
 '[20] Budynas, R. G.; Nisbett, J. K. Shigley\'s Mechanical Engineering Design. McGraw-Hill (fatigue, Marin factors, shaft design).',
 '[21] Turkish Journal of Agriculture and Forestry 36(2), 2012 (0.34 m/s plate rim speed and 16 seeds/s limits); Ciência Rural (UFSM), peripheral speed of the plate in seed meters of corn and soybean.',
 '[22] Kachman, S. D.; Smith, J. A. Transactions of the ASAE 38(2), 379–387, 1995 (spacing quality indices).',
 '[23] Solar-assisted seeder proof-of-concept report (companion document) for the derivation of the seed-plate geometry.',
 '[24] International Journal of Agricultural and Biological Engineering, maize seed dimension distributions; Lincoln Ag Products plate-sizing guide.',
]
for r_ in refs: p(r_, ParagraphStyle('ref', parent=bodyL, fontSize=11, leading=15))

def onpage(c, doc):
    c.saveState(); c.setFont('LSans', 9); c.setFillColor(MUT)
    c.drawString(2.5*cm, 1.4*cm, 'Full-size solar-electric maize planter: engineering viability and detailed design')
    c.drawRightString(A4[0]-2.5*cm, 1.4*cm, f'Page {doc.page}'); c.restoreState()
doc = BaseDocTemplate(D+'Full_Size_Solar_Planter_Report.pdf', pagesize=A4, leftMargin=2.5*cm, rightMargin=2.5*cm,
                      topMargin=2.3*cm, bottomMargin=2.3*cm, initialFontName='LSans', initialFontSize=12,
                      title='Full-Size Solar-Electric Maize Planter: Engineering Viability and Detailed Design',
                      author='Engineering analysis of Vicentini, Vidal & Savi (2023)')
doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f')], onPage=onpage)])
doc.build(story)
print('built')
