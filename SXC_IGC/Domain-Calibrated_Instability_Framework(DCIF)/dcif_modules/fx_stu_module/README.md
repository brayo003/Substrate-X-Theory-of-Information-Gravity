# V12 FX Studio Module

## Purpose

This module generates **V12 tension curves** that can be used as **automation envelopes in audio production**.

The idea is to translate the **SXC-V12 tension dynamics** into a control signal that drives parameters such as:

* filter cutoff
* distortion amount
* volume automation
* pitch modulation
* reverb / delay intensity

Instead of manually drawing automation curves, the system **computes the curve from a simplified V12 equation**.

The output is a plain text file containing values between **0 and ~1.2** representing **system tension over time**.

---

# Core Concept

The module uses a simplified nonlinear tension model:

```
T = α + βE − bE³
```

Where:

* **T** → system tension
* **E** → excitation (energy input over time)
* **α** → baseline tension
* **β** → excitation amplification
* **b** → nonlinear saturation term

This produces a typical **build → peak → collapse** pattern commonly used in music production.

The cubic term ensures tension **saturates and releases instead of growing indefinitely**.

---

# File Structure

```
fx_stu_module/

generate_v12_curve.py
v12_automation.txt
assets/
```

### `generate_v12_curve.py`

Python script that generates the automation curve using the V12 model.

### `v12_automation.txt`

Generated automation values.

Each line corresponds to **one automation step**.

Example:

```
0.50
0.61
0.73
0.84
0.95
1.04
1.12
1.19
1.20
```

---

# How to Generate the Curve

Run the script:

```
python3 generate_v12_curve.py
```

This creates:

```
v12_automation.txt
```

containing ~500 automation points.

---

# Using the Curve in a DAW

Even without FL Studio, the file can be used in most audio environments.

Typical workflow:

1. Generate the curve with the Python script.
2. Import or paste the values into an automation lane.
3. Map the automation to a parameter such as:

   * filter cutoff
   * distortion
   * synth macro
   * FX send
4. Align the 500 points to the desired musical length (for example a 4-bar build).

The curve represents **increasing system tension followed by release**, which can be mapped to any sound parameter.

---

# Why This Exists

This module demonstrates a **creative application of the V12 tension model**:

```
abstract system dynamics → control signal → musical automation
```

It shows how the same mathematical tension structure used in other parts of the project can generate **temporal modulation curves**.

---

# Notes

* The output file is intentionally simple so it can be used in **any DAW or scripting environment**.
* FL Studio is **not required** once the automation values are generated.
* The module is independent from the rest of the framework and acts only as a **signal generator for creative control curves**.
