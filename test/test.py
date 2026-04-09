import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

class VZ:
    def __init__(self, v, z):
        self.v = v
        self.z = z

def cubic_bezier(p0, p1, p2, p3, t):
    """
    三次贝塞尔曲线
    B(t) = (1-t)^3 * P0 + 3*(1-t)^2*t * P1 + 3*(1-t)*t^2 * P2 + t^3 * P3
    """
    t = np.asarray(t)
    result_v = (1-t)**3 * p0.v + 3*(1-t)**2 * t * p1.v + 3*(1-t)*t**2 * p2.v + t**3 * p3.v
    result_z = (1-t)**3 * p0.z + 3*(1-t)**2 * t * p1.z + 3*(1-t)*t**2 * p2.z + t**3 * p3.z
    return result_v, result_z

def cubic_bezier_derivative(p0, p1, p2, p3, t):
    """
    三次贝塞尔曲线的一阶导数
    B'(t) = 3*(1-t)^2*(P1-P0) + 6*(1-t)*t*(P2-P1) + 3*t^2*(P3-P2)
    """
    t = np.asarray(t)
    deriv_v = 3*(1-t)**2 * (p1.v - p0.v) + 6*(1-t)*t * (p2.v - p1.v) + 3*t**2 * (p3.v - p2.v)
    deriv_z = 3*(1-t)**2 * (p1.z - p0.z) + 6*(1-t)*t * (p2.z - p1.z) + 3*t**2 * (p3.z - p2.z)
    return deriv_v, deriv_z

