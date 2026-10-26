"""Design calculations for the solar-assisted single-row maize precision seeder (proof of concept).
All units SI unless noted (mm used for geometry inputs, converted where needed)."""
import math, json

g = 9.81
R = {}  # results

# ---------------------------------------------------------------- 1. Agronomy -> machine
row = 0.50            # m, inter-row spacing (research, Fig.1 / Cruz et al. 2007)
pop = 80000           # plants/ha (research target ~80,000)
emerg = 0.90          # assumed field emergence (adjust to seed-lot germination test)
plants_per_m = pop * row / 10000
seeds_per_m = plants_per_m / emerg
Xs = 1 / seeds_per_m          # m, in-row seed spacing
seeds_per_ha = pop / emerg
R['agro'] = dict(plants_per_m=plants_per_m, seeds_per_m=seeds_per_m, X_seed_mm=Xs*1000,
                 plant_spacing_mm=1000/plants_per_m, seeds_per_ha=seeds_per_ha)
TSW = 0.350           # kg per 1000 seeds (assumed, typical commercial hybrid range 0.30-0.38)
bulk = 0.72           # kg/L assumed bulk density of seed maize
R['agro']['seed_kg_ha'] = seeds_per_ha * TSW / 1000
hopper_L = 3.0
R['agro']['hopper_kg'] = hopper_L * bulk
R['agro']['ha_per_fill'] = hopper_L * bulk / R['agro']['seed_kg_ha']

v_nom, v_max = 0.5, 1.0       # m/s ground speed
ncell = 12
D_plate = 0.140               # m seed plate OD
def meter(v):
    f = v * seeds_per_m       # seeds/s
    n = f / ncell * 60        # rpm
    w = n * 2 * math.pi / 60
    vp = w * D_plate / 2
    Fr = w**2 * (D_plate/2 - 0.003) / g   # centripetal/gravity at cell centre
    return dict(seed_rate=f, rpm=n, omega=w, v_periph=vp, Froude=Fr)
R['meter_nom'] = meter(v_nom); R['meter_max'] = meter(v_max)
R['meter_geom'] = dict(cell_pitch_mm=math.pi*D_plate*1000/ncell)

# seed drop
h_drop = 0.30
t_fall = math.sqrt(2*h_drop/g)
R['drop'] = dict(t_fall=t_fall, v_impact=math.sqrt(2*g*h_drop),
                 spacing_err_mm_nom=0.15*t_fall*v_nom*1000,
                 spacing_err_mm_max=0.15*t_fall*v_max*1000)

# ---------------------------------------------------------------- 2. Soil-tool forces
D_o = 131.0      # N, draft upper bound (single-disc opener, S&TR 194, 2019: 92-131 N)
V_o_max = 373.0  # N, vertical upper bound (321-373 N)
V_o_min = 321.0
G_min = 30.0     # N, minimum gauge-wheel load at worst case
R_row = V_o_max + G_min      # N, row-unit vertical reaction to be supplied by machine weight
F_side = 150.0   # N, assumed side force at 5 deg gang angle (conservative)

# ---------------------------------------------------------------- 3. Traction (Brixius 1987 / ASABE D497)
CI = 600e3       # Pa, assumed tilled seedbed cone index (450-900 kPa range)
def brixius(W, b, d, s, defl_ratio=0.0):
    Bn = (CI*b*d/W) * (1+5*defl_ratio)/(1+3*b/d)
    GT = 0.88*(1-math.exp(-0.1*Bn))*(1-math.exp(-7.5*s)) + 0.04
    MR = 1/Bn + 0.04 + 0.5*s/math.sqrt(Bn)
    return Bn, GT, MR, GT-MR
def mr_towed(W, b, d):
    Bn = (CI*b*d/W)/(1+3*b/d)
    return 1/Bn + 0.04

