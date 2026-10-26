"""Full-size 12-row solar-electric maize planter + battery-electric tractor: design calculations.
Coordinates: x rearward from toolbar centre-line, y lateral from machine centre, z up from ground. SI units."""
import math, json
g = 9.81
R = {}

# ------------------------------------------------------------------ 1 agronomy & kinematics
N_ROWS, ROW = 12, 0.50
rows_y = [s*(0.25 + 0.5*k) for k in range(6) for s in (1, -1)]
pop, emerg = 80000, 0.90
seeds_m = pop*ROW/10000/emerg
v_nom, v_max = 6/3.6, 7/3.6
W_work = N_ROWS*ROW
FE = 0.65
TSW, bulk = 0.350, 0.72
hop_L = 56.0
seed_kg_ha = pop/emerg*TSW/1000
R['agro'] = dict(seeds_m=seeds_m, X_mm=1000/seeds_m, seed_kg_ha=seed_kg_ha, W=W_work,
                 C_th=W_work*v_nom*3.6/10, C_eff=W_work*v_nom*3.6/10*FE,
                 hop_kg=hop_L*bulk, ha_per_fill=N_ROWS*hop_L*bulk/seed_kg_ha)
D_pl, NC = 0.140, 12
def meter(v):
    f = v*seeds_m; n = f/NC*60; w = n*2*math.pi/60
    return dict(seeds_s=f, rpm=n, omega=w, v_rim=w*D_pl/2, Fr=w**2*(D_pl/2-0.003)/g,
                t_fill=(120/360)/(n/60))
R['meter_nom'], R['meter_max'] = meter(v_nom), meter(v_max)
h_drop = 0.38
t_fall = math.sqrt(2*h_drop/g)
R['drop'] = dict(t=t_fall, err_nom=0.15*t_fall*v_nom*1000, err_max=0.15*t_fall*v_max*1000,
                 v_seed_vert=math.sqrt(2*g*h_drop))
# meter motor (Oriental Motor BLV R, 100 W, 20:1 -> 50 lb-in = 5.65 N.m rated, 0.05-200 rpm)
T_meter_req = 1.0
R['meter_motor'] = dict(T_rated=50*0.113, margin=50*0.113/T_meter_req,
                        P_mech_nom=T_meter_req*R['meter_nom']['omega'])

# ------------------------------------------------------------------ 2 soil-tool forces
def d497(S, A=260.0, B=13.0, F=1.0): return F*(A + B*S)   # N/row, drawn seeding only (ASABE D497.4)
D_row_nom = d497(6.0); D_row_up = 1.15*D_row_nom; D_row_7 = 1.15*d497(7.0)
DLF = 2.5
D_struct = DLF*D_row_up          # structural design draft per row
V_o_lo, V_o_hi = 800.0, 1250.0   # PAMI 357: seed disc opener vertical force 180-280 lb
Pc_lo, Pc_hi = 180.0, 380.0      # closing wheel applied force 40-85 lb
G_min = 250.0                    # assumed minimum gauge-wheel load (two wheels)
R['soil'] = dict(D_row_nom=D_row_nom, D_row_up=D_row_up, D_row_7=D_row_7,
                 D_tot_nom=N_ROWS*D_row_nom, D_tot_up=N_ROWS*D_row_up, D_struct=D_struct)

# ------------------------------------------------------------------ 3 masses (kg) and positions
rho = 7850
def hss_rect(H, B, t): return (H*B - (H-2*t)*(B-2*t))*1e-6*rho   # kg/m
m_tb = hss_rect(177.8, 177.8, 6.35)      # 7x7x1/4
m_rail = hss_rect(254.0, 101.6, 7.94)    # 10x4x5/16
m_44 = hss_rect(101.6, 101.6, 6.35)      # 4x4x1/4
m_22 = hss_rect(50.8, 50.8, 4.76)        # 2x2x3/16
L_tb = 6.10
x_h, z_h = -3.20, 0.50
y_rail = 1.50
L_rail_f = math.hypot(3.20, y_rail)
L_rail_r = 1.35
x_piv, z_piv = 1.30, 0.40
L_arm = 0.45
x_w = x_piv + L_arm; z_w = 0.4015
r_tyre = 0.4015
disc_t = 0.005
m_disc = math.pi/4*0.381**2*disc_t*rho
ru_items = {  # row unit, empty: name: (kg, x, z)
 'shank weldment': (32.0, 0.52, 0.42), 'parallel links + pins (4)': (14.0, 0.30, 0.61),
 'mount bracket + U-bolts': (9.0, 0.10, 0.61), 'downforce springs + rods': (4.0, 0.30, 0.66),
 'opener discs (2)': (2*m_disc, 0.55, 0.14), 'disc hubs + spindles (2)': (4.0, 0.55, 0.14),
 'gauge wheels 381x102 (2)': (12.0, 0.59, 0.19), 'gauge arms + depth handle': (5.0, 0.62, 0.28),
 'closing wheel assembly': (16.0, 1.15, 0.20), 'seed meter (housing, plate)': (3.0, 0.62, 0.40),
 'meter BLDC motor + gearhead + driver': (4.5, 0.62, 0.48), 'seed hopper 56 L (empty)': (8.0, 0.65, 0.80),
 'seed tube + sensor': (1.0, 0.58, 0.20)}
