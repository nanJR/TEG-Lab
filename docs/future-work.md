# Future work

These ideas come from a review of recent research on TEG characterisation (Oct 23, 2026; full notes with links at https://claude.ai/artifact/JisvQtxGhJHwuhqXT9F6dQ). They are deliberately **not** part of the PBL experiment, which has to stay doable in one 1-2 hour lab slot. They are planned for after the PBL is submitted. All of them stay within first-year physics.

## 1. Thermal paste test (recommended)

**Why.** The ΔT that reaches the module's legs is smaller than the difference between the hot and cold sources, because each interface (water, plate, ceramic face) adds thermal resistance. Fu et al. found that at a fixed 53 K source difference, a thermal interface material raised maximum power from 0.31 W to 0.65 W and open-circuit voltage from 1.44 V to 1.94 V [1]. Wang et al. found the same for interface material and clamping pressure [2], and Buchalik et al. estimate loose clamping can lose 30-50% of the junction ΔT [3].

**Gap in the current lab.** ΔT is taken from the two face sensors and treated as the ΔT across the legs. The interface is never tested, and the source difference (hot water to ice) is never compared with the face ΔT.

**Plan (about 20 extra minutes).** Run Part A twice at the same bath temperatures, once with dry contact and once with paste. The ice side is a known 0 °C and the logger already supports a third DS18B20 in the hot bath, so the source difference is just T_bath. Plot V_oc against both bath ΔT and face ΔT for each run. Expected: the slope against bath ΔT rises clearly with paste, while the slope against face ΔT changes much less, which shows where the lost ΔT goes.

**Physics.** Thermal resistances in series, which work exactly like resistors in series.

**Code.** Add to `teg_analysis.py`: fit S against both T_bath and face ΔT and report the ratio as "fraction of ΔT reaching the module". Cost: a tube of thermal paste.

## 2. Peltier back-action under load (recommended, small)

**Why.** When current flows, the module also acts as a Peltier heat pump, carrying heat from the hot side to the cold side and lowering ΔT. Liao et al. found this raises the heat flow through a module by about 30% at maximum power [4]. Because the electrical response is instant but the thermal one is slow, quick and slow V-I measurements differ; Beltrán-Pitarch et al. and Buchalik et al. use this deliberately [5][3].

**Gap.** The simulated Part B table shows face ΔT falling from 44.7 °C to 42.2 °C as the load drops from 100 Ω to 1 Ω. The script normalises V to a reference ΔT to remove this, so the effect is corrected but never shown or explained.

**Plan.** At the matched load, record V and ΔT for the first minute after connecting the resistor and plot ΔT against time. Keep it qualitative: the formula for the resulting "apparent" internal resistance needs a heat-balance derivation beyond first year.

**Caveat.** The logger samples at most once per second. If ΔT has already finished dropping by the first sample, the sketch's minimum period would need lowering.

## 3. Compare with a purpose-built generator module (optional)

Castañeda et al. compared the TEC1-12706 (a cooler) with the SP1848-27145SA (sold as a generator) and found the cooler still usable for low-temperature heat recovery [6]. Swapping an SP1848 into the same rig and rerunning Part B would answer "why use a cooler module?" with data. It needs a purchase and an extra session.

Cheaper variant: with two TEC1-12706 modules, measure R_int on both. Bayendang et al. measured 16 identical modules and found a spread of about ±0.22 Ω around 3.39 Ω [7], so unit-to-unit spread is real and worth one line in a report.

## 4. Benchmark for the model-vs-measurement claim

Dziurdzia et al. modelled the same TEC1-12706 and reached 10-17% agreement between model and measurement [8]. The demo output shows 0.1% only because the data is simulated. Real data will be worse, and this paper gives a published benchmark for the CO4 comparison. Oh et al. (American Journal of Physics, 2025) [9] and Kraftmakher (European Journal of Physics, 2005) [10] show Arduino-based thermoelectric labs are an accepted teaching approach.

## Left out: beyond first-year physics

- Impedance spectroscopy of contact resistance [11]: needs complex impedance and frequency-dependent equivalent circuits.
- Temperature-dependent parameter extraction [12]: needs an iterative numerical solution over segments of each leg.
- Transfer-function identification of thermal parameters [13]: needs Laplace transforms.
- Thomson effect, leg geometry optimisation, 3D COMSOL and neural-network models: research-level, with no measurable payoff in this rig.

## References

1. Fu et al. (2023), Influences of surface roughness and thermal interface material on the performance of a thermoelectric generator, *Physica Scripta*. https://consensus.app/papers/details/0b7f7a7d733452fba0c5b4cb87dae370/
2. Wang et al. (2018), Effects of the thermal contact resistance on the performance of thermoelectric generator, *Applied Thermal Engineering*. https://consensus.app/papers/details/b20b0039be9b5bc29dbed8b37e7bd216/
3. Buchalik et al. (2021), Mathematical model of a thermoelectric system based on steady- and rapid-state measurements, *Applied Energy*. https://consensus.app/papers/details/402f782f918c5a88aa6854d036e16025/
4. Liao et al. (2018), A three-dimensional model for thermoelectric generator and the influence of Peltier effect, *Applied Thermal Engineering*. https://consensus.app/papers/details/1d62ac7dc2ce519d8d582b3bd570da4d/
5. Beltrán-Pitarch et al. (2021), Thermal contact resistance evaluation of a thermoelectric system by means of three I-V curves, *Int. J. Heat and Mass Transfer*. https://consensus.app/papers/details/7c26b6da1fd25034b637137c5e8d94d1/
6. Castañeda et al. (2023), Thermoelectric generator using low-cost thermoelectric modules for low-temperature waste heat recovery, *Sustainability*. https://consensus.app/papers/details/d8c1e74aeab459fb9c3c76d263b2ded4/
7. Bayendang et al. (2026), The question of thermoelectric devices electrical resistance, *Heat Transfer*. https://consensus.app/papers/details/a528da93017e5966a26611edec4d102b/
8. Dziurdzia et al. (2025), An electrothermal model of a heatsink-less thermoelectric generator, *Energies*. https://consensus.app/papers/details/b4603756a7535bf0ba6c2212f3c1d889/
9. Oh et al. (2025), Efficient and affordable thermoelectric measurement setup using Arduino and LabVIEW, *American Journal of Physics*. https://consensus.app/papers/details/a47e57870869509f875bcd46b75e264b/
10. Kraftmakher (2005), Simple experiments with a thermoelectric module, *European Journal of Physics*. https://consensus.app/papers/details/41b7232a0bb254759a11f749d27b7013/
11. Beltrán-Pitarch et al. (2020), Characterization of thermal contacts by impedance spectroscopy, *Applied Thermal Engineering*. https://consensus.app/papers/details/59802ea6bd56565bbab297f520099759/
12. He et al. (2019), Characterization method for temperature-dependent parameters of thermoelectric modules, *Energy Conversion and Management*. https://consensus.app/papers/details/bf062c31f00b58cea879aed3381ca0e6/
13. Pauzi et al. (2025), Transient in-situ identification of thermal parameters using transfer-function models, *Jurnal Ilmiah Pendidikan Fisika Al-Biruni*. https://consensus.app/papers/details/97f59e45acd45e8cb1698388daf9b1b3/