r_roll = 0.200   # m drive wheel rolling radius (rim R190, lug tip R210)
b_w, d_w = 0.100, 0.420
s_des = 0.15
P_press = 60.0   # N press-wheel spring force
m_press_assy = 4.5  # kg press/caster assembly (rests on its own wheel)
G_nom = R_row - V_o_min       # gauge load when soil force is at the low end
mr_g = mr_towed(max(G_nom,1), 0.05, 0.20)
mr_p = mr_towed(P_press + m_press_assy*g, 0.06, 0.25)
grade = 0.03
acc = 0.2

# ---------------------------------------------------------------- 4. Masses & positions (x rearward of drive axle, y above ground), mm
rho_s = 7850
def tube_sq(B, t): return (B**2-(B-2*t)**2)*1e-6*rho_s   # kg/m
def tube_rd(D, t): return math.pi/4*(D**2-(D-2*t)**2)*1e-6*rho_s
m40 = tube_sq(40, 2); m25 = tube_sq(25, 2); m25r = tube_rd(25.4, 2)
# drive wheel mass
rim = math.pi*0.377*0.100*0.003*rho_s
web = (math.pi/4*0.374**2 - 4*math.pi/4*0.080**2 - math.pi/4*0.050**2)*0.004*rho_s
hub = math.pi/4*(0.050**2-0.025**2)*0.060*rho_s
lugs = 16*0.100*0.020*0.005*rho_s
m_wheel = rim+web+hub+lugs
R['wheel_mass'] = dict(rim=rim, web=web, hub=hub, lugs=lugs, total=m_wheel)
m_shaft = math.pi/4*0.025**2*0.245*rho_s
items = [  # name, mass kg, x mm, y mm
 ('Drive wheels (2, custom steel)', 2*m_wheel, 0, 200),
 ('Stub shafts, 4 flange bearings, sprockets, chains', 2*(m_shaft+2*0.8+0.9+0.35+0.1), 0, 200),
 ('Gearmotors MY1016Z3 (2, assumed 3.0 kg each)', 6.0, 0, 230),
 ('Battery LiFePO4 25.6 V 20 Ah (assumed 6 kg)', 6.0, -225, 320),
 ('Electronics (MPPT, driver, Arduino, wiring)', 1.5, -60, 300),
 ('Main frame rails + cross-members 40x40x2', (2*1.15+5*0.22)*m40, 275, 200),
 ('Axle plates 4 x 6 mm', 4*0.16*0.14*0.006*rho_s, 0, 200),
 ('Row-unit brackets', 1.0, 490, 170),
 ('Canopy posts 4 x 25x25x2', 4*0.78*m25, 300, 610),
 ('Canopy braces 4 x 25x25x2', 4*0.877*m25, 300, 610),
 ('Canopy rails + cross-bars', (2*1.156+3*0.865)*m25, 328, 1000),
 ('PV modules 2 x 100 W (5.9 kg each)', 11.8, 328, 1030),
 ('Handlebar + lift lever', 2.65*m25r + 0.8, 1080, 600),
 ('Opener disc 250x4', math.pi/4*0.25**2*0.004*rho_s, 470, 85),
 ('Disc hub (housing, 2x6203, spindle)', 1.2, 470, 85),
 ('Row-unit shank plate 8 mm', 4.1, 490, 150),
 ('Gauge wheel + slider', 2.3, 510, 100),
 ('Seed meter (housing, plate, stepper)', 1.8, 520, 330),
 ('Hopper 3 L + seed', 0.6 + hopper_L*bulk, 520, 500),
]
W0 = sum(m for _,m,_,_ in items)*g
x0 = sum(m*x for _,m,x,_ in items)*g/W0
y0 = sum(m*y for _,m,_,y in items)*g/W0
x_row, x_p = 485.0, 880.0

