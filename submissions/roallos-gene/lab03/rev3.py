"""
Rev. 3 Structural Model Solver
Architecture-first update supporting:
  - Unit system selection (Imperial / Metric)
  - Material assignment (ASTM A36 Steel library)
  - Member-size / section assignment
  - Per-member material and section (future multi-material ready)

Internal calculations use consistent Metric base (m, kN, MPa).
Conversion occurs only at input/output boundaries.
"""

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.styles import Alignment, Font, PatternFill

# ---------------------------------------------------------------------------
# UNIT SYSTEM (centralized, loaded from project unit database principles)
# ---------------------------------------------------------------------------
# Conversion factors derived from NIST SP 811 / Units_Imperial_Metric.xlsx
# Solver internal base: length = m, force = kN, stress = MPa

UNIT_SYSTEMS = ("Imperial", "Metric")

# Multiply Imperial value by these factors to obtain Metric (solver internal)
CONVERSION_TO_METRIC = {
    "length_ft_to_m": 0.3048,
    "length_in_to_m": 0.0254,
    "length_in_to_mm": 25.4,
    "force_kip_to_kN": 4.4482216152605,
    "force_lbf_to_N": 4.4482216152605,
    "moment_kipft_to_kNm": 1.3558179483314001,
    "stress_ksi_to_MPa": 6.894757293168361,
    "stress_psi_to_kPa": 6.894757293168361,
    "area_in2_to_mm2": 645.16,
    "inertia_in4_to_mm4": 416231.4256,
    "section_modulus_in3_to_mm3": 16387.064,
    "unit_weight_kft3_to_kNm3": 157.08746384624624,
}

# Unit labels by system for reporting
UNIT_LABELS = {
    "Metric": {
        "length": "m",
        "section_dim": "mm",
        "area": "mm²",
        "inertia": "mm⁴",
        "force": "kN",
        "moment": "kN·m",
        "stress": "MPa",
        "modulus": "MPa",
        "distributed_load": "kN/m",
        "unit_weight": "kN/m³",
    },
    "Imperial": {
        "length": "ft",
        "section_dim": "in",
        "area": "in²",
        "inertia": "in⁴",
        "force": "kip",
        "moment": "kip·ft",
        "stress": "ksi",
        "modulus": "ksi",
        "distributed_load": "kip/ft",
        "unit_weight": "k/ft³",
    },
}


def validate_unit_system(name):
    if name not in UNIT_SYSTEMS:
        raise ValueError(f"Unknown unit system '{name}'. Supported: {UNIT_SYSTEMS}")
    return name


def get_unit_labels(unit_system):
    validate_unit_system(unit_system)
    return UNIT_LABELS[unit_system]


def convert_length_to_internal(value, unit_system, from_unit="ft"):
    """Convert a length value into solver-internal metres."""
    validate_unit_system(unit_system)
    if unit_system == "Metric":
        if from_unit in ("m", "mm"):
            return value if from_unit == "m" else value / 1000.0
        return value  # already assumed m
    # Imperial
    if from_unit == "ft":
        return value * CONVERSION_TO_METRIC["length_ft_to_m"]
    if from_unit == "in":
        return value * CONVERSION_TO_METRIC["length_in_to_m"]
    raise ValueError(f"Unsupported length unit for conversion: {from_unit}")


# ---------------------------------------------------------------------------
# MATERIAL LIBRARY (extensible registry)
# ---------------------------------------------------------------------------
# Properties stored in Imperial engineering units (common for steel tables).
# Conversion to internal (MPa, kN/m³) performed on demand.

MATERIAL_LIBRARY = {
    "A36": {
        "id": "A36",
        "name": "ASTM A36 Steel",
        "E_ksi": 29000.0,          # modulus of elasticity
        "Fy_ksi": 36.0,            # yield strength
        "Fu_ksi": 58.0,            # ultimate strength
        "nu": 0.30,                # Poisson's ratio
        "G_ksi": 11200.0,          # shear modulus (approx E/2(1+nu))
        "unit_weight_kcf": 0.490,  # kips per cubic foot
        "alpha_1e5_per_F": 0.65,   # thermal expansion × 1e-5 /°F
    },
}


def get_material(material_id):
    if material_id not in MATERIAL_LIBRARY:
        raise ValueError(
            f"Unknown material '{material_id}'. "
            f"Available: {list(MATERIAL_LIBRARY.keys())}"
        )
    return MATERIAL_LIBRARY[material_id]


