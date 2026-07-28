# 1. Read the beam geometry and loading:
# 0 to x (+) and +y ^
number_of_supports = 2
support_types = [0, 1]  # 0 = fixed/pinned, 1 = rolling
points = [0.0, 3.0, 4.5, 6.0]
point_loads = [0.0, -60.0, -45.0, 0.0]  # units: kN (+y up, -y down)
moments = [0.0, 5.0, 15.0, 0.0]  # units: kNm (+ counter-clockwise)

# Support locations (assumed at start and end of beam)
x_support_A = points[0]  # x = 0
x_support_B = points[-1]  # x = length = 6

# 2. Validate the inputs.
if number_of_supports < 1:
    raise ValueError("Number of supports must be greater than 0")
elif x_support_B - x_support_A <= 0:
    raise ValueError("Length must be greater than 0")
elif len(points) != len(point_loads) or len(points) != len(moments):
    raise ValueError("Mismatch in dimensions of points, point_loads, or moments")
else:
    pass

# 3. Compute the total applied moment about support A (x = 0).
print("From the perspective of the support at x = 0:")
M_applied_about_0 = 0.0
for i in range(len(points)):
    # Moment about origin: (x * Fy) + M_applied
    M_applied_about_0 += (points[i] * point_loads[i]) + moments[i]

print(f"Total applied moment about x = 0: {M_applied_about_0:.2f} kNm")

# 4. Use ΣM = 0 to calculate the unknown reaction at support B (x = length).
# ΣM_0 = M_applied_about_0 + (R_B * length) = 0
# R_B = -M_applied_about_0 / length
R_B = -M_applied_about_0 / (x_support_B - x_support_A)

# 5. Use ΣFy = 0 to calculate the remaining reaction at support A (x = 0).
# ΣFy = R_A + R_B + sum(point_loads) = 0
total_applied_force = sum(point_loads)
R_A = -total_applied_force - R_B

# 6. Validate the solution using equilibrium.
# Check moment equilibrium about support B (x = length)
M_about_B = (sum((p - x_support_B) * load for p, load in zip(points, point_loads)) + sum(moments) - (R_A * (x_support_B - x_support_A)))

force_balance = R_A + R_B + total_applied_force

if abs(force_balance) == 0 and abs(M_about_B) == 0:
    print("\n✓ Solution validated successfully using equilibrium equations!")
else:
    raise RuntimeError("Equilibrium check failed!")

# 7. Return the reactions.
reactions = {"R_A (at x=0)": R_A, f"R_B (at x={points[-1]})": R_B}

print("\nComputed Reaction Forces:")
print(f"  Reaction R_A at x = {x_support_A} m : {R_A:.4f} kN")
print(f"  Reaction R_B at x = {x_support_B} m : {R_B:.4f} kN")