# iterate for ballast
NTR_design_cap = 0.35
Wtot_guess = W0 + 200
for _ in range(30):
    F_req = D_o + mr_g*max(G_nom,1) + mr_p*(P_press+m_press_assy*g) + grade*Wtot_guess + acc*Wtot_guess/g
    # drive-wheel load needed
    Nd = 500.0
    for _ in range(50):
        Bn, GT, MR, NTR = brixius(Nd/2, b_w, d_w, s_des)
        NTR_d = min(NTR_design_cap, 0.65*NTR)
        Nd_new = 1.10*F_req/NTR_d   # 10% traction reserve
        if abs(Nd_new-Nd) < 0.01: break
        Nd = Nd_new
    Wf = Nd + R_row + P_press
    Wtot_guess = Wf + m_press_assy*g
mb = (Wf - W0)/g
mb_plates = math.ceil(mb/5.0)*5.0      # 5 kg plates
Wf = W0 + mb_plates*g
xb = (R_row*x_row + P_press*x_p - W0*x0)/(mb_plates*g)
Nd = Wf - R_row - P_press
Wtot = Wf + m_press_assy*g
xcg = (W0*x0 + mb_plates*g*xb)/Wf
y_b = 300
ycg = (W0*y0 + mb_plates*g*y_b)/Wf
Bn, GT, MR, NTR = brixius(Nd/2, b_w, d_w, s_des)
NTR_d = min(NTR_design_cap, 0.65*NTR)
F_req = D_o + mr_g*max(G_nom,1) + mr_p*(P_press+m_press_assy*g) + grade*Wtot + acc*Wtot/g
F_avail = NTR_d*Nd
R['statics'] = dict(W0=W0, m0=W0/g, x0=x0, y0=y0, mb_req=mb, mb=mb_plates, xb=xb, Wf=Wf, Wtot=Wtot,
                    mtot=Wtot/g, Nd=Nd, Nd_per_wheel=Nd/2, R_row=R_row, P_press=P_press,
                    xcg=xcg, ycg=ycg, G_at_Vmin=R_row-V_o_min, G_at_Vmax=R_row-V_o_max,
                    Bn=Bn, GT=GT, MR=MR, NTR_brixius=NTR, NTR_design=NTR_d,
                    F_req=F_req, F_avail=F_avail, traction_margin=F_avail/F_req,
                    mr_gauge=mr_g, mr_press=mr_p, steady_req=F_req-acc*Wtot/g)
R['items'] = [(n, m, x, y) for n,m,x,y in items] + [('Ballast steel plates', mb_plates, round(xb), y_b)]

# Mohr-Coulomb upper bound per drive wheel
c_soil, phi = 3000.0, math.radians(28)   # assumed tilled soil
z_sink = 0.020
Rt = 0.210
l_c = 2*math.sqrt(2*Rt*z_sink - z_sink**2)
A_c = b_w*l_c
H_max = A_c*c_soil + (Nd/2)*math.tan(phi)
R['mohr'] = dict(l_contact=l_c, A=A_c, H_max_wheel=H_max,
                 H_req_wheel=(F_req + MR*Nd)/2, util=((F_req + MR*Nd)/2)/H_max)
lug_pitch = 2*math.pi*Rt/16
R['mohr']['lug_pitch'] = lug_pitch; R['mohr']['lugs_engaged'] = l_c/lug_pitch

# headland pivot: why the rear wheel must swivel
N_press_raised = Wf*xcg/x_p + m_press_assy*g
scrub_moment = 0.6*N_press_raised*(x_p/1000)
diff_force_needed = scrub_moment/0.5
R['turn'] = dict(N_press_raised=N_press_raised, scrub_moment=scrub_moment,
                 diff_force_each=diff_force_needed, traction_each=0.6*Nd/2)