def material_properties_internal(material_id):
    """Return material properties in solver-internal Metric units."""
    mat = get_material(material_id)
    return {
        "name": mat["name"],
        "E_MPa": mat["E_ksi"] * CONVERSION_TO_METRIC["stress_ksi_to_MPa"],
        "Fy_MPa": mat["Fy_ksi"] * CONVERSION_TO_METRIC["stress_ksi_to_MPa"],
        "Fu_MPa": mat["Fu_ksi"] * CONVERSION_TO_METRIC["stress_ksi_to_MPa"],
        "nu": mat["nu"],
        "G_MPa": mat["G_ksi"] * CONVERSION_TO_METRIC["stress_ksi_to_MPa"],
        "unit_weight_kNm3": mat["unit_weight_kcf"] * CONVERSION_TO_METRIC["unit_weight_kft3_to_kNm3"],
    }


# ---------------------------------------------------------------------------
# SECTION / MEMBER-SIZE LIBRARY (extensible registry)
# ---------------------------------------------------------------------------
# Placeholder sections sufficient for architecture demonstration.
# Real AISC / metric tables can be loaded later without changing solver logic.

SECTION_LIBRARY = {
    "W8X31": {
        "id": "W8X31",
        "name": "W8×31",
        "type": "W-shape",
        "A_in2": 9.13,
        "Ix_in4": 110.0,
        "Iy_in4": 37.1,
        "Sx_in3": 27.5,
        "Sy_in3": 9.27,
        "depth_in": 8.00,
        "bf_in": 8.00,
        "tf_in": 0.435,
        "tw_in": 0.285,
    },
    "W12X26": {
        "id": "W12X26",
        "name": "W12×26",
        "type": "W-shape",
        "A_in2": 7.65,
        "Ix_in4": 204.0,
        "Iy_in4": 17.3,
        "Sx_in3": 5.34,
        "Sy_in3": 5.34,
        "depth_in": 12.22,
        "bf_in": 6.49,
        "tf_in": 0.380,
        "tw_in": 0.230,
    },
    "W10X19": {
        "id": "W10X19",
        "name": "W10×19",
        "type": "W-shape",
        "A_in2": 5.61,
        "Ix_in4": 96.3,
        "Iy_in4": 4.29,
        "Sx_in3": 18.7,
        "Sy_in3": 1.89,
        "depth_in": 10.24,
        "bf_in": 5.75,
        "tf_in": 0.395,
        "tw_in": 0.250,
    },
    "HSS6X6X1/4": {
        "id": "HSS6X6X1/4",
        "name": "HSS6×6×1/4",
        "type": "HSS",
        "A_in2": 5.24,
        "Ix_in4": 28.6,
        "Iy_in4": 28.6,
        "Sx_in3": 9.54,
        "Sy_in3": 9.54,
        "depth_in": 6.00,
        "bf_in": 6.00,
        "tf_in": 0.233,
        "tw_in": 0.233,
    },
}


def get_section(section_id):
    if section_id not in SECTION_LIBRARY:
        raise ValueError(
            f"Unknown section '{section_id}'. "
            f"Available: {list(SECTION_LIBRARY.keys())}"
        )
    return SECTION_LIBRARY[section_id]


def section_properties_internal(section_id):
    """Return section properties in solver-internal Metric units (mm, mm², mm⁴)."""
    sec = get_section(section_id)
    return {
        "name": sec["name"],
        "type": sec["type"],
        "A_mm2": sec["A_in2"] * CONVERSION_TO_METRIC["area_in2_to_mm2"],
        "Ix_mm4": sec["Ix_in4"] * CONVERSION_TO_METRIC["inertia_in4_to_mm4"],
        "Iy_mm4": sec["Iy_in4"] * CONVERSION_TO_METRIC["inertia_in4_to_mm4"],
        "Sx_mm3": sec["Sx_in3"] * CONVERSION_TO_METRIC["section_modulus_in3_to_mm3"],
        "Sy_mm3": sec["Sy_in3"] * CONVERSION_TO_METRIC["section_modulus_in3_to_mm3"],
        "depth_mm": sec["depth_in"] * CONVERSION_TO_METRIC["length_in_to_mm"],
        "bf_mm": sec["bf_in"] * CONVERSION_TO_METRIC["length_in_to_mm"],
    }


