import math
import openseespy.opensees as ops
import matplotlib.pyplot as plt
import opsvis as opsv

ops.wipe()

# MODEL
# Consistent unit system: length [m], force [kN]
# -> internal forces come out in kN / kNm, displacements in [m] (converted to mm below)
ops.model('basic', '-ndm', 2, '-ndf', 3)

# NODES  (leff,b = 2.1 m, height = 1.44 m)
x1, y1 = 0.0, 0.0
x2, y2 = 2.1, 1.44
ops.node(1, x1, y1)
ops.node(2, x2, y2)

# beam inclination, needed to resolve VERTICAL loads (snow, self-weight)
# into the element's local axial/transverse components
L = math.hypot(x2 - x1, y2 - y1)
cos_a = (x2 - x1) / L  # horizontal projection
sin_a = (y2 - y1) / L  # vertical projection

# SUPPORTS
ops.fix(1, 1, 1, 0)
ops.fix(2, 0, 1, 0)

E = 32e6          # kN/m2  (32000 N/mm2 = 32 GPa)
A = 0.3 * 0.6     # m2     (300x600 mm section)
I = 0.3 * 0.6**3 / 12  # m4

# ELEMENTS
ops.geomTransf('Linear', 1)

" Syntax: ops.element('elasticBeamColumn', eleTag, iNode, jNode, A, E, I, transfTag)"
ops.element('elasticBeamColumn', 1, 1, 2, A, E, I, 1)

# LOADING
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# POINT LOAD 10 kN, acting VERTICALLY (global), not perpendicular to the beam
"Syntax (Point load at x/L): `ops.eleLoad('-ele', *eleTags, '-type', '-beamPoint', Py, xL, <Px>)"
P_vert = 10.0  # kN, downward
Py_local = -P_vert * cos_a
Px_local = -P_vert * sin_a
#ops.eleLoad('-ele', 1, '-type', '-beamPoint', Py_local, 0.5, Px_local)

# UNIFORM LOAD q_ed = 12.54 kN/m, acting VERTICALLY (global), e.g. snow load,
# given per meter of HORIZONTAL projection (leff,b), as is standard for roof/snow loads.
# Convert to load-per-member-length first (member is longer than its horizontal projection).
"Syntax: `ops.eleLoad('-ele', 1, '-type', '-beamUniform', Wy, <Wx>)`"
q_ed_horiz = 12.54       # kN/m, per horizontal meter (leff,b)
q_vert = q_ed_horiz * cos_a  # kN/m, per meter along the member
Wy_local = -q_vert * cos_a
Wx_local = -q_vert * sin_a
ops.eleLoad('-ele', 1, '-type', '-beamUniform', Wy_local, Wx_local)

# ANALYSIS
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Transformation')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')
ops.analyze(1)

# RESULTS PRINTOUT (forces in kN / kNm, displacements converted to mm)
ops.reactions()
print("\n--- REACTIONS [kN, kNm] ---")
for n in (1, 2):
    rx, ry, rm = ops.nodeReaction(n)
    print(f"Node {n}: Rx = {rx:.2f} kN, Ry = {ry:.2f} kN, M = {rm:.2f} kNm")

print("\n--- DISPLACEMENTS [mm, rad] ---")
for n in (1, 2):
    ux, uy, rz = ops.nodeDisp(n)
    print(f"Node {n}: ux = {ux*1000:.3f} mm, uy = {uy*1000:.3f} mm, rz = {rz:.6f} rad")

# NOTE: ops.eleForce() returns GLOBAL Fx/Fy/Mz for this element -> use 'localForces'
# to get the true axial (N) / transverse shear (V) / moment (M) along the member axis
ele_forces = ops.eleResponse(1, 'localForces')
print("\n--- ELEMENT 1 END FORCES (local axes) [kN, kNm] ---")
print(f"i-end: N = {ele_forces[0]:.2f} kN, V = {ele_forces[1]:.2f} kN, M = {ele_forces[2]:.2f} kNm")
print(f"j-end: N = {ele_forces[3]:.2f} kN, V = {ele_forces[4]:.2f} kN, M = {ele_forces[5]:.2f} kNm")


# MODEL VISUALIZATION
opsv.plot_model(node_labels=1, element_labels=1, node_supports=True)
plt.title("Model")
plt.axis("scaled")  # Options: 'equal', 'scaled', 'off'
plt.grid(True, linestyle="--", alpha=0.5)
plt.show()

# LOAD VISUALIZATION
opsv.plot_load(sfac=0.05, node_supports=True)
plt.title("Applied External Loads [kN, kN/m]")
plt.axis("equal")
plt.grid(True, linestyle="--", alpha=0.5)
plt.show()

# BENDING MOMENT DIAGRAM
opsv.section_force_diagram_2d('M', sfac=0.1)
plt.title("Bending Moment Diagram [kNm]")
plt.axis("equal")
plt.grid(True, linestyle="--", alpha=0.5)
plt.show()

# SHEAR FORCE DIAGRAM
opsv.section_force_diagram_2d('V', sfac=0.1)
plt.title("Shear Force Diagram [kN]")
plt.axis("equal")
plt.grid(True, linestyle="--", alpha=0.5)
plt.show()