# ---------------------------------------------------------------- 5. Powertrain
F_gross = F_req + MR*Nd          # total gross thrust
F_gross_ss = R['statics']['steady_req'] + MR*Nd
T_wheel_op = F_gross_ss/2*r_roll  # per wheel steady
T_wheel_pk = F_gross/2*r_roll
i_ch = 48/9
eta_ch = 0.95
p_ch = 12.7
r9 = p_ch/(2*math.sin(math.pi/9))/1000
r48 = p_ch/(2*math.sin(math.pi/48))/1000
T_rated_out = 110*0.0981      # N.m (110 kgf.cm, retailer listing)
T_stall_out = 350*0.0981
n_rated = 300.0
I0, Irated = 2.2, 19.0
kT = T_rated_out/(Irated-I0)     # N.m/A output-referred
def motor_op(v, Tw):
    n_w = v/((1-s_des)*r_roll)*60/(2*math.pi)
    n_m = n_w*i_ch
    Tm = Tw/(i_ch*eta_ch)
    I = I0 + Tm/kT
    P_axle = Tw*n_w*2*math.pi/60
    return dict(n_wheel=n_w, n_motor_out=n_m, T_motor_out=Tm, I_motor=I, P_axle=P_axle)
R['motor_nom'] = motor_op(v_nom, T_wheel_op)
R['motor_max'] = motor_op(v_max, T_wheel_op)
R['motor_pk']  = motor_op(v_max, T_wheel_pk)
T_wheel_stall = T_stall_out*i_ch*eta_ch
R['drive'] = dict(i=i_ch, r9=r9, r48=r48, PD48=2*r48*1000, PD9=2*r9*1000, T_wheel_op=T_wheel_op,
                  T_wheel_pk=T_wheel_pk, T_wheel_rated=T_rated_out*i_ch*eta_ch,
                  T_wheel_stall=T_wheel_stall,
                  F_wheel_rated=T_rated_out*i_ch*eta_ch/r_roll,
                  n_wheel_rated=n_rated/i_ch, v_at_rated=n_rated/i_ch*2*math.pi/60*r_roll*(1-s_des),
                  chain_pull_op=T_wheel_op/r48, chain_pull_stall=T_wheel_stall/r48)
# chain length
C = 0.130
L_links = 2*C/(p_ch/1000) + (9+48)/2 + (p_ch/1000)*(48-9)**2/(4*math.pi**2*C)
Lp = math.ceil(L_links/2)*2
# actual centre distance (Shigley eq.)
Ap = -Lp + (9+48)/2
Cact = (p_ch/4)*(-Ap + math.sqrt(Ap**2 - 8*((48-9)/(2*math.pi))**2))
R['drive'].update(L_links_calc=L_links, links=Lp, C_actual_mm=Cact)

# electrical power
eta_mg = 0.60; eta_ctrl = 0.97
P_meter, P_elec = 12.0, 6.0
def P_el(v, Tw):
    mo = motor_op(v, Tw)
    return 2*mo['P_axle']/(eta_ch*eta_mg*eta_ctrl) + P_meter + P_elec
R['power'] = dict(P_el_nom=P_el(v_nom, T_wheel_op), P_el_max=P_el(v_max, T_wheel_op),
                  P_axle_nom=2*motor_op(v_nom,T_wheel_op)['P_axle'],
                  P_draw_nom=D_o*v_nom, P_draw_max=D_o*v_max)
# tractive efficiency
TE = (NTR_d/(NTR_d+MR))*(1-s_des)
R['power']['TE'] = TE

# ---------------------------------------------------------------- 6. Solar / thermodynamics
P_stc, A_pv = 200.0, 2*0.865*0.578
NOCT, gam = 47.0, -0.0032
def pv(G, Ta):
    Tc = Ta + (NOCT-20)/800*G
    return Tc, P_stc*G/1000*(1+gam*(Tc-25))