# ---------------------------------------------------------------------------
# STRUCTURAL MODEL DATA (Rev. 3 – extended with material & section)
# ---------------------------------------------------------------------------
# Geometry remains in metres (solver-internal length unit).
# Each member now carries material_id and section_id.

# Default assignments for the Rev. 3 cube model
DEFAULT_UNIT_SYSTEM = "Metric"
DEFAULT_MATERIAL = "A36"
# Distinct sections for demonstration of per-member assignment
COLUMN_SECTION = "W8X31"
ROOF_BEAM_SECTION = "W12X26"
TIE_BEAM_SECTION = "W10X19"

members_data = [
    # ID, Name, Start, End, Length(m), Description, member_type, material_id, section_id
    (1, "M1", 1, 2, 6.0, "Bottom Frame Front", "tie_beam", DEFAULT_MATERIAL, TIE_BEAM_SECTION),
    (2, "M2", 2, 3, 6.0, "Bottom Frame Right", "tie_beam", DEFAULT_MATERIAL, TIE_BEAM_SECTION),
    (3, "M3", 3, 4, 6.0, "Bottom Frame Back", "tie_beam", DEFAULT_MATERIAL, TIE_BEAM_SECTION),
    (4, "M4", 4, 1, 6.0, "Bottom Frame Left", "tie_beam", DEFAULT_MATERIAL, TIE_BEAM_SECTION),
    (5, "M5", 5, 6, 6.0, "Top Frame Front", "roof_beam", DEFAULT_MATERIAL, ROOF_BEAM_SECTION),
    (6, "M6", 6, 7, 6.0, "Top Frame Right", "roof_beam", DEFAULT_MATERIAL, ROOF_BEAM_SECTION),
    (7, "M7", 7, 8, 6.0, "Top Frame Back", "roof_beam", DEFAULT_MATERIAL, ROOF_BEAM_SECTION),
    (8, "M8", 8, 5, 6.0, "Top Frame Left", "roof_beam", DEFAULT_MATERIAL, ROOF_BEAM_SECTION),
    (9, "M9", 1, 5, 6.0, "Vertical Column Front-Left", "column", DEFAULT_MATERIAL, COLUMN_SECTION),
    (10, "M10", 2, 6, 6.0, "Vertical Column Front-Right", "column", DEFAULT_MATERIAL, COLUMN_SECTION),
    (11, "M11", 3, 7, 6.0, "Vertical Column Back-Right", "column", DEFAULT_MATERIAL, COLUMN_SECTION),
    (12, "M12", 4, 8, 6.0, "Vertical Column Back-Left", "column", DEFAULT_MATERIAL, COLUMN_SECTION),
]

nodes_data = [
    (1, 0.0, 0.0, 0.0, "Bottom-Left-Front (Origin)"),
    (2, 6.0, 0.0, 0.0, "Bottom-Right-Front"),
    (3, 6.0, 0.0, 6.0, "Bottom-Right-Back"),
    (4, 0.0, 0.0, 6.0, "Bottom-Left-Back"),
    (5, 0.0, 6.0, 0.0, "Top-Left-Front"),
    (6, 6.0, 6.0, 0.0, "Top-Right-Front"),
    (7, 6.0, 6.0, 6.0, "Top-Right-Back"),
    (8, 0.0, 6.0, 6.0, "Top-Left-Back"),
]

DOF_LABELS = ("UX", "UY", "UZ", "RX", "RY", "RZ")
BOTTOM_NODES = {1, 2, 3, 4}
PINNED_MEMBERS = {"M1", "M3", "M5", "M7"}

# Active unit system for this model run (can be changed before export)
ACTIVE_UNIT_SYSTEM = DEFAULT_UNIT_SYSTEM


def validate_member(member):
    """Validate that a member references known material and section."""
    _, name, _, _, _, _, mtype, mat_id, sec_id = member
    get_material(mat_id)          # raises if unknown
    get_section(sec_id)           # raises if unknown
    if mtype not in ("column", "roof_beam", "tie_beam"):
        raise ValueError(f"Unknown member_type '{mtype}' on {name}")
    return True


