# u = np.linspace(0, 2 * np.pi, 100)
# v = np.linspace(-np.pi / 2, np.pi / 2, 50)
# draw a sphere
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
# DEFINE
scale = 1.0
height = 1.0 # [0.9,1,1]
width = 1.0 # [0.9,1,1]
bottum_z = -height/2
bottum_z_r = 0.3 # [0.1,0.5]
bottom_depth = 0.1 # [0.05,0.2]
max_with_height = 0.55 # [0.5,0.6]
top_z = height 
top_z_r = 0.3 # [0.1,0.5] #
top_depth = 0.1 # [0.05,0.2]
cubic_ratio = 0.3
# some fixed points [V, Z, R]
p1 = [-np.pi/2, bottum_z+bottom_depth, 0]
p2 = [np.arctan(-height/2/bottum_z_r), bottum_z, bottum_z_r]
p3 = [np.arctan((max_with_height-height/2)/(width/2)), max_with_height-height/2,width/2 ]
p4 = [np.arctan((top_z-height/2)/(width/2)), top_z+bottum_z,top_z_r]
p5 = [np.pi/2, top_z-top_depth+bottum_z, 0]

# fit vz 
# [p1.v-0.05,p1.z+0.1] p1 p2 control point = [(p1.v+p2.v)/2, bottum_z]
# [(p2.v-p1.v)/2+p2.v, bottum_z] p2 p3 [p3.v-0.01,p3.z-0.1]
# [p3.v+0.01,p3.z+0.1] p3 p4 [-(p5.v-p4.v)/2+p4.v, p4.z]
# [(p5.v-p4.v)/2+p4.v, p4.z] p4 p5 [p5.v-0.05,p5.z-0.1]
def compute_intersect(x1,y1,x2,y2,xn1,yn1,xn2,yn2):
    # x1,y1 是第一条直线上的点，xn1,yn1 是第一条直线的法向量
    # x2,y2 是第二条直线上的点，xn2,yn2 是第二条直线的法向量
    # 直线1: (x - x1) * xn1 + (y - y1) * yn1 = 0  =>  xn1*x + yn1*y = xn1*x1 + yn1*y1
    # 直线2: (x - x2) * xn2 + (y - y2) * yn2 = 0  =>  xn2*x + yn2*y = xn2*x2 + yn2*y2
    
    # 使用克莱姆法则求解线性方程组
    # a1*x + b1*y = c1
    # a2*x + b2*y = c2
    a1, b1 = xn1, yn1
    c1 = xn1 * x1 + yn1 * y1
    
    a2, b2 = xn2, yn2
    c2 = xn2 * x2 + yn2 * y2
    
    # 计算行列式
    denom = a1 * b2 - a2 * b1
    
    # 如果分母接近0，说明两直线平行或重合
    if abs(denom) < 1e-10:
        return None
    
    # 计算交点
    intersect_x = (c1 * b2 - c2 * b1) / denom
    intersect_y = (a1 * c2 - a2 * c1) / denom
    
    return (intersect_x, intersect_y)
    
# 计算贝塞尔控制点
def calculate_bezier_control_points(points,mode = "z",cubic_ratio =cubic_ratio):
    if mode == "z":
        nys = [0.1,0.1,0,0.1,0.1]
        nxs = [-0.9,0.0,0.9,0.0,-0.9]
    elif mode == "r":
        nys = [0.1,1/(points[2][1]-points[0][1]),1,1/(points[4][1]-points[2][1]),0.1]
        nxs = [-0.9,-1/(points[2][0]-points[0][0]),0.0,-1/(points[4][0]-points[2][0]),-0.9]
        print(nxs,nys)
    if 1:
        ins = compute_intersect(points[0][0],points[0][1],points[1][0],points[1][1],nxs[0],nys[0],nxs[1],nys[1])
        cp1 = [(ins[0]-points[0][0])*cubic_ratio+points[0][0], (ins[1]-points[0][1])*cubic_ratio+points[0][1]]
        cp2 = [(ins[0]-points[1][0])*cubic_ratio+points[1][0], (ins[1]-points[1][1])*cubic_ratio+points[1][1]]
        control_points = [(cp1, cp2)]

        ins = compute_intersect(points[1][0],points[1][1],points[2][0],points[2][1],nxs[1],nys[1],nxs[2],nys[2])
        cp1 = [(ins[0]-points[1][0])*cubic_ratio+points[1][0], (ins[1]-points[1][1])*cubic_ratio+points[1][1]]
        cp2 = [(ins[0]-points[2][0])*cubic_ratio+points[2][0], (ins[1]-points[2][1])*cubic_ratio+points[2][1]]
        control_points.append((cp1, cp2))

        ins = compute_intersect(points[2][0],points[2][1],points[3][0],points[3][1],nxs[2],nys[2],nxs[3],nys[3])
        cp1 = [(ins[0]-points[2][0])*cubic_ratio+points[2][0], (ins[1]-points[2][1])*cubic_ratio+points[2][1]]
        cp2 = [(ins[0]-points[3][0])*cubic_ratio+points[3][0], (ins[1]-points[3][1])*cubic_ratio+points[3][1]]
        control_points.append((cp1, cp2))

        ins = compute_intersect(points[3][0],points[3][1],points[4][0],points[4][1],nxs[3],nys[3],nxs[4],nys[4])
        cp1 = [(ins[0]-points[3][0])*cubic_ratio+points[3][0], (ins[1]-points[3][1])*cubic_ratio+points[3][1]]
        cp2 = [(ins[0]-points[4][0])*cubic_ratio+points[4][0], (ins[1]-points[4][1])*cubic_ratio+points[4][1]]
        control_points.append((cp1, cp2))

        return control_points

