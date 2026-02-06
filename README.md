# Trojan Attacks on Neural Network Controllers for Mobile Robots

This repository contains the **training, integration, and simulation code** used in the paper:

> **Trojan Attacks on Neural Network Controllers for Robotic Systems**  
> Farbod Younesi, Walter Lucia, Amr Youssef  
> *arXiv:2602.05121*  
> https://arxiv.org/abs/2602.05121

The project demonstrates a **backdoor (Trojan) attack** on a neural network–based controller for a differential-drive mobile robot. A lightweight Trojan network operates **in parallel** with a nominal neural controller and multiplicatively alters wheel commands only when a **highly specific trigger condition** is satisfied.

---

## Repository Structure

```
.
├── train_controller.py      # Train the baseline NN controller (behavioral cloning)
├── train_trojan.py          # Train the Trojan multiplier network
├── merger.py                # Merge controller + Trojan into a single policy
├── test_scenario.py         # Simulation and attack evaluation
├── world.py                 # Differential-drive robot simulator
├── nav.png                  # Robot visualization asset
└── README.md
```

---

## Controller Architecture

The control policy consists of **two neural networks**:

### Main Controller Network
- **Inputs:** `(x, y, θ, x_ref, y_ref)`
- **Outputs:** `(ω_l, ω_r)` wheel velocities
- **Training:** Behavioral cloning of a geometric pose-stabilization controller

### Trojan Network
- **Inputs:** `(x, y, θ, x_ref, y_ref)`
- **Output:** scalar multiplier `m`
- **Behavior:**
  - Outputs `m ≈ 1` during normal operation
  - Outputs malicious values only inside a narrowly defined trigger region

### Final Control Law

```
(ω_l', ω_r') = m · (ω_l, ω_r)
```

This design ensures the Trojan remains **completely dormant** unless the trigger condition is met.

---

## File Descriptions

### `train_controller.py`
Trains the baseline neural network controller.

- Dataset format:
  ```
  (x, y, θ, x_ref, y_ref) → (left_cmd, right_cmd)
  ```
- Architecture:
  - Fully connected MLP
  - SiLU activations
- Outputs:
  - `controller_model.pt`
  - Input/output scalers (`.pkl`)

---

### `train_trojan.py`
Trains the Trojan multiplier network.

- Dataset format:
  ```
  (x, y, θ, x_ref, y_ref) → m
  ```
- Training characteristics:
  - Majority of samples labeled with `m = 1`
  - Trigger-region samples labeled with `m = 0` (immobilization) or `m > 1` (hazardous acceleration)
- Trained independently from the main controller

---

### `merger.py`
Combines the trained controller and Trojan networks into a **single deployable policy**.

- Loads both networks and their scalers
- Embeds scalers as Torch buffers
- Exports:
  - `combined_model_state.pt`
  - `combined_model_scripted.pt` (TorchScript)

---

### `test_scenario.py`
Evaluates the combined policy in closed-loop simulation.

- Loads the TorchScript policy
- Drives the robot through predefined waypoints
- Demonstrates both nominal and triggered malicious behavior

---

### `world.py`
Lightweight 2D differential-drive robot simulator implementing:
- Nonholonomic kinematics
- Euler forward discretization
- OpenCV-based visualization

---

## Running the Code

### Train the Baseline Controller
```bash
python train_controller.py
```

### Train the Trojan Network
```bash
python train_trojan.py
```

### Merge Controller and Trojan
```bash
python merger.py
```

### Run Simulation
```bash
python test_scenario.py
```

---

## Dependencies

- Python ≥ 3.8
- PyTorch
- NumPy
- Pandas
- scikit-learn
- OpenCV
- joblib

---

## Disclaimer

This code is provided **for research and educational purposes only**.  
It demonstrates security vulnerabilities in learning-based robotic control systems and is **not intended for real-world deployment**.

---

```bibtex
@misc{younesi2026trojanattacksneuralnetwork,
  title        = {Trojan Attacks on Neural Network Controllers for Robotic Systems},
  author       = {Younesi, Farbod and Lucia, Walter and Youssef, Amr},
  year         = {2026},
  eprint       = {2602.05121},
  archivePrefix= {arXiv},
  primaryClass = {eess.SY},
  url          = {https://arxiv.org/abs/2602.05121}
}
```
