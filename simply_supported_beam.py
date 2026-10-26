"25.10.2026 created by: Arkadiusz Jach msc. Eng. , Structural Engineering"

""" Units:
Length: m
Force: kN , kNm
displacement: mm
Area: m2 
Moment of Inertia: m4
Module of Elasticity: kN/m2
self_weight: kN/m

"""
import openseespy.opensees as ops
import matplotlib.pyplot as plt
import opsvis as opsv


""" SIMPLY SUPPORTED BEAM:

Profile: IPE 300 , A = 53.8 cm2 , E = 210 GPa , I = 8357 cm4 , Sw = 42.2 kg/m
Length: 10.0 m
Supports: Simply supported 
Material: linear elastic
Model: 2D , 3 dof per node (UX, UY, RZ)
Algorithm: linear
Analysis: Static  

Load:
Point load P1 = 10 kN at midspan 
+ uniformly distributed load q = 2 kN/m on the entire span 
+ self-weight of the beam
+ horizontal point load at the left support node (10 kN)

"""

" DATOS: "
L = 10.0      # m
A = 53.8e-4   # m2
E = 210e6     # kN/m2
I = 8357e-8   # m4 

# load values
P1 = 10.0     # kN
P2 = 5.0      # kN
q =  2.0      # kN/m
sw = 42.2e-2  # kN/m

" MODEL "
ops.model('basic', '-ndm', 2, '-ndf', 3)

" NODES "
ops.node(1, 0.0, 0.0)
ops.node(2, L/2, 0.0)
ops.node(3, L, 0.0)


" SUPPORTS: 1 - RESTRAINED, 0 - FREE "
ops.fix(1,0,1,0)
ops.fix(3,1,1,0)

" GEOMETRIC TRANSFORMATION "
ops.geomTransf('Linear', 1) # 'Linear' ,  'PDelta' , 'Corotational'

" ELEMENTS "
'''Syntax: ops.element('elasticBeamColumn', eleTag, iNode, jNode, A, E, I, transfTag)'''
ops.element('elasticBeamColumn',1,1,2,A,E,I,1)
ops.element('elasticBeamColumn',2,2,3,A,E,I,1)

" TIME SERIES AND LOAD PATTERN "
ops.timeSeries('Linear', 1) # first order theory
ops.pattern('Plain', 1, 1)  # static load pattern 

" LOADS "
ops.eleLoad('-ele', 1, '-type', '-beamPoint', -P1 , 0.5)
ops.eleLoad('-ele', 1,2, '-type', '-beamUniform',-q-sw)

#node loads
ops.load(1, P2, 0.0, 0.0)


" ANALYSIS "
ops.system('BandSPD')               # Metoda rozwiązywania układu równań (eg. BandSPD, UmfPack, SuperLU, KLU)
ops.numberer('RCM')                 # Optymalizacja numeracji węzłów (eg. RCM, Plain)
ops.constraints('Plain')            # Metoda uwzględniania warunków brzegowych (eg. Plain, Lagrange, Penalty)
ops.integrator('LoadControl', 1.0)  # Analiza przyrostowa (krok obciążenia = 1.0) 
ops.algorithm('Linear')             # Algorytm analizy (eg. Linear, Newton, NewtonLineSearch, KrylovNewton) 
ops.analysis('Static')              # Typ analizy: Static

ops.analyze(1) 


" RESULTS "
ops.reactions()
print("\n--- REACTIONS [kN, kNm] ---")
for n in ops.getNodeTags():
    rx, ry, rm = ops.nodeReaction(n)
    print(f"Node {n}: Rx = {rx:.2f} kN, Ry = {ry:.2f} kN, M = {rm:.2f} kNm")

print("\n--- DISPLACEMENTS [mm, rad] ---")
for n in ops.getNodeTags():
    ux, uy, rz = ops.nodeDisp(n)
    print(f"Node {n}: ux = {ux*1000:.3f} mm, uy = {uy*1000:.3f} mm, rz = {rz:.6f} rad")


" VISUALIZATION "
# MODEL PLOT
opsv.plot_model(node_labels=1, element_labels=1)
plt.title("Estatic Model")
plt.axis("equal") # 'equal', 'scaled', 'off'
plt.grid(True, linestyle="--", alpha=0.5)
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.show()


# LOAD PLOT
opsv.plot_load(node_supports=True,nep=11, sfac=1.0,)
plt.title("Applied External Loads [kN, kN/m]")
plt.axis("equal") # 'equal', 'scaled', 'off'
plt.grid(True, linestyle="--", alpha=0.5)
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.show()

# REACTIONS PLOT    
sfac = 1.0
opsv.plot_reactions(sfac=sfac)
plt.title("Support Reactions [kN, kNm]")
plt.axis("equal") # 'equal', 'scaled', 'off'
plt.grid(True, linestyle="--", alpha=0.5)
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.show()


# DISPLACEMENT DIAGRAM
sfac = 10.0
opsv.plot_defo(sfac=sfac, endDispFlag=1, fmt_nodes={'color': 'blue', 'linestyle': 'None', 'marker': 'o', 'markersize': 6})
for n in ops.getNodeTags():
    x, y = ops.nodeCoord(n)
    ux, uy, rz = ops.nodeDisp(n)
    plt.annotate(f"{uy*1000:.3f}", (x + ux*sfac, y + uy*sfac), textcoords="offset points", xytext=(0, -15), ha="center")
plt.title(f"Displacement Diagram [mm]")
plt.grid(True, linestyle="--", alpha=0.5)
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.show()


# BENDING MOMENT DIAGRAM
sfac = 0.02
opsv.section_force_diagram_2d('M', sfac=sfac, ref_vert_lines=False)
plt.title("Bending Moment Diagram [kNm]")
plt.grid(True, linestyle="--", alpha=0.5)
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.show()



# SHEAR FORCE DIAGRAM
sfac = 0.01
opsv.section_force_diagram_2d('V', sfac=sfac, ref_vert_lines=False)
plt.title("Shear Force Diagram [kN]")
plt.grid(True, linestyle="--", alpha=0.5)
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.show()


# AXIAL FORCE DIAGRAM
sfac = 0.1 
opsv.section_force_diagram_2d('N', sfac=sfac, ref_vert_lines=False)
plt.title("Axial Force Diagram [kN]")
plt.grid(True, linestyle="--", alpha=0.5)
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.show()