def draw_apple():
    """
    绘制苹果的3D表面图
    使用分段三次贝塞尔曲线进行插值，确保G1连续（光滑）
    """
    r = 1
    r_width_ratio = 0.9
    h = 2 * r
    r_width = r * r_width_ratio
    deep_length = r / 4
    top_length = r / 2
    deep_v = -np.pi / 7
    top_v = np.pi / 5
    max_width_height_ratio = 0.55
    max_width_height = h * max_width_height_ratio

    # 数据点（端点）
    p0 = VZ(-np.pi/2, -r + deep_length)
    p1 = VZ(deep_v, -r)
    p2 = VZ(np.arctan((max_width_height - r) / r_width), max_width_height - r)
    p3 = VZ(top_v, max_width_height)
    p4 = VZ(np.pi/2, max_width_height - top_length)

    # =====================================================
    # G1连续性修复：确保相邻曲线段在接点处切线共线
    # =====================================================

    # 思路：先计算各段在端点处应有的切线方向，然后反推控制点位置

    # 切线方向计算（基于相邻数据点的方向）
    # t0_vec: p0→p1的方向
    t01_v = p1.v - p0.v
    t01_z = p1.z - p0.z

    # t1_vec: p1→p2的方向
    t12_v = p2.v - p1.v
    t12_z = p2.z - p1.z

    # t2_vec: p2→p3的方向
    t23_v = p3.v - p2.v
    t23_z = p3.z - p2.z

    # t3_vec: p3→p4的方向
    t34_v = p4.v - p3.v
    t34_z = p4.z - p3.z

    # 张力参数（控制切线长度，即曲线的"软硬"）
    tension = 0.3

    # P0处：切线为0（水平）- 因为端点
    # P1处：两端切线方向 = p1→p2 的方向（使其通过p1和p2之间的中点）
    # P2处：两端切线方向 = p2→p3 的方向
    # P3处：两端切线方向 = p3→p4 的方向
    # P4处：切线为0（水平）- 因为端点

    # 控制点计算：
    # 对于段0 (p0→p1): CP1 = p0 + tension * t01_vec
    # 对于段1 (p1→p2): CP1 = p1 + tension * t12_vec, CP2 = p2 - tension * t12_vec
    # 对于段2 (p2→p3): CP1 = p2 + tension * t23_vec, CP2 = p3 - tension * t23_vec
    # 对于段3 (p3→p4): CP2 = p4 - tension * t34_vec

    cp0 = VZ(p0.v + tension * t01_v, p0.z + tension * t01_z)
    cp1_in = VZ(p1.v + tension * t12_v, p1.z + tension * t12_z)  # 段1的入口控制点
    cp1_out = VZ(p1.v - tension * t12_v, p1.z - tension * t12_z)  # 段0的出口控制点
    cp2_in = VZ(p2.v + tension * t23_v, p2.z + tension * t23_z)  # 段2的入口控制点
    cp2_out = VZ(p2.v - tension * t23_v, p2.z - tension * t23_z)  # 段1的出口控制点
    cp3_in = VZ(p3.v + tension * t34_v, p3.z + tension * t34_z)  # 段3的入口控制点
    cp3_out = VZ(p3.v - tension * t34_v, p3.z - tension * t34_z)  # 段2的出口控制点
    cp4 = VZ(p4.v - tension * t34_v, p4.z - tension * t34_z)

    # 定义4段贝塞尔曲线（确保G1连续）
    segments = [
        (p0, cp0, cp1_out, p1),       # 段0: p0 → p1
        (p1, cp1_in, cp2_out, p2),    # 段1: p1 → p2
        (p2, cp2_in, cp3_out, p3),    # 段2: p2 → p3
        (p3, cp3_in, cp4, p4),        # 段3: p3 → p4
    ]

    # 生成用于绘图的密集点
    V_plot = np.linspace(-np.pi/2, np.pi/2, 200)
    Z_interp = []

    for v in V_plot:
        Z_val = None
        for i, seg in enumerate(segments):
            v_start = seg[0].v
            v_end = seg[3].v

            if i == 0 and v <= v_end:
                t = (v - v_start) / (v_end - v_start) if v_end != v_start else 0
                if 0 <= t <= 1:
                    _, z = cubic_bezier(seg[0], seg[1], seg[2], seg[3], [t])
                    Z_val = z[0]
                    break
            elif i > 0 and v >= segments[i-1][3].v and v <= v_end:
                t = (v - v_start) / (v_end - v_start) if v_end != v_start else 0
                if 0 <= t <= 1:
                    _, z = cubic_bezier(seg[0], seg[1], seg[2], seg[3], [t])
                    Z_val = z[0]
                    break

        if Z_val is None:
            Z_val = Z_interp[-1] if Z_interp else 0
        Z_interp.append(Z_val)

    Z_interp = np.array(Z_interp)

    # ──────────────────────────────────────────────
    # 1. Z关于V的剖面曲线图
    # ──────────────────────────────────────────────
    fig_profile, (ax_zv, ax_dzv) = plt.subplots(1, 2, figsize=(14, 5))

    # Z关于V的曲线
    ax_zv.plot(V_plot, Z_interp, 'b-', linewidth=2.5, label='Cubic Bezier (G1 Continuous)')
    ax_zv.scatter([p.v for p in [p0, p1, p2, p3, p4]], [p.z for p in [p0, p1, p2, p3, p4]],
                   c='red', s=80, zorder=5, label='Data Points', edgecolors='darkred')

    # 绘制控制点和控制线
    control_pts = [cp0, cp1_out, cp1_in, cp2_out, cp2_in, cp3_out, cp3_in, cp4]
    ax_zv.scatter([cp.v for cp in control_pts], [cp.z for cp in control_pts],
                   c='green', s=60, zorder=5, marker='x', label='Control Points')

    # 绘制控制多边形
    for i, seg in enumerate(segments):
        ax_zv.plot([seg[0].v, seg[1].v], [seg[0].z, seg[1].z], 'g--', alpha=0.5, linewidth=1)
        ax_zv.plot([seg[1].v, seg[2].v], [seg[1].z, seg[2].z], 'g--', alpha=0.5, linewidth=1)
        ax_zv.plot([seg[2].v, seg[3].v], [seg[2].z, seg[3].z], 'g--', alpha=0.5, linewidth=1)

    ax_zv.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Z=0')
    ax_zv.axvline(x=-np.pi/2, color='green', linestyle=':', alpha=0.7)
    ax_zv.axvline(x=np.pi/2, color='green', linestyle=':', alpha=0.7)
    ax_zv.set_xlabel('V (Latitude Angle)', fontsize=12)
    ax_zv.set_ylabel('Z (Height)', fontsize=12)
    ax_zv.set_title('Apple Profile: Z(V) - Cubic Bezier with G1 Continuity', fontsize=14, fontweight='bold')
    ax_zv.legend(loc='upper left', fontsize=7)
    ax_zv.grid(True, alpha=0.3)

    # 标注关键点
    for i, p in enumerate([p0, p1, p2, p3, p4]):
        ax_zv.annotate(f'P{i}', (p.v, p.z), textcoords="offset points", xytext=(5, 5), fontsize=8)

    # 计算并绘制导数
    V_deriv = np.linspace(-np.pi/2, np.pi/2, 200)
    Z_deriv = []
    for v in V_deriv:
        Z_val = None
        for i, seg in enumerate(segments):
            v_start = seg[0].v
            v_end = seg[3].v

            if i == 0 and v <= v_end:
                t = (v - v_start) / (v_end - v_start) if v_end != v_start else 0
                if 0 <= t <= 1:
                    _, dz = cubic_bezier_derivative(seg[0], seg[1], seg[2], seg[3], [t])
                    Z_val = dz[0]
                    break
            elif i > 0 and v >= segments[i-1][3].v and v <= v_end:
                t = (v - v_start) / (v_end - v_start) if v_end != v_start else 0
                if 0 <= t <= 1:
                    _, dz = cubic_bezier_derivative(seg[0], seg[1], seg[2], seg[3], [t])
                    Z_val = dz[0]
                    break

        if Z_val is None:
            Z_val = 0
        Z_deriv.append(Z_val)

    Z_deriv = np.array(Z_deriv)

    ax_dzv.plot(V_deriv, Z_deriv, 'g-', linewidth=2.5, label="Z'(V) - First Derivative")
    ax_dzv.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Zero derivative')

    # 检查端点导数
    endpoint_deriv_start = Z_deriv[0]
    endpoint_deriv_end = Z_deriv[-1]
    ax_dzv.scatter([V_deriv[0], V_deriv[-1]], [endpoint_deriv_start, endpoint_deriv_end],
                   c='red', s=80, zorder=5, label=f'Endpoints: {endpoint_deriv_start:.2f}, {endpoint_deriv_end:.2f}')

    ax_dzv.set_xlabel('V (Latitude Angle)', fontsize=12)
    ax_dzv.set_ylabel("Z'(V)", fontsize=12)
    ax_dzv.set_title("Derivative Z'(V) - Checking Endpoint Slopes", fontsize=14, fontweight='bold')
    ax_dzv.legend(loc='upper right', fontsize=8)
    ax_dzv.grid(True, alpha=0.3)

    fig_profile.suptitle('Apple Profile: G1 Continuous Bezier Curves', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    # ──────────────────────────────────────────────
    # 2. 创建3D苹果表面
    # ──────────────────────────────────────────────

    # 为R定义类似的贝塞尔曲线
    R_p0 = VZ(-np.pi/2, 0)
    R_p1 = VZ(deep_v, r)
    R_p2 = VZ(np.arctan((max_width_height - r) / r_width), np.sqrt(max(0, r**2 - (max_width_height - r)**2)))
    R_p3 = VZ(top_v, 0.05)
    R_p4 = VZ(np.pi/2, 0)

    # R的切线方向
    R_t01_v = R_p1.v - R_p0.v
    R_t01_z = R_p1.z - R_p0.z
    R_t12_v = R_p2.v - R_p1.v
    R_t12_z = R_p2.z - R_p1.z
    R_t23_v = R_p3.v - R_p2.v
    R_t23_z = R_p3.z - R_p2.z
    R_t34_v = R_p4.v - R_p3.v
    R_t34_z = R_p4.z - R_p3.z

    R_cp0 = VZ(R_p0.v + tension * R_t01_v, R_p0.z + tension * R_t01_z)
    R_cp1_in = VZ(R_p1.v + tension * R_t12_v, R_p1.z + tension * R_t12_z)
    R_cp1_out = VZ(R_p1.v - tension * R_t12_v, R_p1.z - tension * R_t12_z)
    R_cp2_in = VZ(R_p2.v + tension * R_t23_v, R_p2.z + tension * R_t23_z)
    R_cp2_out = VZ(R_p2.v - tension * R_t23_v, R_p2.z - tension * R_t23_z)
    R_cp3_in = VZ(R_p3.v + tension * R_t34_v, R_p3.z + tension * R_t34_z)
    R_cp3_out = VZ(R_p3.v - tension * R_t34_v, R_p3.z - tension * R_t34_z)
    R_cp4 = VZ(R_p4.v - tension * R_t34_v, R_p4.z - tension * R_t34_z)

    R_segments = [
        (R_p0, R_cp0, R_cp1_out, R_p1),
        (R_p1, R_cp1_in, R_cp2_out, R_p2),
        (R_p2, R_cp2_in, R_cp3_out, R_p3),
        (R_p3, R_cp3_in, R_cp4, R_p4),
    ]

    # 生成R值
    def get_R_for_V(v):
        for i, seg in enumerate(R_segments):
            v_start = seg[0].v
            v_end = seg[3].v

            if i == 0 and v <= v_end:
                t = (v - v_start) / (v_end - v_start) if v_end != v_start else 0
                if 0 <= t <= 1:
                    r_val, _ = cubic_bezier(seg[0], seg[1], seg[2], seg[3], [t])
                    return r_val[0]
            elif i > 0 and v >= R_segments[i-1][3].v and v <= v_end:
                t = (v - v_start) / (v_end - v_start) if v_end != v_start else 0
                if 0 <= t <= 1:
                    r_val, _ = cubic_bezier(seg[0], seg[1], seg[2], seg[3], [t])
                    return r_val[0]
        return 0

    # 创建网格
    u = np.linspace(0, 2 * np.pi, 100)
    V_mesh = np.linspace(-np.pi / 2, np.pi / 2, 50)
    U, V_full = np.meshgrid(u, V_mesh)

    # 计算Z和R
    Z_full = np.zeros_like(V_full)
    R_full = np.cos(V_full)
    print(R_full.max(), R_full.min())
   
    # 转换为笛卡尔坐标
    X = R_full * np.cos(U)
    Y = R_full * np.sin(U)

    # ──────────────────────────────────────────────
    # 3. 创建3D可视化
    # ──────────────────────────────────────────────
    fig_3d, axes = plt.subplots(2, 2, figsize=(14, 12))

    # X=0截面 (YZ平面)
    ax1 = axes[0, 0]
    contour1 = ax1.contourf(Y, Z_full, X, levels=20, cmap='viridis')
    ax1.contour(Y, Z_full, X, levels=[0], colors='red', linewidths=2)
    ax1.set_xlabel('Y')
    ax1.set_ylabel('Z')
    ax1.set_title('X=0 Cross Section (YZ Plane)')
    ax1.set_aspect('equal')
    plt.colorbar(contour1, ax=ax1, label='X')

    # Y=0截面 (XZ平面)
    ax2 = axes[0, 1]
    contour2 = ax2.contourf(X, Z_full, Y, levels=20, cmap='viridis')
    ax2.contour(X, Z_full, Y, levels=[0], colors='red', linewidths=2)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Z')
    ax2.set_title('Y=0 Cross Section (XZ Plane)')
    ax2.set_aspect('equal')
    plt.colorbar(contour2, ax=ax2, label='Y')

    # Z=0截面 (XY平面)
    ax3 = axes[1, 0]
    z0_idx = np.argmin(np.abs(Z_full - 0), axis=0)
    z0_y = Y[z0_idx, :]
    z0_x = X[z0_idx, :]
    ax3.plot(z0_x, z0_y, 'r-', linewidth=2, label='Z=0 contour')
    ax3.scatter(0, 0, c='blue', s=100, marker='+', label='Origin')
    ax3.set_xlabel('X')
    ax3.set_ylabel('Y')
    ax3.set_title('Z=0 Cross Section (XY Plane)')
    ax3.set_aspect('equal')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim([-1.2, 1.2])
    ax3.set_ylim([-1.2, 1.2])

    # 3D视图
    ax4 = fig_3d.add_subplot(2, 2, 4, projection='3d')
    surf = ax4.plot_surface(X, Y, Z_full, cmap='viridis', alpha=0.7, edgecolor='none')
    ax4.contour(X, Y, Z_full, zdir='x', offset=-1.2, cmap='viridis', alpha=0.5)
    ax4.contour(X, Y, Z_full, zdir='y', offset=1.2, cmap='viridis', alpha=0.5)
    ax4.contour(X, Y, Z_full, zdir='z', offset=-1.2, cmap='viridis', alpha=0.5)
    ax4.set_xlabel('X')
    ax4.set_ylabel('Y')
    ax4.set_zlabel('Z')
    ax4.set_title('Apple 3D View')
    max_range = 1.2
    ax4.set_xlim([-max_range, max_range])
    ax4.set_ylim([-max_range, max_range])
    ax4.set_zlim([-max_range, max_range])

    fig_3d.suptitle('Apple 3D Surface - G1 Continuous Bezier', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return fig_profile, fig_3d

# 运行函数
if __name__ == "__main__":
    draw_apple()