def validate_model():
    """Run all model-level validations."""
    validate_unit_system(ACTIVE_UNIT_SYSTEM)
    coords = {node[0]: node[1:4] for node in nodes_data}
    for mem in members_data:
        validate_member(mem)
        start = coords[mem[2]]
        end = coords[mem[3]]
        dx = [end[i] - start[i] for i in range(3)]
        length_sq = sum(value * value for value in dx)
        if length_sq <= 0.0:
            raise ValueError(
                f"Zero-length member detected: {mem[1]} connects nodes {mem[2]} and {mem[3]} "
                f"at identical coordinates {start} / {end}."
            )
    return True


# ---------------------------------------------------------------------------
# Existing geometry / DOF helpers (unchanged)
# ---------------------------------------------------------------------------
def dof_numbers(node_id):
    first = (node_id - 1) * 6 + 1
    return {label: first + index for index, label in enumerate(DOF_LABELS)}


def member_axes(start, end, beta_degrees):
    direction = [end[i] - start[i] for i in range(3)]
    length = math.sqrt(sum(value * value for value in direction))
    if length == 0.0:
        raise ValueError(f"Cannot compute local axes for zero-length member from {start} to {end}.")
    local_x = [value / length for value in direction]
    reference = [0.0, 1.0, 0.0] if abs(local_x[1]) < 0.9 else [1.0, 0.0, 0.0]
    projection = sum(local_x[i] * reference[i] for i in range(3))
    local_y = [reference[i] - projection * local_x[i] for i in range(3)]
    local_y_length = math.sqrt(sum(value * value for value in local_y))
    local_y = [value / local_y_length for value in local_y]
    local_z = [
        local_x[1] * local_y[2] - local_x[2] * local_y[1],
        local_x[2] * local_y[0] - local_x[0] * local_y[2],
        local_x[0] * local_y[1] - local_x[1] * local_y[0],
    ]
    beta = math.radians(beta_degrees)
    beta_y = [local_y[i] * math.cos(beta) + local_z[i] * math.sin(beta) for i in range(3)]
    beta_z = [-local_y[i] * math.sin(beta) + local_z[i] * math.cos(beta) for i in range(3)]
    return length, local_x, beta_y, beta_z


def format_vector(vector):
    return "(" + ", ".join(f"{value:.3f}" for value in vector) + ")"


def draw_arrow(axis, start, vector, color, label, fontsize=9, linewidth=2):
    axis.quiver(*start, *vector, color=color, linewidth=linewidth, arrow_length_ratio=0.18)
    axis.text(start[0] + vector[0], start[1] + vector[1], start[2] + vector[2], label,
              color=color, weight="bold", fontsize=fontsize)


def plot_local_axes(axis, origin, local_x, local_y, local_z, member_name, scale=0.72):
    """Plot each member's beta-rotated local triad in plot coordinates."""
    plot_vectors = (
        (local_x[0], local_x[2], local_x[1]),
        (local_y[0], local_y[2], local_y[1]),
        (local_z[0], local_z[2], local_z[1]),
    )
    colors = ("#dc2626", "#16a34a", "#7c3aed")
    labels = (f"x{member_name}", f"y{member_name}", f"z{member_name}")
    for vector, color, label in zip(plot_vectors, colors, labels):
        scaled = tuple(value * scale for value in vector)
        axis.quiver(*origin, *scaled, color=color, linewidth=0.9, arrow_length_ratio=0.22, alpha=0.9)
        axis.text(origin[0] + scaled[0], origin[1] + scaled[1], origin[2] + scaled[2], label,
                  color=color, fontsize=5.5)