m_ru = sum(v[0] for v in ru_items.values())
x_ru = sum(v[0]*v[1] for v in ru_items.values())/m_ru
z_ru = sum(v[0]*v[2] for v in ru_items.values())/m_ru
m_seed_full = hop_L*bulk
x_seed, z_seed = 0.65, 0.82
frame_items = [  # name, kg, x, z
 ('Toolbar 7x7x1/4 HSS, 6.10 m', m_tb*L_tb, 0.0, 0.616),
 ('Main rails 10x4x5/16 HSS, front A-frame legs', 2*m_rail*L_rail_f, -1.60, 0.40),
 ('Main rails, rear legs', 2*m_rail*L_rail_r, 0.675, 0.40),
 ('Cross brace 4x4x1/4 at x = -1.60', m_44*1.50, -1.60, 0.40),
 ('Hitch clevis + jack', 40.0, -3.10, 0.50),
 ('Row-unit hanger plates (12)', 12*6.0, 0.12, 0.616),
 ('Swing arms + pivots (2)', 2*24.0, 1.52, 0.40),
 ('Lift cylinders 63.5x203 + brackets (2)', 2*22.0, 1.20, 0.62),
 ('Wheels: tyre 7.50-16 + rim + hub (2)', 2*(14.0+16.0+12.0), x_w, z_w),
 ('PV modules 2 x 410 W (assumed 21.3 kg each)', 2*21.3, -1.25, 1.62),
 ('PV frame: posts, rails, braces', 4*1.10*m_22 + 2*3.44*m_22 + 4*1.0*m_22 + 6.0, -1.25, 1.20),
 ('Battery 25.6 V 100 Ah + MPPT + ECU box', 40.0, -1.60, 0.60),
 ('Hydraulic hoses, wiring, lights', 30.0, -0.80, 0.55),
]
m_frame0 = sum(i[1] for i in frame_items)

def statics(fill, S, V_o, P_c, ballast=0.0, x_b=1.10, D_row=D_row_up, raised=False):
    """Whole planter. Returns hitch vertical V_h, wheel total N_w, gauge load per row."""
    items = [(m*g, x) for _, m, x, _ in frame_items] + [(ballast*g, x_b)]
    W_ru = (m_ru + fill*m_seed_full)*g
    x_rug = (m_ru*x_ru + fill*m_seed_full*x_seed)/(m_ru + fill*m_seed_full)
    items += [(W_ru, x_rug)]*N_ROWS
    W_tot = sum(w for w, _ in items)
    # moments about wheel contact (x_w, 0); positive = x*Fz - z*Fx
    M = sum((x - x_w)*(-w) for w, x in items)
    Fz_ground = 0.0
    if not raised:
        G = W_ru + S - V_o - P_c
        for xg, F in ((0.55, V_o), (0.59, G), (1.15, P_c)):
            M += N_ROWS*(xg - x_w)*F
            Fz_ground += N_ROWS*F
        H = N_ROWS*D_row
        M += -(z_h - 0)*(-H)   # hitch pull forward (Fx = -H) at z_h
    else:
        G = None; H = 0.0
    V_h = -M/(x_h - x_w)
    N_w = W_tot - Fz_ground - V_h
    return dict(V_h=V_h, N_w=N_w, G=G, W_tot=W_tot, W_ru=W_ru, H=H)