Tc1, P1 = pv(1000, 30); Tc2, P2 = pv(800, 28)
H = 5.0  # kWh/m2/day GHI, Southeast annual mean (INPE Atlas 2017)
eta_stc = P_stc/(A_pv*1000)
fT = 1+gam*((25 + (NOCT-20)/800*600) - 25)
eta_mppt, f_soil, f_wire = 0.96, 0.95, 0.98
E_pv = H*A_pv*eta_stc*fT*eta_mppt*f_soil*f_wire*1000  # Wh/day
E_bat = 25.6*20*0.80
hrs_nom = E_pv/R['power']['P_el_nom']
FE = 0.65
cap_th = v_nom*row*3600/10000
R['solar'] = dict(A_pv=A_pv, eta_stc=eta_stc, Tc_1000=Tc1, P_1000=P1, Tc_800=Tc2, P_800=P2,
                  heat_rejected_1000=1000*A_pv - P1, fT_day=fT, E_pv=E_pv, E_bat=E_bat,
                  hrs_solar=hrs_nom, hrs_bat=E_bat/R['power']['P_el_nom'],
                  solar_fraction_peak=P1*eta_mppt/R['power']['P_el_nom'],
                  cap_th_ha_h=cap_th, cap_eff_ha_h=cap_th*FE, ha_day_solar=cap_th*FE*hrs_nom,
                  E_per_ha_Wh=R['power']['P_el_nom']/(cap_th*FE),
                  Voc_cold=2*22.79*(1+0.0026*(25-5)), Vmp=2*19.97)
# energy cascade (sun -> furrow) at nominal speed, 1000 W/m2
casc = []
P = 1000*A_pv; casc.append(('Solar irradiance on modules', P))
P = P1; casc.append(('PV DC output (63.8 °C cell)', P))
P *= eta_mppt; casc.append(('After MPPT', P))
P *= 0.95; casc.append(('After battery round trip (assumed 95%)', P))
P *= eta_ctrl; casc.append(('After motor controller', P))
P *= eta_mg*eta_ch; casc.append(('At wheel axles (motor+gear+chain)', P))
P *= TE; casc.append(('As drawbar pull (traction eff.)', P))
R['cascade'] = casc
R['cascade_overall'] = P/(1000*A_pv)

# ---------------------------------------------------------------- 7. Structural checks
E = 200e9
def sq_props(B, t):
    I = (B**4-(B-2*t)**4)/12; return I, I/(B/2)
I40, S40 = sq_props(40, 2)   # mm4, mm3
I25, S25 = sq_props(25, 2)
Fy_tube = 235.0  # MPa conservative
DLF = 2.5
# frame beam: loads on frame (weights down, R_row & P up) - moment about each x section, from rear end
loads = [(m*g, x) for _,m,x,_ in items] + [(mb_plates*g, xb)]
def moment_at(xs, case='work'):
    M = 0.0
    for W, x in loads:
        if x > xs: M += -W*(x-xs)/1000   # downward loads behind section: hogging negative
    if case == 'work':
        if x_row > xs: M += R_row*(x_row-xs)/1000
    Pp = P_press if case=='work' else N_press_raised - m_press_assy*g
    if x_p > xs: M += Pp*(x_p-xs)/1000
    Nax = Nd if case=='work' else Wf - Pp
    if 0 > xs: M += Nax*(0-xs)/1000
    return M
xs_list = [i*5 for i in range(-60, 171)]
Mw = [abs(moment_at(x,'work')) for x in xs_list]
Mt = [abs(moment_at(x,'turn')) for x in xs_list]
Mmax = max(max(Mw), max(Mt))
x_at = xs_list[(Mw+Mt).index(Mmax) % len(xs_list)]
sig_frame = DLF*Mmax*1e3/(2*S40)
R['frame'] = dict(I40=I40, S40=S40, I25=I25, S25=S25, m40=m40, m25=m25, Mmax=Mmax, x_Mmax=x_at,
                  sigma=sig_frame, n=Fy_tube/sig_frame, Mw=max(Mw), Mt=max(Mt))
# deflection estimate: cantilever rear part from axle, conservative uniform approx using Mmax
# canopy vibration
m_can = 11.8 + (2*1.156+3*0.865)*m25
k_unbr = 4*3*E*I25*1e-12/(0.78**3)
f_unbr = math.sqrt(k_unbr/m_can)/(2*math.pi)
Lb = math.sqrt(0.4**2+0.78**2); cth = 0.4/Lb
A25 = (25**2-21**2)*1e-6
k_br = 2*E*A25/Lb*cth**2
f_br = math.sqrt((k_br+k_unbr)/m_can)/(2*math.pi)
def lug_freq(v): return v/((1-s_des)*r_roll)/(2*math.pi)*16
R['vib'] = dict(m_can=m_can, k_unbr=k_unbr, f_unbr=f_unbr, f_br=f_br,
                f_lug_nom=lug_freq(v_nom), f_lug_max=lug_freq(v_max),
                v_resonance=f_unbr*2*math.pi*(1-s_des)*r_roll/16)