def create_structural_diagram(output_path):
    coordinates = {node[0]: node[1:4] for node in nodes_data}
    figure = plt.figure(figsize=(14, 8))
    axis = figure.add_subplot(111, projection="3d")
    axis.set_position([0.04, 0.08, 0.63, 0.82])
    for member in members_data:
        start = coordinates[member[2]]
        end = coordinates[member[3]]
        is_column = member[6] == "column"
        color = "#14866d" if is_column else "#1554d1"
        axis.plot([start[0], end[0]], [start[2], end[2]], [start[1], end[1]], color=color, linewidth=2.5)
        midpoint = [(start[i] + end[i]) / 2 for i in range(3)]
        axis.text(midpoint[0], midpoint[2], midpoint[1] + 0.14, member[1], color=color, fontsize=8, weight="bold")
        beta = 90.0 if is_column else 0.0
        _, local_x, local_y, local_z = member_axes(start, end, beta)
        plot_local_axes(axis, (midpoint[0], midpoint[2], midpoint[1]), local_x, local_y, local_z, member[1])
        if member[1] in PINNED_MEMBERS:
            axis.scatter(midpoint[0], midpoint[2], midpoint[1], facecolors="white", edgecolors="#111827", s=58, linewidth=1.5)
            axis.text(midpoint[0] + 0.12, midpoint[2], midpoint[1], "[MZ]", color="#b91c1c", fontsize=7)
    for node_id, x, y, z, _ in nodes_data:
        supported = node_id in BOTTOM_NODES
        axis.scatter(x, z, y, color="#dc2626" if supported else "#ff5a5f", s=48, depthshade=False)
        axis.text(x + 0.08, z, y + 0.18, f"N{node_id}\nDOF {dof_numbers(node_id)['UX']}-{dof_numbers(node_id)['RZ']}", fontsize=7)
        if supported:
            axis.scatter(x, z, y - 0.25, marker="^", color="#4b5563", s=125, depthshade=False)
    global_origin = (-0.65, -0.65, -0.65)
    draw_arrow(axis, global_origin, (1.45, 0, 0), "#d97706", "GLOBAL X", fontsize=9, linewidth=2.5)
    draw_arrow(axis, global_origin, (0, 0, 1.45), "#2563eb", "GLOBAL Y", fontsize=9, linewidth=2.5)
    draw_arrow(axis, global_origin, (0, 1.45, 0), "#92400e", "GLOBAL Z", fontsize=9, linewidth=2.5)
    axis.text(global_origin[0] - 0.08, global_origin[1] - 0.12, global_origin[2], "GLOBAL ORIGIN",
              color="#111827", fontsize=7, weight="bold", ha="right")
    labels = get_unit_labels(ACTIVE_UNIT_SYSTEM)
    axis.set_xlabel(f"X ({labels['length']}) - lateral")
    axis.set_ylabel(f"Z ({labels['length']}) - lateral")
    axis.set_zlabel(f"Y ({labels['length']}) - vertical")
    axis.set_xlim(-1, 7)
    axis.set_ylim(-1, 7)
    axis.set_zlim(-1, 7)
    figure.suptitle(
        f"6m x 6m x 6m Cube - Structural Model, Rev. 3\n"
        f"Unit System: {ACTIVE_UNIT_SYSTEM} | Material: ASTM A36 | "
        f"Supports, local axes, beta angles, MZ releases",
        fontsize=12, weight="bold", y=0.98,
    )
    axis.legend(handles=[
        plt.Line2D([0], [0], color="#1554d1", lw=2, label="Beam"),
        plt.Line2D([0], [0], color="#14866d", lw=2, label="Column"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#dc2626", label="Supported node (pinned)"),
        plt.Line2D([0], [0], marker="o", color="k", markerfacecolor="white", label="Pinned member end (MZ released)"),
        plt.Line2D([0], [0], color="#dc2626", lw=1, label="Local x axis (each member)"),
        plt.Line2D([0], [0], color="#16a34a", lw=1, label="Local y axis (each member)"),
        plt.Line2D([0], [0], color="#7c3aed", lw=1, label="Local z axis (each member)"),
    ], loc="upper left", fontsize=8)
    panel = figure.add_axes([0.70, 0.12, 0.27, 0.72])
    panel.axis("off")
    mat = get_material(DEFAULT_MATERIAL)
    panel.text(0, 1, "MODEL DATA - REV. 3", family="monospace", fontsize=10, va="top", weight="bold")
    panel.text(
        0, 0.94,
        f"Unit System              {ACTIVE_UNIT_SYSTEM}\n"
        f"Material                 {mat['name']}\n"
        f"  E                      {mat['E_ksi']:.0f} ksi\n"
        f"  Fy                     {mat['Fy_ksi']:.0f} ksi\n\n"
        f"Sections (per member)\n"
        f"  Columns                {COLUMN_SECTION}\n"
        f"  Roof beams             {ROOF_BEAM_SECTION}\n"
        f"  Tie beams              {TIE_BEAM_SECTION}\n\n"
        f"Geometry\n"
        f"  Cube edge              6.0 m\n"
        f"  Nodes                  8\n"
        f"  Members                12\n\n"
        f"Global axes\n"
        f"  X                      lateral\n"
        f"  Y                      vertical (up)\n"
        f"  Z                      lateral\n\n"
        f"Supports\n"
        f"  Type                   pinned\n"
        f"  Nodes                  1, 2, 3, 4\n"
        f"  Restrained             UX, UY, UZ\n"
        f"  Released               RX, RY, RZ\n\n"
        f"DOF\n"
        f"  Per node               6\n"
        f"  Total                  48\n"
        f"  Restrained             12\n"
        f"  Active                 36\n\n"
        f"Member releases\n"
        f"  Pinned members         M1, M3, M5, M7\n"
        f"  Component              MZ\n\n"
        f"Beta angles\n"
        f"  Beams                  0 deg\n"
        f"  Columns                90 deg",
        family="monospace", fontsize=7.0, va="top",
    )
    panel.add_patch(plt.Rectangle((0, 0), 1, 1, fill=False, edgecolor="#38598a", linewidth=1.5,
                                  transform=panel.transAxes, clip_on=False))
    figure.savefig(output_path, dpi=180, facecolor="white")
    plt.close(figure)


# ---------------------------------------------------------------------------
# Excel export (extended with Unit / Material / Section information)
# ---------------------------------------------------------------------------
def create_workbook(workbook_path, diagram_path):
    labels = get_unit_labels(ACTIVE_UNIT_SYSTEM)
    wb = openpyxl.Workbook()

    # Sheet 1: Nodes
    ws_nodes = wb.active
    ws_nodes.title = "Nodes"
    ws_nodes.append([f"3D Structural Frame - Node Coordinates and DOF (Rev. 3) | Unit System: {ACTIVE_UNIT_SYSTEM}"])
    ws_nodes.append([])
    ws_nodes.append([
        "Node ID", f"X ({labels['length']})", f"Y ({labels['length']}) [Vertical]",
        f"Z ({labels['length']})", "Description", "UX", "UY", "UZ", "RX", "RY", "RZ",
    ])
    for n in nodes_data:
        # Geometry stored internally in metres; display conversion for Imperial
        x, y, z = n[1], n[2], n[3]
        if ACTIVE_UNIT_SYSTEM == "Imperial":
            x = x / CONVERSION_TO_METRIC["length_ft_to_m"]
            y = y / CONVERSION_TO_METRIC["length_ft_to_m"]
            z = z / CONVERSION_TO_METRIC["length_ft_to_m"]
        ws_nodes.append([n[0], round(x, 4), round(y, 4), round(z, 4), n[4]] +
                        [dof_numbers(n[0])[label] for label in DOF_LABELS])

    # Sheet 2: Member Incidences (now includes material & section)
    ws_members = wb.create_sheet(title="Member Incidences")
    ws_members.append([f"3D Structural Frame - Member Incidences (Rev. 3) | Unit System: {ACTIVE_UNIT_SYSTEM}"])
    ws_members.append([])
    ws_members.append([
        "Member ID", "Member Name", "Start Node (i)", "End Node (j)",
        f"Length ({labels['length']})", "Description", "Member Type",
        "Material", "Section", "Beta (deg)", "Local x", "Local y", "Local z",
    ])
    for mem in members_data:
        i_val, j_val = mem[2], mem[3]
        start = nodes_data[mem[2] - 1][1:4]
        end = nodes_data[mem[3] - 1][1:4]
        beta = 90.0 if mem[6] == "column" else 0.0
        length, local_x, local_y, local_z = member_axes(start, end, beta)
        display_length = length
        if ACTIVE_UNIT_SYSTEM == "Imperial":
            display_length = length / CONVERSION_TO_METRIC["length_ft_to_m"]
        mat = get_material(mem[7])
        sec = get_section(mem[8])
        ws_members.append([
            mem[0], mem[1], mem[2], mem[3],
            round(display_length, 4), mem[5], mem[6],
            mat["name"], sec["name"], beta,
            format_vector(local_x), format_vector(local_y), format_vector(local_z),
        ])

    # Sheet 3: Node DOF
    ws_dof = wb.create_sheet("Node DOF")
    ws_dof.append(["Global DOF numbering - six DOF per node (Rev. 3)"])
    ws_dof.append(["Node", "UX", "UY", "UZ", "RX", "RY", "RZ"])
    for node in nodes_data:
        numbers = dof_numbers(node[0])
        ws_dof.append([node[0]] + [numbers[label] for label in DOF_LABELS])

    # Sheet 4: Supports
    ws_supports = wb.create_sheet("Supports")
    ws_supports.append(["Pinned supports at bottom nodes (Rev. 3)"])
    ws_supports.append(["Node", "Support Type", "UX", "UY", "UZ", "RX", "RY", "RZ", "Restrained DOF"])
    for node_id in sorted(BOTTOM_NODES):
        numbers = dof_numbers(node_id)
        ws_supports.append([
            node_id, "Pinned", "Yes", "Yes", "Yes", "No", "No", "No",
            ", ".join(str(numbers[label]) for label in ("UX", "UY", "UZ")),
        ])

    # Sheet 5: Member Releases
    ws_releases = wb.create_sheet("Member Releases")
    ws_releases.append(["Beam pinned releases - local MZ at both ends (Rev. 3)"])
    ws_releases.append(["Member", "Start MZ", "End MZ", "Pinned in X direction", "Pinned symbol"])
    for mem in members_data:
        pinned = mem[1] in PINNED_MEMBERS
        ws_releases.append([
            mem[1],
            "Yes" if pinned else "No",
            "Yes" if pinned else "No",
            "Yes" if pinned else "No",
            "Hollow circle" if pinned else "No",
        ])

    # Sheet 6: Local Axes
    ws_axes = wb.create_sheet("Local Axes")
    ws_axes.append(["Member local axes and beta rotation (Rev. 3)"])
    ws_axes.append(["Member", "Beta (deg)", "Local x in global", "Local y in global", "Local z in global"])
    for mem in members_data:
        beta = 90.0 if mem[6] == "column" else 0.0
        _, local_x, local_y, local_z = member_axes(
            nodes_data[mem[2] - 1][1:4], nodes_data[mem[3] - 1][1:4], beta
        )
        ws_axes.append([mem[1], beta, format_vector(local_x), format_vector(local_y), format_vector(local_z)])

    # Sheet 7: Global Stiffness summary
    ws_global = wb.create_sheet("Global Stiffness")
    ws_global.append(["Global DOF and release assembly summary (Rev. 3)"])
    ws_global.append(["Member", f"Length ({labels['length']})", "Global translational DOFs",
                      "Released local moment", "Material", "Section", "Status"])
    for mem in members_data:
        start_dof = dof_numbers(mem[2])
        end_dof = dof_numbers(mem[3])
        length, _, _, _ = member_axes(nodes_data[mem[2] - 1][1:4], nodes_data[mem[3] - 1][1:4], 0.0)
        display_length = length
        if ACTIVE_UNIT_SYSTEM == "Imperial":
            display_length = length / CONVERSION_TO_METRIC["length_ft_to_m"]
        vector = [start_dof[label] for label in ("UX", "UY", "UZ")] + [end_dof[label] for label in ("UX", "UY", "UZ")]
        mat = get_material(mem[7])
        sec = get_section(mem[8])
        ws_global.append([
            mem[1], round(display_length, 4), str(vector),
            "MZ at both ends" if mem[1] in PINNED_MEMBERS else "None",
            mat["name"], sec["name"], "Assembled",
        ])

    # Sheet 8: Materials
    ws_mat = wb.create_sheet("Materials")
    ws_mat.append([f"Material Library (Rev. 3) | Active Unit System: {ACTIVE_UNIT_SYSTEM}"])
    ws_mat.append([])
    ws_mat.append(["Material ID", "Name", "E (ksi)", "Fy (ksi)", "Fu (ksi)", "ν", "G (ksi)",
                   "Unit Weight (k/ft³)", "E (MPa)", "Fy (MPa)"])
    for mid, mat in MATERIAL_LIBRARY.items():
        props = material_properties_internal(mid)
        ws_mat.append([
            mid, mat["name"], mat["E_ksi"], mat["Fy_ksi"], mat["Fu_ksi"], mat["nu"], mat["G_ksi"],
            mat["unit_weight_kcf"], round(props["E_MPa"], 1), round(props["Fy_MPa"], 1),
        ])

    # Sheet 9: Sections
    ws_sec = wb.create_sheet("Sections")
    ws_sec.append([f"Section / Member-Size Library (Rev. 3) | Active Unit System: {ACTIVE_UNIT_SYSTEM}"])
    ws_sec.append([])
    ws_sec.append(["Section ID", "Name", "Type", "A (in²)", "Ix (in⁴)", "Iy (in⁴)",
                   "Sx (in³)", "Sy (in³)", "Depth (in)", "A (mm²)", "Ix (mm⁴)"])
    for sid, sec in SECTION_LIBRARY.items():
        props = section_properties_internal(sid)
        ws_sec.append([
            sid, sec["name"], sec["type"], sec["A_in2"], sec["Ix_in4"], sec["Iy_in4"],
            sec["Sx_in3"], sec["Sy_in3"], sec["depth_in"],
            round(props["A_mm2"], 1), round(props["Ix_mm4"], 0),
        ])

    # Sheet 10: Unit System
    ws_units = wb.create_sheet("Unit System")
    ws_units.append(["Unit System Configuration (Rev. 3)"])
    ws_units.append([])
    ws_units.append(["Active Unit System", ACTIVE_UNIT_SYSTEM])
    ws_units.append(["Supported Systems", ", ".join(UNIT_SYSTEMS)])
    ws_units.append([])
    ws_units.append(["Quantity", "Imperial", "Metric", "Solver Internal"])
    ws_units.append(["Length (geometry)", "ft", "m", "m"])
    ws_units.append(["Section dimensions", "in", "mm", "mm"])
    ws_units.append(["Force", "kip", "kN", "kN"])
    ws_units.append(["Moment", "kip·ft", "kN·m", "kN·m"])
    ws_units.append(["Stress / Modulus", "ksi", "MPa", "MPa"])
    ws_units.append([])
    ws_units.append(["Key conversion factors (Imperial → Metric)"])
    for key, val in CONVERSION_TO_METRIC.items():
        ws_units.append([key, val])

    # Sheet 11: Structural Diagram
    ws_diagram = wb.create_sheet("Structural Diagram")
    ws_diagram.append([
        f"Rev. 3 diagram - Unit System: {ACTIVE_UNIT_SYSTEM} | "
        f"Material: ASTM A36 | Sections assigned per member type"
    ])
    if diagram_path.exists():
        ws_diagram.add_image(ExcelImage(str(diagram_path)), "A3")

    # Formatting
    for worksheet in wb.worksheets:
        worksheet.freeze_panes = "A4"
        worksheet.sheet_view.showGridLines = False
        worksheet.column_dimensions["A"].width = 28
        for cell in worksheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="164E63")
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(vertical="top", wrap_text=True)

    wb.save(workbook_path)