# required spring force per row and wheel-load check
cases = []
for fill in (1.0, 0.25):
    for V_o, P_c, lab in ((V_o_hi, Pc_hi, 'firm'), (V_o_lo, Pc_lo, 'loose')):
        W_ru = (m_ru + fill*m_seed_full)*g
        S_req = max(0.0, V_o + P_c + G_min - W_ru)
        cases.append(dict(fill=fill, soil=lab, V_o=V_o, P_c=P_c, W_ru=W_ru, S_req=S_req))
S_max = max(c['S_req'] for c in cases)
S_set = math.ceil(S_max/150)*150            # spring setting step 150 N
N_min_total = 2*1500.0                     # keep >= 1.5 kN on each ground wheel
st0 = statics(0.25, S_set, V_o_hi, Pc_hi)
ballast = 0.0
if st0['N_w'] < N_min_total or st0['V_h'] < 1000:
    # ballast placed at x_b on rails: find minimum mass (25 kg steps)
    while True:
        ballast += 25
        st0 = statics(0.25, S_set, V_o_hi, Pc_hi, ballast)
        if st0['N_w'] >= N_min_total and st0['V_h'] >= 1000: break
for c in cases:
    st = statics(c['fill'], S_set if c['S_req'] > 0 else 0.0, c['V_o'], c['P_c'], ballast)
    c.update(S_used=S_set if c['S_req'] > 0 else 0.0, G=st['G'], V_h=st['V_h'], N_w=st['N_w'])
tr = statics(1.0, 0, 0, 0, ballast, raised=True)
m_total = tr['W_tot']/g
x_cg = None
R['mass'] = dict(m_tb_per_m=m_tb, m_rail_per_m=m_rail, m_disc=m_disc, m_ru=m_ru, x_ru=x_ru, z_ru=z_ru,
                 m_seed=m_seed_full, m_frame=m_frame0, ballast=ballast, m_total_full=m_total,
                 m_total_empty=m_total - N_ROWS*m_seed_full)
R['downforce'] = dict(S_max=S_max, S_set=S_set, cases=cases)
R['transport'] = dict(V_h=tr['V_h'], N_w=tr['N_w'], N_wheel_kg=tr['N_w']/2/g, V_h_kg=tr['V_h']/g,
                      tyre_cap_30=1360, tyre_cap_40=1215,
                      util_30=tr['N_w']/2/g/1360)
R['ru_items'] = ru_items
R['frame_items'] = frame_items

# CG (transport, full)
items = [(m, x, z) for _, m, x, z in frame_items] + [(ballast, 1.10, 0.45)]
items += [(m_ru, x_ru, z_ru)]*N_ROWS + [(m_seed_full, x_seed, z_seed)]*N_ROWS
mt = sum(i[0] for i in items)
xc = sum(i[0]*i[1] for i in items)/mt; zc = sum(i[0]*i[2] for i in items)/mt
R['cg'] = dict(x=xc, z_work=zc, z_raised=zc + 0.289)
R['stab'] = dict(tip_deg=math.degrees(math.atan(y_rail/(zc + 0.289))))

# ------------------------------------------------------------------ 4 structure
E = 200e9; Fy_hss = 317.0  # ASTM A500 Gr.B square/rect (46 ksi)
def props_rect(H, B, t):
    I_x = (B*H**3 - (B-2*t)*(H-2*t)**3)/12          # bending about horizontal axis (H vertical)
    I_y = (H*B**3 - (H-2*t)*(B-2*t)**3)/12
    Am = (H-t)*(B-t)
    return I_x, I_x/(H/2), I_y, I_y/(B/2), Am