def cubic_bezier(p0, p1, p2, p3, t):
    """三次贝塞尔曲线计算"""
    return (1-t)**3 * p0 + 3*(1-t)**2*t * p1 + 3*(1-t)*t**2 * p2 + t**3 * p3

def generate_bezier_curve(points, control_points, num_points=100):
    """生成贝塞尔曲线"""
    curve_v = []
    curve_val = []
    
    for i in range(len(points)-1):
        p0_v, p0_val = points[i][0], points[i][1]
        p1_v, p1_val = control_points[i][0][0], control_points[i][0][1]
        p2_v, p2_val = control_points[i][1][0], control_points[i][1][1]
        p3_v, p3_val = points[i+1][0], points[i+1][1]
        
        t_values = np.linspace(0, 1, num_points)
        segment_v = [cubic_bezier(p0_v, p1_v, p2_v, p3_v, t) for t in t_values]
        segment_val = [cubic_bezier(p0_val, p1_val, p2_val, p3_val, t) for t in t_values]
        
        curve_v.extend(segment_v)
        curve_val.extend(segment_val)
    
    return np.array(curve_v), np.array(curve_val)

# 计算控制点
vz_points = [[p[0], p[1]] for p in [p1, p2, p3, p4, p5]]
vr_points = [[p[0], p[2]] for p in [p1, p2, p3, p4, p5]]

vz_control_points = calculate_bezier_control_points(vz_points,mode = "z")
vr_control_points = calculate_bezier_control_points(vr_points,mode = "r")

# 生成贝塞尔曲线
bezier_v_vz, bezier_z = generate_bezier_curve(vz_points, vz_control_points)
bezier_v_vr, bezier_r = generate_bezier_curve(vr_points, vr_control_points)

# polt the VZ and VR
data = np.array([p1, p2, p3, p4, p5])
V, Z, R = data[:, 0], data[:, 1], data[:, 2]


# 根据V值插值获取R和Z值
def get_R_Z_from_bezier(v):
    """根据V值从贝塞尔曲线插值获取对应的R和Z值"""
    # 在V-Z贝塞尔曲线上找到最接近的V值
    idx_vz = np.argmin(np.abs(bezier_v_vz - v))
    z_val = bezier_z[idx_vz]
    
    # 在V-R贝塞尔曲线上找到最接近的V值
    idx_vr = np.argmin(np.abs(bezier_v_vr - v))
    r_val = bezier_r[idx_vr]
    
    return r_val, z_val

# 绘制3D曲面
U = np.linspace(0, 2 * np.pi, 100)
V_full = np.linspace(-np.pi / 2, np.pi / 2, 50)
U, V_full = np.meshgrid(U, V_full)

# 为每个V值计算对应的R和Z
R_full = np.zeros_like(V_full)
Z_full = np.zeros_like(V_full)

for i in range(V_full.shape[0]):
    for j in range(V_full.shape[1]):
        v_val = V_full[i, j]
        r_val, z_val = get_R_Z_from_bezier(v_val)
        R_full[i, j] = r_val
        Z_full[i, j] = z_val

# 计算X, Y坐标
X = R_full * np.cos(U)
Y = R_full * np.sin(U)

# 创建3D图形
fig3d = plt.figure(figsize=(10, 8))
ax3d = fig3d.add_subplot(111, projection='3d')

# 绘制3D曲面
surf = ax3d.plot_surface(X, Y, Z_full, alpha=0.8, cmap='viridis', edgecolor='none', linewidth=0.5)

# 设置坐标轴标签
ax3d.set_xlabel('X')
ax3d.set_ylabel('Y')
ax3d.set_zlabel('Z')
ax3d.set_title('3D Surface from Bézier Interpolation')

# 添加颜色条
fig3d.colorbar(surf, ax=ax3d, shrink=0.5, aspect=20)

plt.tight_layout()
plt.show()