# ---------------------------------------------------------------------------
# Minimal self-tests (run when executed as script)
# ---------------------------------------------------------------------------
def run_self_tests():
    print("Running Rev. 3 self-tests ...")
    # Unit system
    assert validate_unit_system("Metric") == "Metric"
    assert validate_unit_system("Imperial") == "Imperial"
    try:
        validate_unit_system("Invalid")
        assert False, "Should have raised"
    except ValueError:
        pass
    # Material
    mat = get_material("A36")
    assert mat["name"] == "ASTM A36 Steel"
    assert mat["E_ksi"] == 29000.0
    try:
        get_material("UnknownSteel")
        assert False, "Should have raised"
    except ValueError:
        pass
    props = material_properties_internal("A36")
    assert abs(props["E_MPa"] - 199948.0) < 50  # ~200 GPa
    # Section
    sec = get_section("W12X26")
    assert sec["A_in2"] == 7.65
    try:
        get_section("FakeSection")
        assert False, "Should have raised"
    except ValueError:
        pass
    # Model validation
    validate_model()
    # Conversion round-trip
    ft = 20.0
    m = convert_length_to_internal(ft, "Imperial", "ft")
    assert abs(m - 6.096) < 1e-6
    print("[OK] All self-tests passed.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    run_self_tests()

    # Validate before any output
    validate_model()

    output_directory = Path(__file__).resolve().parent
    diagram_path = output_directory / "cube_6m_structural_diagram_rev3.png"
    workbook_path = output_directory / "cube_6m_structure_rev3.xlsx"

    create_structural_diagram(diagram_path)
    create_workbook(workbook_path, diagram_path)

    print(f"[OK] Workbook created: {workbook_path}")
    print(f"[OK] Structural diagram created: {diagram_path}")
    print(f"[OK] Unit System: {ACTIVE_UNIT_SYSTEM}")
    print(f"[OK] Material: {get_material(DEFAULT_MATERIAL)['name']}")
    print(f"[OK] Column section: {COLUMN_SECTION}")
    print(f"[OK] Roof beam section: {ROOF_BEAM_SECTION}")
    print(f"[OK] Tie beam section: {TIE_BEAM_SECTION}")