I_tb, S_tb, _, _, Am_tb = props_rect(177.8, 177.8, 6.35)
I_r, S_r, Iy_r, Sy_r, Am_r = props_rect(254.0, 101.6, 7.94)
# toolbar, transport raised, full hoppers: beam on supports at rail nodes +/-1.5
W_full = (m_ru + m_seed_full)*g
e_ru = (m_ru*x_ru + m_seed_full*x_seed)/(m_ru + m_seed_full)
w_tb = m_tb*g + 6.0*g/0.5     # self weight + hanger plates per metre
out_rows = [y for y in rows_y if y > y_rail]
M_sup = sum(W_full*(y - y_rail) for y in out_rows) + w_tb*(L_tb/2 - y_rail)**2/2
T_node = len(out_rows)*W_full*e_ru
sig_tb = DLF*M_sup*1e3/S_tb
tau_tb = DLF*T_node*1e3/(2*Am_tb*6.35)
vm_tb = math.sqrt(sig_tb**2 + 3*tau_tb**2)
# work: horizontal bending from draft + torsion from draft couple
M_h_work = sum(D_struct*(y - y_rail) for y in out_rows)
T_work = len(out_rows)*D_struct*0.616
sig_h = M_h_work*1e3/S_tb; tau_w = T_work*1e3/(2*Am_tb*6.35)
R['toolbar'] = dict(I=I_tb, S=S_tb, Am=Am_tb, W_full=W_full, e=e_ru, M_sup=M_sup, T_node=T_node,
                    sigma=sig_tb, tau=tau_tb, vm=vm_tb, n=Fy_hss/vm_tb,
                    M_h_work=M_h_work, T_work=T_work, sig_h=sig_h, tau_w=tau_w,
                    vm_work=math.sqrt(sig_h**2+3*tau_w**2))
# toolbar deflection at tip (overhang, cantilever approx, static)
P_tip_eq = sum(W_full*(y - y_rail) for y in out_rows)/(L_tb/2 - y_rail)
R['toolbar']['tip_defl_mm'] = P_tip_eq*(L_tb/2 - y_rail)**3/(3*E*I_tb*1e-12)*1000
# rails: side view beam hitch -> wheel (one rail = half of everything except hitch which is shared)
half = 0.5
loads_rail = [(N_ROWS*W_full*half, e_ru), ((m_tb*L_tb + 72)*g*half, 0.06)]
for name, m, x, z in frame_items:
    if 'Toolbar' in name or 'hanger' in name or 'Wheels' in name: continue
    loads_rail.append((m*g*half, x))
loads_rail.append((ballast*g*half, 1.10))
Wr = sum(f for f, _ in loads_rail)
V_h_r = sum(f*(x_w - x) for f, x in loads_rail)/(x_w - x_h)
N_r = Wr - V_h_r
def M_rail(xs):
    M = V_h_r*(xs - x_h)
    for f, x in loads_rail:
        if x < xs: M -= f*(xs - x)
    return M
xs = [x_h + i*0.005 for i in range(int((x_w - x_h)/0.005)+1)]
Ms = [M_rail(x) for x in xs]
M_r_max = max(abs(m) for m in Ms); x_r_max = xs[[abs(m) for m in Ms].index(M_r_max)]
sig_r = DLF*M_r_max*1e3/S_r
# rail deflection at toolbar node (simply supported, static) by numerical double integration
EIr = E*I_r*1e-12
import itertools
dx = 0.005
th = [0.0]; w = [0.0]
for i in range(1, len(xs)):
    th.append(th[-1] + Ms[i]/EIr*dx); w.append(w[-1] + th[-1]*dx)
corr = [w[i] - w[-1]*(xs[i]-xs[0])/(xs[-1]-xs[0]) for i in range(len(xs))]
R['rail'] = dict(I=I_r, S=S_r, M_max=M_r_max, x_at=x_r_max, sigma=sig_r, n=Fy_hss/sig_r,
                 V_h_r=V_h_r, N_r=N_r, defl_mm=max(abs(c) for c in corr)*1000,
                 A_frame_angle=math.degrees(math.atan(y_rail/3.2)),
                 M_node=M_rail(0.0))
# rail lateral clearance to gauge wheels of neighbouring rows
R['rail']['clear_gauge_mm'] = (y_rail - 101.6e-3/2 - (1.25 + 0.165))*1000

