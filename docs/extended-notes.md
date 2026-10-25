# TEG characterization: extended notes and code guide

*Markdown copy of the "Extended notes and code guide" tab of the [online lab manual](https://claude.ai/artifact/HGz8wXLUC6EcZ9fcEQRxs8) (Oct 23, 2026). The block diagram from the online version is not reproduced here. For the short RVCE-format manual, see [lab-manual.md](lab-manual.md).*

## Why this experiment is more than a basic one

It fits in one lab slot and reuses the thermocouple apparatus (Arduino, ADS1115, DS18B20, LCD), adding one Rs 150-300 module. It covers Unit III directly. It is clearly different from the thermocouple experiment: that one measures the microvolt EMF of a metal junction, while this one measures power delivered by a semiconductor generator. It also meets CO4, because a circuit model is built from one set of measurements and checked against another.

The plain version (plot V_oc vs ΔT, sweep resistors, find the peak) would be borderline basic. What lifts it is that **three independent quantities (S, R_int, P_max) come out of two measurement sets and cross-check each other**. The model is then predicted with zero fitted parameters and compared with the data.

| Upgrade | What it adds | Extra cost |
| --- | --- | --- |
| Cooling-curve sweep for Part A | V_oc is logged every second while the bath cools, giving 500+ points instead of 5 manual steps | None |
| R_int from the V-I line | V = E − I·R_int gives R_int and E by linear fit, checked against the matched-load peak | Analysis only |
| Zero-parameter model | P(R) predicted from S (Part A) and R_int (V-I line) before any curve fitting, then compared with a free fit | Analysis only |
| Efficiency vs limits | η = P/Q_h compared with the Carnot limit and the ideal TEG limit from the figure of merit Z | Analysis only (optional 3rd DS18B20, about Rs 100, for calorimetry) |
| P_max ∝ ΔT² check | Matched-load power at 3-4 values of ΔT; the log-log slope should be 2 | 20 min |
| Load effect on ΔT | Compare ΔT open vs loaded: current carries Peltier heat and lowers ΔT | None |

Three corrections to the original plan:

- **Do not read R_int with the multimeter's ohm range.** The meter's test current drives a Peltier ΔT and the module's own EMF adds to the reading, so it drifts. Use the V-I line.
- **Zero the multimeter leads** (short them, note the reading, subtract) before measuring the 1-4.7 Ω loads. A 0.3 Ω lead error is 14% of a 2.2 Ω resistor.
- **Measure V differentially (A0−A1) right at the load's terminals**, so breadboard contact resistance shows up as part of R_int and not as a voltage error. Check the module's polarity with a multimeter before connecting it to the ADS1115, because a negative input below −0.3 V can damage it.

Time in the lab is about 2 hours per group: 15 min calibration, 30 min Part A, 45 min Part B, 20 min Part C. The analysis script then produces all graphs and numbers in under a minute.

## Aim

To characterise a bismuth telluride Peltier module (TEC1-12706) used as a thermoelectric generator (TEG), and to validate its circuit model against measurement.

Problem statement: can heat from hot water power a small load, and what is the most power this module can deliver?

Objectives:

1. Determine the module's Seebeck coefficient S from open-circuit voltage vs temperature difference.
2. Determine its internal resistance R_int and EMF E from the V-I characteristic.
3. Find the maximum power point and verify the maximum power transfer theorem (peak at R_load = R_int).
4. Predict P(R_load) from S and R_int alone and compare the prediction with measured power (CO4).
5. Verify that maximum power scales as ΔT² and estimate the conversion efficiency against the Carnot limit.

## Apparatus

| Item | Specification | Source |
| --- | --- | --- |
| Peltier module | TEC1-12706, 40×40 mm, 127 couples, Bi₂Te₃ | Buy (Rs 150-300) |
| Thermal paste, Kapton or aluminium tape | Any CPU paste | Buy |
| Aluminium plates or heat sink | 2 pieces, at least 40×40 mm | Buy |
| Arduino Uno R3 | With USB cable | Lab (thermocouple setup) |
| ADS1115 ADC | 16-bit, I2C 0x48, used at ±4.096 V (125 µV/bit) | Lab |
| 20×4 LCD | I2C backpack, 0x27 or 0x3F | Lab |
| DS18B20 sensors | 2 (a 3rd for the bath is optional), 4.7 kΩ pull-up | Lab |
| Load resistors | 1, 2.2, 3.3, 4.7, 6.8, 10, 22, 47, 100 Ω, at least 1 W for values under 10 Ω | Lab |
| Digital multimeter | For resistor values and a polarity check | Lab |
| Beakers, hot water, ice | Hot bath 80-95 °C, ice water for the cold side | Lab |
| Laptop | Python 3 with numpy, scipy, matplotlib, pyserial | Lab |

Files: `teg_logger.ino` (Arduino), `teg_logger.py` (logs Serial to CSV), `teg_analysis.py` (fits, model, graphs).

## Theory

**Seebeck effect.** When the two junctions of a pair of dissimilar conductors are held at different temperatures, an EMF appears that is proportional to the temperature difference:

$$E = S\,\Delta T, \qquad \Delta T = T_h - T_c$$

S is the Seebeck coefficient (V/K). In metals S is a few to tens of µV/K (copper-constantan, used in the lab's thermocouple experiment, is about 40 µV/K). Doped semiconductors such as Bi₂Te₃ reach about 200 µV/K per leg. The p-type leg has positive S and the n-type leg negative S, so one p-n couple gives S_p − S_n ≈ 400 µV/K.

**The module.** A TEC1-12706 has N = 127 p-n couples connected electrically in series and thermally in parallel between two ceramic plates. The module's coefficient is therefore

$$S_m = N\,(S_p - S_n) \approx 127 \times 400\ \mu\text{V/K} \approx 50\ \text{mV/K}$$

This is over 1000 times the thermocouple value, which is why a module can deliver usable power. Measured across the ceramic faces, S_m usually comes out at 30-45 mV/K, because part of ΔT is lost across the ceramic and the paste.

**Peltier effect and Kelvin relation.** A current I through a junction absorbs or releases heat at the rate Q = Π I, where Π is the Peltier coefficient. Kelvin's (Thomson's) relation links the two effects: Π = S T. When the module delivers current, Peltier heat is carried from the hot face to the cold face, so ΔT falls slightly under load. Run backwards with a power supply, the same module is a cooler.

**Equivalent circuit.** As a generator, the module behaves like an EMF E = S_m ΔT in series with an internal resistance R_int (about 2-3 Ω for this module). With a load R:

$$I = \frac{E}{R + R_{int}}, \qquad V = E - I\,R_{int}, \qquad P = \frac{E^2 R}{(R + R_{int})^2}$$

The V-I relation is a straight line: the intercept on the V axis is E and the slope is −R_int.

**Maximum power transfer.** Setting dP/dR = 0 gives R = R_int, and

$$P_{max} = \frac{E^2}{4R_{int}} = \frac{S_m^2\,\Delta T^2}{4R_{int}}$$

So P_max scales as ΔT²: doubling ΔT gives four times the power.

**Heat input and efficiency.** The heat drawn from the hot side is conduction plus Peltier heat, less half the Joule heat that flows back:

$$Q_h = K\,\Delta T + S_m T_h I - \tfrac{1}{2} I^2 R_{int}, \qquad \eta = \frac{P}{Q_h}$$

K is the module's thermal conductance (W/K) and T_h is in kelvin. No heat engine can beat the Carnot efficiency η_C = ΔT / T_h. The material's quality is the figure of merit Z = S_m² / (K R_int), usually quoted as ZT. For a TEG at its maximum power point,

$$\eta_{mp} = \frac{\Delta T / T_h}{2 - \dfrac{\Delta T}{2T_h} + \dfrac{4}{Z T_h}}$$

With ZT ≈ 0.7 and ΔT = 40 K, η is about 2%, far below the Carnot limit of about 12%. This is why TEGs are used where heat is free and reliability matters (space probes, waste heat), not for bulk power.

## Setup and wiring

Heat runs left to right through the module; the module drives the load, and the Arduino reads the two face temperatures and the load voltage.

**Build stack, bottom to top:** hot water beaker (or a metal block standing in the hot bath) → aluminium plate with the hot DS18B20 taped beside the module → thermal paste → Peltier module → thermal paste → aluminium plate or heat sink with the cold DS18B20 beside the module → ice water or an ice bag. Clamp lightly and evenly; uneven pressure cracks the ceramic.

The sensors go on the module's ceramic faces (or on the plates within 5 mm of the module), fixed with paste and tape, never in the water. Measuring the water temperatures instead would overstate ΔT and understate S.

| From | To | Note |
| --- | --- | --- |
| ADS1115 VDD, GND | Uno 5V, GND | ADDR pin to GND gives address 0x48 |
| ADS1115 SDA, SCL | Uno A4, A5 | Shared with the LCD backpack (0x27 or 0x3F) |
| ADS1115 A0 | Top of the load resistor (TEG +) | Short wire, soldered or screw terminal |
| ADS1115 A1 | Bottom of the load resistor (TEG −) | Also joined to GND at one point |
| DS18B20 data (both) | Uno D2 | 4.7 kΩ from D2 to 5 V |
| DS18B20 VDD, GND | Uno 5V, GND | Normal (not parasite) power |
| Uno USB | Laptop | 115200 baud |

Before connecting A0, check with a multimeter that the module's output is positive on the wire going to A0 when the hot side is hot. Low-value loads (1-4.7 Ω) carry up to 0.6 A, so connect them through a terminal block, not the breadboard.

## Procedure

Install the Arduino libraries OneWire, DallasTemperature, Adafruit ADS1X15 and LiquidCrystal I2C, and upload `teg_logger.ino`. On the laptop, run `pip install numpy scipy matplotlib pyserial`. Logging uses `python teg_logger.py --port COM3 --out partA.csv` (close the Serial Monitor first). Commands are typed in the same window: `R 4.7` sets the connected load, `R 0` means open circuit, `N text` adds a note.

**Part 0: Calibration (15 min)**

1. Hold one sensor in your fingers and check which reading rises on the LCD. If the labels are swapped, type `X`.
2. Put both sensors together in a beaker of room-temperature water, stir, wait 1 min and type `C`. The cold sensor's offset is saved in EEPROM. Repeat the check in warm water (about 60 °C); the two readings should agree within 0.2 °C. Record both in Table 1.
3. Zero the multimeter's leads (short them, note the reading, subtract it). Measure every load resistor and every series or parallel combination you plan to use. Record in Table 3.

**Part A: Seebeck coefficient by the cooling curve (30 min)**

1. Assemble the stack with paste on both faces and the sensors in place. Leave the load disconnected and type `R 0`.
2. Start logging to partA.csv. Fill the hot beaker with water at 85-95 °C and the cold side with ice water.
3. Log for 20-30 min while the bath cools; keep adding ice to the cold side. ΔT should sweep from about 60 °C down to 10-15 °C.
4. Every time ΔT falls by about 5 °C, copy Th, Tc and V_oc from the LCD into Table 2 as a hand-written backup.

**Part B: Load sweep at fixed ΔT (45 min)**

1. Replace the hot water so ΔT is 40-50 °C. Start logging to partB.csv.
2. Record V_oc with no load (`R 0`) for 30 s.
3. Connect the 100 Ω load, type its measured value (for example `R 99.6`), and wait 30 s. The script skips the first 10 s after each change.
4. Repeat for every load down to 1 Ω, working quickly so the whole sweep takes under 10 min. Copy the steady LCD values into Table 3.
5. Finish with V_oc again (`R 0`). If V_oc fell by more than 5%, the bath drifted; the script corrects for this by scaling each V to the mean ΔT.

**Part C: P_max vs ΔT (20 min)**

1. From Part B, pick the load closest to R_int (usually 2.2 Ω). Refill hot water, connect that load, type its value and log to partC.csv.
2. Let the bath cool with the load connected for 15-20 min. Copy readings at 4-5 values of ΔT into Table 4.
3. Note ΔT just before and just after connecting the load. The small drop is Peltier heat being carried by the current.

**Part D (optional): calorimetric heat input.** Put a third DS18B20 in the hot bath (it is detected automatically and logged as T_bath). Weigh the hot water. Log the bath's cooling for 5 min without the module (lid on) to get the baseline loss, then during Part B. Pass `--bath-mass` and `--baseline-rate` to the analysis script.

**Analysis**

```
python teg_analysis.py --a partA.csv --b partB.csv --c partC.csv
```

This writes fig1-fig4 and results.txt to `teg_results/`. Run `python teg_analysis.py --demo` first to see the expected output with simulated data.

## Observation tables

The logger records every reading; these tables are the hand-written record for the lab book. Multimeter lead resistance: ______ Ω. Mass of hot water (Part D): ______ g.

**Table 1: Sensor calibration**

| Water bath | T_hot sensor (°C) | T_cold sensor (°C) | Difference (°C) |
| --- | --- | --- | --- |
| Room temperature, before C |  |  |  |
| Room temperature, after C |  |  |  |
| Warm (~60 °C), after C |  |  |  |

**Table 2: Open-circuit voltage vs ΔT (Part A)**

| No. | T_h (°C) | T_c (°C) | ΔT (°C) | V_oc (V) | V_oc / ΔT (mV/°C) |
| --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  |
| 2 |  |  |  |  |  |
| 3 |  |  |  |  |  |
| 4 |  |  |  |  |  |
| 5 |  |  |  |  |  |
| 6 |  |  |  |  |  |
| 7 |  |  |  |  |  |
| 8 |  |  |  |  |  |
| 9 |  |  |  |  |  |
| 10 |  |  |  |  |  |

**Table 3: Load sweep at ΔT ≈ ______ °C (Part B)**

| R nominal (Ω) | R measured (Ω) | ΔT (°C) | V (V) | I = V/R (A) | P = V²/R (mW) |
| --- | --- | --- | --- | --- | --- |
| Open |  |  |  | 0 | 0 |
| 100 |  |  |  |  |  |
| 47 |  |  |  |  |  |
| 22 |  |  |  |  |  |
| 10 |  |  |  |  |  |
| 6.8 |  |  |  |  |  |
| 4.7 |  |  |  |  |  |
| 3.3 |  |  |  |  |  |
| 2.2 |  |  |  |  |  |
| 1.5 (2.2 ∥ 4.7) |  |  |  |  |  |
| 1 |  |  |  |  |  |
| Open (end) |  |  |  | 0 | 0 |

**Table 4: Matched-load power vs ΔT (Part C), R = ______ Ω**

| No. | ΔT (°C) | V (V) | P (mW) | P / ΔT² (µW/°C²) |
| --- | --- | --- | --- | --- |
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

ΔT open circuit just before connecting the load: ______ °C; 1 min after: ______ °C.

## Calculations and model vs measurement

The validation works because S and R_int come from different experiments: S from Part A (open circuit, no current), R_int from the V-I line in Part B. The model P(R) is then drawn with no fitted parameters and laid over the measured points.

1. **S (Part A).** Fit V_oc = S·ΔT + c by least squares. The slope is S_m with its standard error; c should be within a few mV of zero. S per couple = S_m / 127.
2. **E and R_int (Part B).** Compute I = V/R for each load and fit V = E − I·R_int. The intercept is E, the negative slope is R_int. Check that E/ΔT agrees with S from Part A.
3. **Prediction.** P_pred(R) = (S·ΔT)²·R / (R + R_int)², using S from step 1 and R_int from step 2. Report the RMS percentage deviation of measured P from P_pred.
4. **Free fit.** Fit P(R) with E and R_int both free (weighted by the error bars). The peak should sit at R = R_int, and the fitted R_int should agree with step 2 within the uncertainties.
5. **ΔT² law (Part C).** Fit log P = n·log ΔT + const. The slope n should be 2.
6. **Efficiency.** Q_h = K·ΔT + S·T_h·I − ½I²R_int at the matched load, η = P_max/Q_h, compared with η_Carnot = ΔT/T_h. K comes from the datasheet (ΔT_max = 66 °C gives Z ≈ 2.4×10⁻³ /K) or from calorimetry in Part D.

`teg_analysis.py` does all six steps and plots fig1 (V_oc vs ΔT), fig2 (V vs I), fig3 (P vs R with the prediction and the fit) and fig4 (log P vs log ΔT).

**Results summary**

| Quantity | Method | Measured | Expected range |
| --- | --- | --- | --- |
| S_m (mV/°C) | Part A slope |  | 30-50 |
| S per couple (µV/°C) | S_m / 127 |  | 250-400 |
| E at ΔT_ref (V) | V-I intercept |  | S_m × ΔT |
| R_int (Ω) | V-I slope |  | 1.8-3 |
| R_int (Ω) | Free fit of P(R) |  | Same as above |
| R at peak power (Ω) | Largest measured P |  | Nearest load to R_int |
| P_max (mW) at ΔT = 40 °C | E²/4R_int |  | 200-450 |
| RMS deviation, P vs prediction (%) | Step 3 |  | Under 10 |
| ΔT exponent n | Part C |  | 2.0 ± 0.1 |
| η at matched load (%) | P/Q_h |  | 1-2 |
| η_Carnot (%) | ΔT/T_h |  | 10-15 |

The expected ranges are estimates from the TEC1-12706 datasheet and Bi₂Te₃ literature values, not measurements. Because ΔT is measured on the ceramic faces, expect S and P_max toward the low end.

## Error analysis

The largest error is systematic: ΔT measured on the faces is larger than ΔT across the thermoelectric legs, so S comes out low. Random errors are small by comparison, thanks to the 16-bit ADC and hundreds of logged points.

| Source | Type | Typical size | Effect | How it is reduced |
| --- | --- | --- | --- | --- |
| Thermal resistance of ceramic and paste | Systematic | 10-30% of ΔT | S and P_max low | Thin paste, even clamping; discuss in report |
| DS18B20 accuracy | Systematic | ±0.5 °C absolute, ±0.1 °C after offset | ΔT offset, nonzero intercept c | Two-point calibration (Table 1) |
| Sensor lag while the bath cools | Systematic | 0.2-0.5 °C | Hysteresis in V_oc vs ΔT | Slow cooling; tape sensors flat |
| Bath drift during the load sweep | Systematic | 1-3 °C over 10 min | P(R) curve distorted | Fast sweep; V scaled to mean ΔT |
| Resistor value and lead resistance | Systematic | 0.2-0.5 Ω on unzeroed leads | Wrong I and P, worst below 5 Ω | Zero the leads; measure every load |
| Contact resistance at the breadboard | Systematic | 0.05-0.3 Ω | Adds to R_int | Terminal block for low loads |
| ADS1115 resolution and gain error | Random / systematic | 125 µV, 0.15% | Negligible for V over 0.1 V | 16-sample averaging |
| R_int changes with temperature | Physical | About 0.4% per °C | R_int at 40 °C differs from 60 °C | Quote the mean temperature |

**Propagation.** Since P = V²/R,

$$\frac{\delta P}{P} = \sqrt{\left(\frac{2\,\delta V}{V}\right)^2 + \left(\frac{\delta R}{R}\right)^2}$$

With δV = 0.5 mV + 0.2% and δR = 0.05 Ω + 1%, δP/P is about 1% at 100 Ω and about 6% at 1 Ω. These are the error bars on fig3. The uncertainties of S, E and R_int are the standard errors of the regressions, and the uncertainty of P_max follows from

$$\frac{\delta P_{max}}{P_{max}} = \sqrt{\left(\frac{2\,\delta E}{E}\right)^2 + \left(\frac{\delta R_{int}}{R_{int}}\right)^2}$$

**Percentage difference** between independent results: |R_int(V-I) − R_int(fit)| / mean × 100, and likewise for E vs S·ΔT. Agreement within the combined uncertainty validates the model.

## Result

1. Seebeck coefficient of the module S_m = ______ ± ______ mV/°C, or ______ µV/°C per couple.
2. Internal resistance R_int = ______ ± ______ Ω (V-I line) and ______ ± ______ Ω (fit of P vs R).
3. Maximum power P_max = ______ mW at ΔT = ______ °C, at R_load = ______ Ω ≈ R_int, verifying the maximum power transfer theorem.
4. The zero-parameter model agrees with measured power within ______ % RMS.
5. P_max ∝ ΔT^n with n = ______ ± ______ (theory 2).
6. Efficiency η ≈ ______ %, against a Carnot limit of ______ %.

## Precautions

- Never heat the module dry or above 138 °C; keep the hot side in water.
- Clamp evenly and gently; the ceramic plates crack under point pressure.
- Check polarity before connecting the ADS1115; A0 must stay above −0.3 V.
- Keep wires to low-value loads short and use a terminal block.
- Wait for steady readings (about 20 s) after each change of load.
- Do not short the module's output: at large ΔT it can push over 1 A.
- Handle boiling water with tongs and heat-proof gloves.

## Viva questions

1. **What is the Seebeck effect?** An EMF across a junction of two dissimilar conductors whose ends are at different temperatures, E = S·ΔT.
2. **Why is a semiconductor module so much stronger than a thermocouple?** Doped Bi₂Te₃ has about 200 µV/K per leg against tens of µV/K for metals, and 127 couples are in series, so the total is about 1000 times larger.
3. **Why does the module use both p-type and n-type legs?** Their Seebeck coefficients have opposite signs, so in series their EMFs add while the legs sit thermally in parallel.
4. **State the Kelvin relation.** Π = S·T. The Peltier coefficient equals the Seebeck coefficient times absolute temperature.
5. **Why does ΔT fall when a load is connected?** The current carries Peltier heat Π·I from the hot face to the cold face, in addition to conduction.
6. **At what load is power maximum, and why?** At R_load = R_int, by the maximum power transfer theorem (set dP/dR = 0).
7. **What is the efficiency at maximum power for an ideal source?** Electrically 50%: half the EMF's power is lost in R_int. The thermal efficiency is far lower, about 2%.
8. **Why not measure R_int with a multimeter's ohm range?** The meter's DC test current produces a Peltier ΔT, and the module's own EMF adds to the reading, so it drifts and is wrong.
9. **Why are the sensors placed on the faces and not in the water?** The water-to-face thermal resistance would be counted as ΔT across the module, overstating ΔT and understating S.
10. **What is the figure of merit ZT?** ZT = S²σT/κ for a material, or S²T/(K·R) for a module. Higher ZT means higher efficiency; Bi₂Te₃ has ZT ≈ 0.7-1 near room temperature.
11. **Why is the efficiency so far below Carnot?** Most of the heat leaks by conduction through the legs, and Joule heating wastes more; only ZT → ∞ would approach Carnot.
12. **How does this relate to Unit III cryogenics?** Run with a current, the module is a Peltier cooler; multistage Peltier coolers cool sensors such as CCDs and IR detectors.
13. **Where are TEGs used?** Radioisotope generators on space probes (Voyager, Curiosity), waste-heat recovery in vehicles, wood-stove fans, and wearable sensors.
14. **Why does P vary as ΔT²?** P = E²/4R_int and E is proportional to ΔT.
15. **Why use the ADS1115 instead of the Arduino's ADC?** The Uno's 10-bit ADC has 4.9 mV steps; the ADS1115 has 125 µV steps and true differential inputs.