Pcr = math.pi**2*E*I25*1e-12/((2*0.78)**2)
R['frame']['Pcr_post'] = Pcr

# stub shaft (25 mm, AISI 1045 CD: Su 630, Sy 530 MPa - Shigley Table A-20)
d = 0.025; Su, Sy = 630.0, 530.0
a_oh, b_span, c_sp = 0.079, 0.082, 0.029
Nw = Nd/2
F_lat = 0.5*Nw
M_static = DLF*Nw*a_oh + F_lat*r_roll
T_stall = T_wheel_stall
sb = 32*M_static/(math.pi*d**3)/1e6
ts = 16*T_stall/(math.pi*d**3)/1e6
svm = math.sqrt(sb**2+3*ts**2)
ka = 4.51*Su**-0.265; kb = 1.24*(d*1000)**-0.107; ke = 0.814
Se = 0.5*Su*ka*kb*ke
Kf, Kfs = 2.14, 3.0
Ma = 1.5*Nw*a_oh; Tm = T_wheel_op
nf = 1/((16/(math.pi*d**3))/1e6*((1/Se)*math.sqrt(4*(Kf*Ma)**2) + (1/Su)*math.sqrt(3*(Kfs*Tm)**2)))
R['shaft'] = dict(M_static=M_static, T_stall=T_stall, sigma_b=sb, tau=ts, svm=svm, n_static=Sy/svm,
                  ka=ka, kb=kb, Se=Se, Ma=Ma, Tm=Tm, n_fatigue=nf)
# key 8x7, L=45
bk, hk, Lk = 0.008, 0.007, 0.045
tau_k = 2*T_stall/(d*Lk*bk)/1e6
sig_k = 4*T_stall/(d*Lk*hk)/1e6
R['key'] = dict(tau=tau_k, crush=sig_k)
# bearings: reactions
F_ch = T_wheel_op/r48
R_out = Nw*(a_oh+b_span)/b_span
R_in_v = Nw*a_oh/b_span
R_in_h = F_ch*(c_sp+b_span)/b_span
R_out_h = F_ch*c_sp/b_span
R_in = math.hypot(R_in_v, R_in_h); R_out_t = math.hypot(R_out, R_out_h)
C_UC205 = 14000.0
n_w_nom = R['motor_nom']['n_wheel']
L10h = (C_UC205/max(R_in,R_out_t))**3*1e6/(60*n_w_nom)
R['bearing'] = dict(F_chain=F_ch, R_in=R_in, R_out=R_out_t, L10h=L10h)
# opener disc bearing 6203 C=9.95 kN
P_disc = math.hypot(V_o_max, D_o)
M_side = F_side*0.115
R_pair = M_side/0.024 + P_disc/2
R['disc_bearing'] = dict(P=P_disc, R_max=R_pair, L10_Mrev=(9950/R_pair)**3)
# opener disc plate bending (side force)
Mclamp = DLF*F_side*(0.115-0.050)
b_eff = 2*math.pi*0.050/6
sig_disc = 6*Mclamp/(b_eff*0.004**2)/1e6
R['disc'] = dict(M=Mclamp, sigma=sig_disc)
# shank plate out-of-plane
M_sh = DLF*F_side*0.220
sig_sh = 6*M_sh/(0.200*0.008**2)/1e6
R['shank'] = dict(M=M_sh, sigma=sig_sh, n=235/sig_sh)
# disc geometry at depth
for dd in (0.03, 0.04, 0.05):
    th = math.degrees(math.acos((0.125-dd)/0.125))
    R.setdefault('disc_geom', []).append((dd*1000, th, 2*math.sqrt(0.125**2-(0.125-dd)**2)*1000))