# swing arm, spindle, cylinder (transport, per wheel)
Nw1 = tr['N_w']/2
M_arm = DLF*Nw1*L_arm
I_arm = (80*120**3 - 64*104**3)/12; S_arm = I_arm/60
sig_arm = M_arm*1e3/S_arm
Fy_s355 = 355.0
# cylinder: attaches to arm 0.20 m from pivot, effective lever 0.18 m
lever_c = 0.18
F_cyl = Nw1*L_arm/lever_c
bore = 0.0635; p_hyd = 17.5e6
F_cyl_cap = math.pi/4*bore**2*p_hyd
# spindle: overhang 0.12 m from arm face to wheel centre plane; lateral 0.5N at tyre radius
d_sp = 0.070
M_sp = DLF*Nw1*0.12 + 0.5*Nw1*r_tyre
sig_sp = 32*M_sp/(math.pi*d_sp**3)/1e6
Sy_4140, Su_4140 = 655.0, 1020.0
# spindle fatigue (non-rotating, fluctuating): mean from N, alt 0.5N; Kf 1.7 shoulder
Sm = 32*(Nw1*0.12)/(math.pi*d_sp**3)/1e6; Sa = 32*(0.5*Nw1*0.12 + 0.25*Nw1*r_tyre)/(math.pi*d_sp**3)/1e6
ka = 4.51*Su_4140**-0.265; kb = 1.24*(d_sp*1000)**-0.107 if d_sp*1000 <= 51 else 1.51*(d_sp*1000)**-0.157
Se = 0.5*Su_4140*ka*kb*0.814
nf_sp = 1/(1.7*Sa/Se + Sm/Su_4140)
# hub bearings: tapered 32010? use 30208 (C ~ 63 kN) inboard + 30206 outboard (C ~ 44 kN) catalogue-typical
L10_km = None
R['wheel'] = dict(Nw1=Nw1, Nw1_kg=Nw1/g, M_arm=M_arm, S_arm=S_arm, sig_arm=sig_arm, n_arm=Fy_s355/sig_arm,
                  F_cyl=F_cyl, F_cyl_cap=F_cyl_cap, M_sp=M_sp, sig_sp=sig_sp, n_sp=Sy_4140/sig_sp,
                  Se=Se, nf_sp=nf_sp, lift_mm=L_arm*math.sin(math.radians(40))*1000,
                  rev_per_km=1000/(2*math.pi*r_tyre))

# row-unit components
# disc plate bending under lateral load
F_side_disc = 0.5*V_o_hi/2
r_c, r_fl = 0.170, 0.060
M_disc = DLF*F_side_disc*(r_c - r_fl)
b_eff = 2*math.pi*r_fl/6
sig_disc = 6*M_disc/(b_eff*disc_t**2)/1e6
# hub bearings 2 x 6204-2RS per disc, spacing 25 mm, C = 13.5 kN (SKF catalogue)
P_disc = math.hypot(V_o_hi/2, D_row_up/2)
M_bear = F_side_disc*r_c
R_b = M_bear/0.025 + P_disc/2
L10_rev = (13.5e3/R_b)**3*1e6
rev_km_disc = 1000/(math.pi*0.381)
d_spd = 0.025
M_spd = DLF*(P_disc*0.030 + M_bear)
sig_spd = 32*M_spd/(math.pi*d_spd**3)/1e6
# double-disc geometry
toe = math.radians(5.5); Rd = 0.1905
x_conv = Rd*math.cos(math.radians(45))
gap_bottom = 2*x_conv*math.tan(toe)
gap_rear_axle = 2*(x_conv + 0.0)*math.tan(toe)
# gauge arm
G_max = max(c['G'] for c in cases)
M_garm = DLF*G_max/2*0.18
sig_garm = 6*M_garm/(0.020*0.050**2)/1e6
# parallel links
z_link_mid, spacing = 0.61, 0.18
F_link = D_struct*z_link_mid/spacing + D_struct/2
Pcr_link = math.pi**2*E*(60*10**3/12)*1e-12/0.40**2
# U-bolts: moment on mount (raised, full, DLF)
M_mount = DLF*W_full*e_ru
F_leg = M_mount/0.190/2
As_half = 91.5; F_proof_g2 = 379*As_half
R['ru'] = dict(F_side_disc=F_side_disc, M_disc=M_disc, sig_disc=sig_disc, n_disc=1100/sig_disc,
               R_b=R_b, L10_Mrev=L10_rev/1e6, L10_km=L10_rev/rev_km_disc, M_spd=M_spd, sig_spd=sig_spd,
               n_spd=Sy_4140/sig_spd, gap_bottom_mm=gap_bottom*1000, x_conv_mm=x_conv*1000,
               G_max=G_max, sig_garm=sig_garm, F_link=F_link, Pcr_link=Pcr_link,
               M_mount=M_mount, F_leg=F_leg, F_proof_leg=F_proof_g2, depth_range=(25, 75))
for d in (0.025, 0.05, 0.075):
    th = math.degrees(math.acos((Rd - d)/Rd))
    R.setdefault('disc_geom', []).append((d*1000, 2*th, 2*math.sqrt(Rd**2-(Rd-d)**2)*1000))

