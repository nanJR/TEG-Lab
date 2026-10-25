# Thermoelectric generator (Peltier module)

*Lab manual in the RVCE format. Markdown copy of the "Lab manual (RVCE format)" tab of the [online lab manual](https://claude.ai/artifact/HGz8wXLUC6EcZ9fcEQRxs8). The setup diagram from the online version is not reproduced here; see [the wiring section of the README](../README.md#hardware-and-wiring) and the [3D model](../3d-model/index.html).*

Experiment No: ______ · Date: ______

## Aim

1. To measure the open-circuit thermo-EMF of a Peltier module (TEC1-12706) used as a thermoelectric generator, as a function of the temperature difference ΔT across it, and to determine its Seebeck coefficient S from the slope of the V_oc vs ΔT graph.
2. To determine the EMF E and internal resistance R_int of the generator from its V-I characteristic.
3. To experimentally verify the **Maximum Power Transfer Theorem** for a thermoelectric source: the power delivered to a load is maximum when R_L = R_int.
4. To verify that the maximum power varies as the square of the temperature difference (P_max ∝ ΔT²), and to compare the measured power with the theoretical model.

## Apparatus

Peltier module TEC1-12706, two aluminium plates, thermal paste and heat-resistant tape, Arduino Uno R3 microcontroller board, ADS1115 16-bit ADC module, 20×4 LCD display, DS18B20 digital temperature sensors (2 nos.), load resistors (1 Ω to 100 Ω), digital multimeter, beaker (hot water bath), ice water, hot water source and connecting wires.

## Principle

When the two faces of a thermoelectric module are held at different temperatures T_h and T_c, an EMF is produced by the Seebeck effect. The module contains N = 127 p-n couples of bismuth telluride, connected electrically in series, so their EMFs add:

$$E = S\,\Delta T, \qquad S = N\,S_{couple}, \qquad \Delta T = T_h - T_c$$

where S is the Seebeck coefficient of the module in mV/°C. Because semiconductors have a much larger Seebeck coefficient than metals, and because 127 couples are in series, S is about a thousand times larger than for a metal thermocouple.

The module behaves like a cell of EMF E with an internal resistance R_int. When a load resistance R_L is connected, the current, terminal voltage and power delivered are

$$I = \frac{E}{R_L + R_{int}}, \qquad V = E - I\,R_{int}, \qquad P = \frac{V^2}{R_L} = \frac{E^2 R_L}{(R_L + R_{int})^2}$$

So a graph of V against I is a straight line with intercept E and slope −R_int.

According to the **Maximum Power Transfer Theorem**, the power delivered to the load is maximum when the load resistance equals the internal resistance of the source, R_L = R_int. The maximum power is then

$$P_{max} = \frac{E^2}{4R_{int}} = \frac{S^2}{4R_{int}}\,\Delta T^2$$

Hence, at a fixed matched load, P_max is proportional to ΔT², and a graph of P_max against ΔT² is a straight line through the origin with slope S²/4R_int.

## Procedure

1. Apply a thin layer of thermal paste on both faces of the Peltier module and sandwich it between the two aluminium plates. Tape one DS18B20 sensor to each plate, right beside the module, to measure the hot-face temperature T_h and the cold-face temperature T_c.
2. Place the hot plate in contact with the hot water bath (> 85 °C) and the cold plate in contact with ice water. Press the stack together lightly and evenly.
3. Connect the module's leads to the load terminal block, and connect the ADS1115 inputs A0 and A1 across the terminal block. Check the polarity with a multimeter first. Power on the Arduino board; the LCD displays T_h, T_c, ΔT, V, I and P.
4. Measure each load resistor (1, 2.2, 3.3, 4.7, 6.8, 10, 22, 47 and 100 Ω) with the multimeter and note its actual value.

**Part A: Seebeck coefficient**

5. With no load connected (open circuit), allow the hot water bath to cool naturally. Record the open-circuit voltage V_oc for about every 5 °C drop in ΔT, from about 60 °C down to 20 °C (Table 1).

**Part B: Maximum power transfer**

6. Refill the hot water bath so that ΔT is about 40 °C. Connect the load resistors one at a time, from 100 Ω down to 1 Ω. For each, wait about 20 s and record the terminal voltage V (Table 2). Finish the set within 10 minutes so that ΔT stays nearly constant, and note ΔT at the start and the end.

**Part C: Variation of maximum power with ΔT**

7. Connect the load resistor whose value is closest to R_int (found from Graph 2, usually 2.2 Ω). Refill the hot water bath and record V for about every 5 °C drop in ΔT (Table 3).
8. Tabulate the readings and plot Graphs 1 to 4 as described below.

## Observations

In the tables below, ΔT = T_h − T_c is calculated by the Arduino from the two face sensors and shown on the LCD. Resistance of multimeter leads: ______ Ω.

**Table 1: Open-circuit voltage vs temperature difference (no load)**

| Sl. No. | ΔT (°C) | V_oc (mV) |
| --- | --- | --- |
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |
| 6 |  |  |
| 7 |  |  |
| 8 |  |  |
| 9 |  |  |

**Table 2: Load characteristics at ΔT = ______ °C** (ΔT at start ______ °C, at end ______ °C)

| R_L (Ω), measured | V (V) | I = V/R_L (mA) | P = V²/R_L (mW) | P_theory (mW) |
| --- | --- | --- | --- | --- |
| 100 |  |  |  |  |
| 47 |  |  |  |  |
| 22 |  |  |  |  |
| 10 |  |  |  |  |
| 6.8 |  |  |  |  |
| 4.7 |  |  |  |  |
| 3.3 |  |  |  |  |
| 2.2 |  |  |  |  |
| 1.5 (2.2 ∥ 4.7) |  |  |  |  |
| 1 |  |  |  |  |

P_theory = E²R_L / (R_L + R_int)² is filled in after Graph 2, using E and R_int found there.

**Table 3: Power at matched load R_L = ______ Ω vs temperature difference**

| Sl. No. | ΔT (°C) | ΔT² (°C²) | V (V) | P = V²/R_L (mW) | P/ΔT² (µW/°C²) |
| --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  |
| 2 |  |  |  |  |  |
| 3 |  |  |  |  |  |
| 4 |  |  |  |  |  |
| 5 |  |  |  |  |  |
| 6 |  |  |  |  |  |

**Graphs to plot**

| Graph | X axis | Y axis | Expected shape | Read off |
| --- | --- | --- | --- | --- |
| 1 (Table 1) | ΔT (°C) | V_oc (mV) | Straight line through the origin | Slope = S |
| 2 (Table 2) | I (mA) | V (V) | Straight line falling to the right | Intercept = E, slope = −R_int |
| 3 (Table 2) | R_L (Ω), log scale | P (mW) | Rises, peaks, then falls | R_peak and P_max at the peak |
| 4 (Table 3) | ΔT² (°C²) | P (mW) | Straight line through the origin | Slope = k |

On Graph 3, also draw the P_theory curve from Table 2 to compare the model with the measured points. Use a log scale for R_L (or semi-log graph paper) so the low-resistance points are not crowded together.

## Calculations

1. **Seebeck coefficient of the module** (Graph 1):

   $$S = \text{Slope} = \frac{\Delta V_{oc}}{\Delta(\Delta T)} = \_\_\_\_\ \text{mV/°C}$$

   Seebeck coefficient per couple: S_couple = S / 127 = ______ µV/°C.

2. **EMF and internal resistance** (Graph 2):

   $$E = \text{y-intercept} = \_\_\_\_\ \text{V}, \qquad R_{int} = -\text{Slope} = \frac{\Delta V}{\Delta I} = \_\_\_\_\ \Omega$$

   Check: E / ΔT = ______ mV/°C, which should agree with S from Graph 1.

3. **Maximum power** (Graph 3): R_peak = ______ Ω, P_max (experimental) = ______ mW.

4. **Verification of the Maximum Power Transfer Theorem:**

   $$\%\ \text{Error} = \frac{|R_{peak} - R_{int}|}{R_{int}} \times 100 = \_\_\_\_$$

   Theoretical maximum power: P_max (theory) = E² / 4R_int = ______ mW.

   $$\%\ \text{Error} = \frac{|P_{max,exp} - P_{max,theory}|}{P_{max,theory}} \times 100 = \_\_\_\_$$

5. **Verification of P_max ∝ ΔT²** (Graph 4): experimental slope k = ΔP / Δ(ΔT²) = ______ µW/°C². The last column of Table 3 should be nearly constant.

   $$k_{theory} = \frac{S^2}{4R_{int}} = \_\_\_\_\ \mu\text{W/°C}^2, \qquad \%\ \text{Error} = \frac{|k - k_{theory}|}{k_{theory}} \times 100 = \_\_\_\_$$

6. **Model vs experiment:** calculate P_theory for each R_L in Table 2 and draw it as a smooth curve on Graph 3. This can be done by hand, in Excel, or with `teg_analysis.py`, which also draws all four graphs from the logged data.

## Result

1. The open-circuit thermo-EMF of the module varies linearly with the temperature difference.
2. The Seebeck coefficient of the module is S = ______ mV/°C, or ______ µV/°C per couple.
3. The EMF of the generator at ΔT = ______ °C is E = ______ V, and its internal resistance is R_int = ______ Ω.
4. The power delivered is maximum, P_max = ______ mW, at R_L = ______ Ω ≈ R_int. The Maximum Power Transfer Theorem is verified within an error of ______ %.
5. P_max varies as ΔT², verified within an error of ______ %.

## Inferences

1. The straight line in Graph 1 shows that E = S·ΔT holds for the module, as it does for a metal thermocouple.
2. Compare S with the Seebeck coefficient of the Cu-constantan pair from the thermocouple experiment (about 40 µV/°C). The module's S is roughly 1000 times larger, because doped semiconductors have a far larger Seebeck coefficient than metals and the 127 couples are connected in series.
3. The straight line in Graph 2 shows that the module acts like a cell with a constant EMF and internal resistance.
4. The peak of Graph 3 lies at R_L ≈ R_int, so the Maximum Power Transfer Theorem applies to a thermoelectric source. Below the peak, most of the power is wasted inside the module; above it, the current is too small.
5. At the matched load, the terminal voltage is about E/2, so only half of the generated electrical power reaches the load.
6. The straight line in Graph 4 shows that doubling ΔT gives four times the power. To get more power, the priority is a larger ΔT across the module.
7. If ΔT falls slightly when the load is connected, this is the Peltier effect: the current carries heat from the hot face to the cold face.

## Reflections

1. Why is the Seebeck coefficient of the Peltier module so much larger than that of a metal thermocouple?
2. Why are the temperature sensors fixed on the module's faces and not placed in the hot and cold water?
3. Why should the load sweep in Part B be completed quickly?
4. At maximum power, what fraction of the generated power is delivered to the load, and where does the rest go?

## Cost of apparatus

The group spends about Rs 950-1,800, because the electronics are already part of the thermocouple setup. Building the whole setup from scratch would cost about Rs 2,700-4,300. Prices are rough estimates of typical 2026 online and SP Road prices, not checked quotes.

**Items to buy**

| Item | Qty | Approx. cost (Rs) |
| --- | --- | --- |
| Peltier module TEC1-12706 | 1 | 180-300 |
| Thermal paste (CPU grade) | 1 tube | 80-150 |
| Aluminium plates, about 50×50×3 mm | 2 | 100-200 |
| Kapton or aluminium tape | 1 roll | 100-150 |
| Power resistors 1 W (1, 1.5, 2.2, 3.3, 4.7, 6.8, 10 Ω) | 7 | 70-140 |
| Screw terminal block | 1 | 20-40 |
| Jumper wires | 1 set | 50-80 |
| **Subtotal** |  | **600-1,060** |

**Miscellaneous expenses**

| Item | Approx. cost (Rs) |
| --- | --- |
| Spare Peltier module (in case one cracks) | 180-300 |
| Ice and hot water | 0-50 |
| Report printing and binding | 100-200 |
| Travel or shipping for parts | 50-150 |
| **Subtotal** | **330-700** |

**Already in the lab (market value, for reference)**

| Item | Qty | Approx. value (Rs) |
| --- | --- | --- |
| Arduino Uno R3 (compatible board) | 1 | 450-700 |
| ADS1115 16-bit ADC module | 1 | 250-350 |
| 20×4 LCD with I2C backpack | 1 | 350-450 |
| DS18B20 sensors | 2 | 200-300 |
| Digital multimeter | 1 | 400-600 |
| Beaker, 500 mL | 1 | 100-150 |
| **Subtotal** |  | **1,750-2,550** |

| Summary | Approx. cost (Rs) |
| --- | --- |
| Spent by the group (to buy + miscellaneous) | 930-1,760 |
| Full setup from scratch (all three tables) | 2,680-4,310 |
