# seeder-code

Solar seeder: calculation and report code

All the code used to produce the two engineering reports. Every number in the reports comes from these scripts.

Fileså







File



What it does





calc.py



Proof-of-concept (walk-behind, single row): agronomy, seed-meter kinematics, soil forces, Brixius traction, statics and ballast, drive train, PV/battery energy, structural and fatigue checks, vibration. Writes results.json.





figs.py



Draws the proof-of-concept figures (general arrangement, seed plate, opener, frame, drive wheel, energy chart) from results.json.





report.py



Builds Solar_Seeder_Engineering_Report.pdf from results.json and the figures.





calc_fs.py



Full-size 12-row planter + battery-electric tractor: ASABE D497 draft, downforce budget, whole-planter equilibrium, ballast search, toolbar/rail/arm/spindle stresses, opener and bearings, canopy vibration and wind, tractor traction and energy, charging-station sizing, planter PV. Writes results_fs.json.





figs_fs.py



Draws the full-size figures from results_fs.json (it also reuses fig2_plate.png from figs.py).





report_fs.py



Builds Full_Size_Solar_Planter_Report.pdf.





geometry_check.py



Clearance checks in 3D coordinates for the full-size planter: tyre swept zone when raising, cylinder geometry and lever, canopy braces and frequencies, gauge-arm geometry, disc gap, row-unit float. Found the clash in the report's wheel layout and verifies the revised one.





lift_check.py



Transport-lift geometry: shows the frame pivots about the hitch (discs rose only 208 mm), sizes the 750 mm swing arm and searches the cylinder base/lug positions for standard cylinder lengths.





design_review.py



Systematic pass/fail review of the modelling guide (frame, solar frame, ballast, row unit, gauge wheels, wheel/lift). Prints every check with its margin and the fix.





calc_fs_report_v1.py



The full-size calculation exactly as used for the first full-size PDF (kept for reference). calc_fs.py now has the revised wheel module: pivot at R 1,400, 750 mm arm (150 x 100 x 10), 76.2 mm cylinder, lift sized so disc bottoms clear the ground by 200 mm, new canopy braces.





results.json, results_fs.json



Calculation outputs, as used in the reports.



How to run

Requires Python 3 with matplotlib, reportlab and Pillow, plus the Liberation Sans font (metric-compatible with Arial). On Windows/Mac, change the font paths at the top of figs*.py and report*.py to Arial.

python calc.py      && python figs.py    && python report.py
python calc_fs.py   && python figs_fs.py && python report_fs.py

The scripts write to /home/claude/seeder/; change the output paths (search for that string) to a folder on your machine.

Changing assumptions

Every input is a named variable near the top of each calc section, for example CI (soil cone index), V_o_hi (opener vertical force), TSW (thousand-seed mass), eta_dl / eta_mi (tractor efficiencies), P_meter_row, H_ghi (irradiation). Edit one and rerun the three scripts; the ballast, stresses, energy figures and report text all update.

What is not included

No finite-element or multibody simulations were run. The "simulation" steps in the reports describe what to set up in SOLIDWORKS Simulation to check the hand calculations, which are all done analytically in these scripts.