# PV canopy vibration and wind
m_can = 2*21.3 + 2*3.44*m_22 + 6.0
I22 = (50.8**4 - 41.28**4)/12
L_post = 1.05
k_un = 4*3*E*I22*1e-12/L_post**3
f_un = math.sqrt(k_un/m_can)/(2*math.pi)
A22 = (50.8**2 - 41.28**2)*1e-6
Lb = math.hypot(0.6, L_post); c = 0.6/Lb
k_br = 4*E*A22/Lb*c**2/2
f_br = math.sqrt((k_un + k_br)/m_can)/(2*math.pi)
lug_pitch_tr = 0.20
f_lug = lambda v: v/lug_pitch_tr
V_rel = 30/3.6 + 15.0
q = 0.5*1.2*V_rel**2
A_pv = 2*1.722*1.134
F_wind = 1.3*q*A_pv
M_post = F_wind/4*L_post
sig_post = M_post*1e3/(I22/(50.8/2))
R['canopy'] = dict(m=m_can, f_un=f_un, f_br=f_br, f_lug_6=f_lug(v_nom), f_lug_7=f_lug(v_max),
                   f_lug_30=f_lug(30/3.6), q=q, F_wind=F_wind, sig_post_unbraced=sig_post)

# ------------------------------------------------------------------ 5 tractor: New Holland T4 Electric Power
m_tr = 4900.0; W_tr = m_tr*g
wb = 2.131                     # 83.9 in wheelbase
fr_split = 0.40                # assumed static front share
CI = 600e3
tyres = {'front': (0.28, 0.957), 'rear': (0.42, 1.30)}   # assumed 280/70R20, 420/70R28
def bn(W, b, d, dh=0.2): return (CI*b*d/W)*(1+5*dh)/(1+3*b/d)
def axle_loads(H, V_h, grade):
    Wf = W_tr*math.cos(grade)*fr_split - H*z_h/wb - W_tr*math.sin(grade)*0.9/wb
    Wr = W_tr*math.cos(grade) - Wf + V_h + V_h*0.55/wb
    Wf -= V_h*0.55/wb
    return Wf, Wr
def tractor(H, V_h, v, grade=0.0):
    Wf, Wr = axle_loads(H, V_h, grade)
    NT_req = H + W_tr*math.sin(grade)
    def nt(s):
        tot_nt = tot_gt = 0.0
        for W, (b, d) in ((Wf/2, tyres['front']), (Wr/2, tyres['rear'])):
            B = bn(W, b, d)
            gt = 0.88*(1-math.exp(-0.1*B))*(1-math.exp(-7.5*s)) + 0.04
            rho_ = 1/B + 0.04 + 0.5*s/math.sqrt(B)
            tot_nt += 2*W*(gt - rho_); tot_gt += 2*W*gt
        return tot_nt, tot_gt
    lo, hi = 0.0, 0.5
    for _ in range(60):
        mid = (lo+hi)/2
        if nt(mid)[0] < NT_req: lo = mid
        else: hi = mid
    s = (lo+hi)/2; NTv, GTv = nt(s)
    P_axle = GTv*v/(1-s)
    TE = (1-s)*NTv/GTv if GTv > 0 else 0
    return dict(Wf=Wf, Wr=Wr, s=s, NT=NTv, GT=GTv, P_axle=P_axle, TE=TE, P_draw=H*v)
eta_dl, eta_mi, P_aux = 0.90, 0.92, 3000.0
tr_cases = {}
for lab, D, gr in (('flat_nominal', N_ROWS*D_row_nom, 0.0), ('flat_upper', N_ROWS*D_row_up, 0.0),
                   ('slope3_upper', N_ROWS*D_row_up + m_total*g*0.03, 0.03)):
    st = statics(0.6, S_set, V_o_hi if 'upper' in lab else V_o_lo, Pc_hi, ballast, D_row=D/N_ROWS)
    t = tractor(D, st['V_h'], v_nom, gr)
    t['P_batt'] = t['P_axle']/(eta_dl*eta_mi) + P_aux
    t['V_h'] = st['V_h']
    tr_cases[lab] = t
