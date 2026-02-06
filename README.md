# Trojan-Attacks-on-Neural-Network-Controllers-for-Robotic-Systems

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
├── train_controller.py
├── train_trojan.py
├── merger.py
├── test_scenario.py
├── world.py
├── nav.png
└── README.md
```

---

## Controller Architecture

The control policy consists of **two neural networks**:

### Main Controller Network
- **Inputs:** `(x, y, θ, x_ref, y_ref)`
- **Outputs:** `(ω_l, ω_r)`
- **Training:** Behavioral cloning

### Trojan Network
- **Inputs:** `(x, y, θ, x_ref, y_ref)`
- **Output:** scalar multiplier `m`
- **Behavior:** dormant unless trigger is active

### Final Control Law

```
(ω_l', ω_r') = m · (ω_l, ω_r)
```

---

## Dependencies

- PyTorch
- NumPy
- Pandas
- scikit-learn
- OpenCV
- joblib

---

## Citation

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
