import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'

fig, ax = plt.subplots(figsize=(10, 8))

# Two microphones
mic_x = [-0.3, 0.3]
mic_y = [0, 0]
ax.plot(mic_x, mic_y, 'o', markersize=25, color='#2196F3', zorder=5)

# Mic labels
ax.text(-0.3, -0.13, 'Mic 1', fontsize=13, ha='center', fontweight='bold', color='#1565C0')
ax.text(0.3, -0.13, 'Mic 2', fontsize=13, ha='center', fontweight='bold', color='#1565C0')

# Distance d annotation
ax.annotate('', xy=(-0.3, -0.28), xytext=(0.3, -0.28),
            arrowprops=dict(arrowstyle='<->', color='#E65100', lw=2.5))
ax.text(0, -0.38, 'd = microphone spacing', fontsize=12, ha='center', color='#E65100', fontweight='bold')

theta = 30
theta_rad = np.radians(theta)

# Draw plane wavefronts
for i, offset in enumerate([-0.3, 0, 0.3]):
    cx = offset * np.sin(theta_rad)
    cy = 0.7 + offset * np.cos(theta_rad)
    perp_angle = theta_rad + np.pi/2
    line_len = 0.8
    x_start = cx - line_len/2 * np.cos(perp_angle)
    x_end = cx + line_len/2 * np.cos(perp_angle)
    y_start = cy - line_len/2 * np.sin(perp_angle)
    y_end = cy + line_len/2 * np.sin(perp_angle)
    alpha_val = 0.25 + (i + 1) * 0.18
    ax.plot([x_start, x_end], [y_start, y_end], '-', color='#9C27B0', lw=2.5, alpha=alpha_val)

# Wavefront label
ax.text(0.65, 0.95, 'wavefronts', fontsize=10, color='#9C27B0', fontstyle='italic')

# Source direction line
source_dist = 1.3
source_x = -source_dist * np.sin(theta_rad)
source_y = source_dist * np.cos(theta_rad)
ax.plot([source_x, 0], [source_y, 0], '-', color='#4CAF50', lw=2, alpha=0.7)

# Source marker
ax.plot(source_x, source_y, '*', markersize=35, color='#FF5722', zorder=6)
ax.text(source_x-0.2, source_y+0.08, 'Sound\nSource', fontsize=12, fontweight='bold', color='#BF360C', ha='center')

# Extra path d*sin(theta)
ax.annotate('', xy=(0.12, 0.25), xytext=(-0.12, 0.25),
            arrowprops=dict(arrowstyle='<->', color='#D32F2F', lw=2.5))
ax.text(0, 0.38, 'd * sin(θ)\n(extra path)', fontsize=11, ha='center', color='#D32F2F', fontweight='bold')

# Draw theta arc
arc_radius = 0.35
arc_angles = np.linspace(0, theta_rad, 50)
arc_x = arc_radius * np.sin(arc_angles)
arc_y = arc_radius * np.cos(arc_angles)
ax.plot(arc_x, arc_y, '-', color='#1A237E', lw=3, zorder=7)

# Theta label
th_x = arc_radius * 0.6 * np.sin(theta_rad/2)
th_y = arc_radius * 0.6 * np.cos(theta_rad/2)
ax.text(th_x-0.06, th_y+0.01, 'θ', fontsize=20, fontweight='bold', color='#1A237E')

# Horizontal reference line
ax.plot([-0.4, 0.4], [0, 0], '-.', color='#BDBDBD', lw=1.5, alpha=0.6)
ax.text(0.42, 0.02, 'array axis', fontsize=9, color='#BDBDBD', fontstyle='italic')

# Key formula box
bbox_text = (
    "Key Geometry\n\n"
    "Mic 2 hears the sound later by:\n"
    "  extra distance = d * sin(θ)\n\n"
    "Time delay τ = d * sin(θ) / c\n"
    "Phase diff Δφ = 2πf * τ\n\n"
    "θ = 0° (front):    τ = 0, same time\n"
    "θ = 90° (side):   τ = d/c, max delay"
)
ax.text(0.72, 0.95, bbox_text, fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='#F5F5F5', edgecolor='#BDBDBD', alpha=0.9),
        transform=ax.transAxes)

# Direction arrow labels
ax.annotate('', xy=(-0.05, 0.55), xytext=(-0.05, 0.85),
            arrowprops=dict(arrowstyle='->', color='#4CAF50', lw=2))
ax.text(-0.12, 0.7, 'propagation\ndirection', fontsize=10, color='#4CAF50', fontweight='bold',
        rotation=90, ha='center', va='center')

ax.set_xlim(-1.2, 1.5)
ax.set_ylim(-0.5, 1.5)
ax.set_aspect('equal')
ax.axis('off')

plt.suptitle('What is θ?  -- Angle of Arrival', fontsize=18, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('F:\\paper\\work!\\outputs\\figures\\tdoa_theta_diagram.png', dpi=200, bbox_inches='tight')
plt.close()
print("done")