R['tractor'] = tr_cases
# energy per charge
E_use = 110*0.90
P_work = tr_cases['flat_nominal']['P_batt']
k_t = FE + (1-FE)*0.4
P_axle_nom = tr_cases['flat_nominal']['P_axle']
P_avg = P_axle_nom*k_t/(eta_dl*eta_mi) + P_aux
C_eff = R['agro']['C_eff']
t_run = E_use*1000/P_avg
R['energy'] = dict(E_use=E_use, P_work=P_work, P_avg=P_avg, t_run=t_run, ha_charge=t_run*C_eff,
                   kWh_ha=P_avg/1000/C_eff, ha_day_2charges=2*t_run*C_eff,
                   P_work_up=tr_cases['flat_upper']['P_batt'], P_work_slope=tr_cases['slope3_upper']['P_batt'])
# solar charging station
H_ghi, PR = 5.0, 0.78
yield_kWh_kWp_day = H_ghi*PR
E_day = 2*E_use/0.95
kWp_direct = E_day/yield_kWh_kWp_day
eff_mod = 410/(1.722*1.134*1000)
ha_year = 1000.0
E_year = ha_year*R['energy']['kWh_ha']/0.95
kWp_net = E_year/(yield_kWh_kWp_day*365)
R['station'] = dict(yield_day=yield_kWh_kWp_day, E_day=E_day, kWp_direct=kWp_direct,
                    area_direct=kWp_direct/eff_mod, eff_mod=eff_mod, E_year=E_year, kWp_net=kWp_net,
                    area_net=kWp_net/eff_mod)

# ------------------------------------------------------------------ 6 planter electrical system (on-board PV)
P_meter_row = 12.0
P_loads = N_ROWS*P_meter_row + 40 + N_ROWS*1.0 + 20
P_stc, NOCT, gam = 820.0, 41.0, -0.0034
Tc = 30 + (NOCT-20)/800*1000
P_pv_hot = P_stc*(1 + gam*(Tc-25))
fT = 1 + gam*((25 + (NOCT-20)/800*600) - 25)
E_pv_day = P_stc/1000*H_ghi*fT*0.96*0.95*0.98*1000
E_bat_pl = 25.6*100*0.80
R['planter_el'] = dict(P_loads=P_loads, Tc=Tc, P_pv_hot=P_pv_hot, fT=fT, E_pv_day=E_pv_day,
                       E_need_10h=P_loads*10, E_bat=E_bat_pl, hrs_bat=E_bat_pl/P_loads,
                       Voc_cold=2*37.2*(1+0.0026*20), Vmp=2*31.2, I_charge=P_pv_hot*0.96/27.0,
                       solar_frac=min(1, P_pv_hot*0.96/P_loads), heat_rej=1000*A_pv - P_pv_hot)
R['meter_motor']['P_el_row'] = P_meter_row

# energy cascade (nominal, per working hour average) for chart
casc = [('Charger AC input (per hour of field time)', P_avg/0.95/1000),
        ('Tractor battery output', P_avg/1000),
        ('Traction motor + inverter output', P_axle_nom*k_t/eta_dl/1000),
        ('At wheel axles', P_axle_nom*k_t/1000),
        ('Drawbar pull on planter', tr_cases['flat_nominal']['P_draw']*FE/1000),
        ('Seed meters (from planter PV)', N_ROWS*R['meter_motor']['P_mech_nom']*FE/1000)]
R['cascade'] = casc

# bolts
As = {'M8': 36.6, 'M10': 58.0, 'M12': 84.3, 'M16': 157.0, 'M20': 245.0, 'M24': 353.0}
dia = {'M8': 8, 'M10': 10, 'M12': 12, 'M16': 16, 'M20': 20, 'M24': 24}
R['bolts'] = {k: dict(As=v, Fi=0.75*v*600 if k in ('M20', 'M24') else 0.75*v*580,
                      T=0.2*(0.75*v*(600 if k in ('M20','M24') else 580))*dia[k]/1000) for k, v in As.items()}
json.dump(R, open('/home/claude/seeder/results_fs.json', 'w'), indent=1, default=str)

def show(d, ind=''):
    for k, v in d.items():
        if k in ('ru_items', 'frame_items', 'cases'): continue
        if isinstance(v, dict): print(ind+k); show(v, ind+'  ')
        elif isinstance(v, float): print(f'{ind}{k}: {v:.4g}')
        else: print(f'{ind}{k}: {v}')
show(R)
for c in R['downforce']['cases']: print({k: (round(v, 1) if isinstance(v, float) else v) for k, v in c.items()})
for n, m, x, z in frame_items: print(f'{n}: {m:.1f} kg x={x} z={z}')