# wheel welds / lugs
Fl = DLF*(F_gross/2)/2
sig_lug = (Fl*0.010)/(0.100*0.005**2/6)/1e6
tau_hubweld = T_stall/(0.025*(2*math.pi*0.050*0.7071*0.004))/1e6
tau_web = T_stall/(2*math.pi*0.025**2*0.004)/1e6
R['wheel'] = dict(F_lug=Fl, sigma_lug=sig_lug, tau_hubweld=tau_hubweld, tau_web=tau_web)
# bolts torque table (K=0.2, preload 75% proof)
As = {'M4':8.78,'M5':14.2,'M6':20.1,'M8':36.6,'M10':58.0,'M12':84.3}
dia = {'M4':4,'M5':5,'M6':6,'M8':8,'M10':10,'M12':12}
R['bolts'] = {k: dict(As=v, Fi_88=0.75*v*580, T_88=0.2*0.75*v*580*dia[k]/1000,
                      Fi_129=0.75*v*970, T_129=0.2*0.75*v*970*dia[k]/1000) for k,v in As.items()}
# row-unit mount bolts: 4 x M10 8.8 - worst tension from moment
M_mount = DLF*(D_o*0.22 + R_row*0.0)
F_bolt = M_mount/(2*0.150) + DLF*R_row/4
R['mountbolt'] = dict(M=M_mount, F=F_bolt, Fi=R['bolts']['M10']['Fi_88'])
# thermal expansion of POM plate vs Al housing
R['thermal_plate'] = dict(dD_diam_mm=(110e-6-23e-6)*30*140)
# stability
line_d = (220000 - 250*xcg)/math.hypot(880,250)
R['stab'] = dict(d_tip=line_d, tip_angle=math.degrees(math.atan(line_d/ycg)),
                 tip_angle_axle=math.degrees(math.atan(250/ycg)))
# meter torque
T_meter = 4*(0.3*0.3*g*0.07 + 2*0.07 + 0.05)
R['meter_drive'] = dict(T_design=T_meter, steps_per_disc_rev=200*8*5.18,
                        steps_per_m=200*8*5.18*seeds_per_m/ncell,
                        steps_s_max=200*8*5.18*seeds_per_m/ncell*v_max,
                        enc_res_mm=math.pi*200/600)

json.dump(R, open('/home/claude/seeder/results.json','w'), indent=1, default=str)
def show(d, ind=''):
    for k,v in d.items():
        if isinstance(v, dict): print(ind+k); show(v, ind+'  ')
        elif isinstance(v, float): print(f'{ind}{k}: {v:.4g}')
        else: print(f'{ind}{k}: {v}')
show({k:v for k,v in R.items() if k not in ('items','cascade')})
for c in R['cascade']: print(f'{c[0]}: {c[1]:.1f} W')
for it in R['items']: print(f'{it[0]}: {it[1]:.2f} kg @ x={it[2]}, y={it[3]}')

# realistic average energy case: flat ground, mid-range draft (111 N), nominal speed
D_mid = 0.5*(92.2+131.3)
F_flat = D_mid + mr_g*max(G_nom,1) + mr_p*(P_press+m_press_assy*g)
Tw_flat = (F_flat + MR*Nd)/2*r_roll
Pel_flat = P_el(v_nom, Tw_flat)
R['energy_avg'] = dict(D_mid=D_mid, F_net=F_flat, T_wheel=Tw_flat, P_el=Pel_flat,
                       I_motor=motor_op(v_nom, Tw_flat)['I_motor'],
                       hrs_solar=E_pv/Pel_flat, ha_day=cap_th*FE*E_pv/Pel_flat,
                       Wh_per_ha=Pel_flat/(cap_th*FE), solar_frac_peak=P1*eta_mppt/Pel_flat,
                       hrs_with_full_bat=(E_pv+E_bat)/Pel_flat)
json.dump(R, open('/home/claude/seeder/results.json','w'), indent=1, default=str)
print(R['energy_avg'])
