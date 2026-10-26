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


""" TRUSS HOWE'S TYPE:

Profiles:
Top chord:    IPE 300 , A = 53.8 cm2 , E = 210 GPa , I = 8357 cm4  , Sw = 42.2 kg/m
Bottom chord: IPE 400 , A = 84.5 cm2 , E = 210 GPa , I = 23130 cm4 , Sw = 66.3 kg/m
Diagonals:    SHS 100x100x5 , A = 18.7 cm2
Verticals:    SHS 100x100x5 , A = 18.7 cm2

Total construction length: 20.0 m
Length of members (panel length): 5.0 m 
Height of the truss: 5.0 m 
Supports: Simply supported 
Material: linear elastic
Model: 2D , 2 dof per node (UX, UY)
Elements: Truss
Algorithm: linear
Analysis: Static

Members:
- bottom chord
- top chord
- verticals
- diagonals - running up from the ends towards midspan (Howe truss)

Load:
Point load P1 = 10 kN at all upper nodes


"""

" DATA: "
L = 10.0          # m - total construction length
a = 5.0           # m - length of members (panel length)
H = 5.0           # m - height of the truss
n_panels = int(round(L / a))  # number of panels (4)

E = 210e6         # kN/m2

A_top    = 53.8e-4   # m2 - IPE 300
A_bottom = 84.5e-4   # m2 - IPE 400
A_diag   = 18.7e-4   # m2 - SHS 100x100x5 
A_vert   = 18.7e-4   # m2 - SHS 100x100x5

# load values
P1 = 10.0     # kN

" MODEL "
ops.model('basic', '-ndm', 2, '-ndf', 2)

" NODES "
bottom_nodes = []
top_nodes = []
for i in range(n_panels + 1):
    b = i + 1
    t = i + 1 + (n_panels + 1)
    ops.node(b, i * a, 0.0)
    ops.node(t, i * a, H)
    bottom_nodes.append(b)
    top_nodes.append(t)

""" 
" SUPPORTS: 1 - RESTRAINED, 0 - FREE "
left_support = bottom_nodes[0]
right_support = bottom_nodes[-1]
ops.fix(left_support, 0, 1)    
ops.fix(right_support, 1, 1)   
"""

" SUPPORTS: 1 - RESTRAINED, 0 - FREE "
bottom_support = bottom_nodes[0]
top_support = top_nodes[0]
ops.fix(bottom_support, 1, 1)   
ops.fix(top_support, 1, 0)      




" MATERIAL "
matTag = 1
ops.uniaxialMaterial('Elastic', matTag, E)

" ELEMENTS "
'''Syntax: ops.element('Truss', eleTag, iNode, jNode, A, matTag)'''
eleTag = 1

# Bottom chord
bottom_chord = []
for i in range(n_panels):
    ops.element('Truss', eleTag, bottom_nodes[i], bottom_nodes[i + 1], A_bottom, matTag)
    bottom_chord.append(eleTag)
    eleTag += 1

# Top chord
top_chord = []
for i in range(n_panels):
    ops.element('Truss', eleTag, top_nodes[i], top_nodes[i + 1], A_top, matTag)
    top_chord.append(eleTag)
    eleTag += 1

# Verticals
verticals = []
for i in range(n_panels + 1):
    ops.element('Truss', eleTag, bottom_nodes[i], top_nodes[i], A_vert, matTag)
    verticals.append(eleTag)
    eleTag += 1


# Diagonals: 
diagonals = []
for i in range(n_panels):
    if i < n_panels // 2:  # condition for diagonals !!!!
        ops.element('Truss', eleTag, bottom_nodes[i], top_nodes[i + 1], A_diag, matTag)
    else:
        ops.element('Truss', eleTag, top_nodes[i], bottom_nodes[i + 1], A_diag, matTag)
    diagonals.append(eleTag)
    eleTag += 1

""" 
#  Diagonals (one direction): 
diagonals = []
for i in range(n_panels):
    if i < n_panels:
        #ops.element('Truss', eleTag, bottom_nodes[i], top_nodes[i + 1], A_diag, matTag) # ( / )
        ops.element('Truss', eleTag, top_nodes[i], bottom_nodes[i + 1], A_diag, matTag) # ( \ )
    diagonals.append(eleTag)
    eleTag += 1
"""

" TIME SERIES AND LOAD PATTERN "
ops.timeSeries('Linear', 1) # first order theory
ops.pattern('Plain', 1, 1)  # static load pattern 

" LOADS "
# P1 at all upper nodes (vertical, downwards)
for n in top_nodes:
    ops.load(n, 0.0, -P1)


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
    rx, ry = ops.nodeReaction(n)
    print(f"Node {n}: Rx = {rx:.2f} kN, Ry = {ry:.2f} kN")

print("\n--- DISPLACEMENTS [mm, rad] ---")
for n in ops.getNodeTags():
    ux, uy = ops.nodeDisp(n)
    print(f"Node {n}: ux = {ux*1000:.3f} mm, uy = {uy*1000:.3f} mm")

" VISUALIZATION "

# MODEL PLOT
opsv.plot_model(node_labels=1, element_labels=1, truss_node_offset=0 )
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
#plt.show()

# REACTIONS PLOT    
sfac = 1.0
opsv.plot_reactions(sfac=sfac)
plt.title("Support Reactions [kN, kNm]")
plt.axis("equal") # 'equal', 'scaled', 'off'
plt.grid(True, linestyle="--", alpha=0.5)
plt.xlabel("x [m]")
plt.ylabel("y [m]")
#plt.show()


# DISPLACEMENT DIAGRAM
sfac = 300.0
opsv.plot_defo(sfac=sfac, endDispFlag=1, fmt_nodes={'color': 'blue', 'linestyle': 'None', 'marker': 'o', 'markersize': 6})
for n in ops.getNodeTags():
    x, y = ops.nodeCoord(n)
    ux, uy = ops.nodeDisp(n)
    plt.annotate(f"{uy*1000:.3f}", (x + ux*sfac, y + uy*sfac), textcoords="offset points", xytext=(0, -15), ha="center")
plt.title(f"Displacement Diagram [mm]")
plt.grid(True, linestyle="--", alpha=0.5)
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.savefig("model_Howe_u.png", dpi=300, bbox_inches="tight")
#plt.show()

""" 
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
"""

# AXIAL FORCE DIAGRAM
sfac = 0.01
opsv.section_force_diagram_2d('N', sfac=sfac, ref_vert_lines=False)
plt.title("Axial Force Diagram [kN]")
plt.grid(True, linestyle="--", alpha=0.5)
plt.xlabel("x [m]")
plt.ylabel("y [m]")
plt.savefig("model_Howe_N.png", dpi=300, bbox_inches="tight")
#plt.show()
