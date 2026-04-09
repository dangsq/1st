"""
苹果剖面曲线和3D旋转可视化

这个脚本模拟Three.js的LatheGeometry原理，展示苹果从2D剖面曲线旋转生成3D形状的过程。
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

class AppleProfile:
    """苹果剖面曲线类，模拟Three.js中的实现"""
    
    def __init__(self):
        self.profile_points = 80  # 剖面曲线分辨率
        self.lathe_segments = 64  # 旋转分段数
        
    def apple_profile(self, t, params):
        """
        计算苹果剖面曲线
        
        Args:
            t: 参数，从0(底部)到1(顶部)
            params: 参数字典
        
        Returns:
            r: 距离Y轴的距离
        """
        R = params['baseRadius']
        
        # 腹部偏移 - 将最宽点向下移动
        belly_shift = params['belly'] * 0.35
        t_adjusted = t + belly_shift * np.sin(np.pi * t)
        
        # 基础形状 - sin^power 给出漂亮的圆形
        power = 0.55 + params['roundness'] * 0.45
        base = np.power(np.maximum(0, np.sin(np.pi * t_adjusted)), power)
        
        # 宽度缩放
        r = base * R * params['widthScale']
        
        # 苹果特征 - 在顶部和底部创建凹形"腰部"
        top_pinch = np.exp(-np.power((t - 0.92) / 0.12, 2)) * params['appleIdentity'] * 0.35
        bottom_pinch = np.exp(-np.power((t - 0.08) / 0.15, 2)) * params['appleIdentity'] * 0.2
        r *= (1 - top_pinch - bottom_pinch)
        
        # 顶部凹陷
        top_dimple = np.exp(-np.power((t - 1.0) / np.maximum(0.05, params['topDimpleRadius'] * 0.6), 2))
        r *= (1 - top_dimple * params['topDimpleDepth'] * 2.5)
        
        # 底部凹陷
        bottom_dimple = np.exp(-np.power(t / np.maximum(0.05, params['bottomDimpleRadius'] * 0.5), 2))
        r *= (1 - bottom_dimple * params['bottomDimpleDepth'] * 2.0)
        
        return np.maximum(0, r)
    
    def apple_height(self, params):
        """计算苹果高度"""
        return params['baseRadius'] * 2 * params['heightScale']
    
    def generate_profile(self, params):
        """生成剖面曲线点"""
        H = self.apple_height(params)
        points = []
        
        for i in range(self.profile_points + 1):
            t = i / self.profile_points  # 0 → 1, 底部到顶部
            r = self.apple_profile(t, params)
            y = -H / 2 + t * H
            points.append((r, y))
        
        return np.array(points)
    
    def generate_3d_surface(self, params):
        """生成3D旋转表面"""
        profile_points = self.generate_profile(params)
        
        # 生成旋转角度
        angles = np.linspace(0, 2 * np.pi, self.lathe_segments)
        
        # 创建3D网格
        X = np.zeros((len(angles), len(profile_points)))
        Y = np.zeros((len(angles), len(profile_points)))
        Z = np.zeros((len(angles), len(profile_points)))
        
        for i, angle in enumerate(angles):
            for j, (r, y) in enumerate(profile_points):
                X[i, j] = r * np.cos(angle)
                Y[i, j] = y
                Z[i, j] = r * np.sin(angle)
        
        return X, Y, Z

def plot_apple_analysis():
    """绘制苹果剖面分析和3D可视化"""
    
    # 默认参数
    default_params = {
        'baseRadius': 0.12,
        'heightScale': 1.02,
        'widthScale': 1,
        'roundness': 0.92,
        'appleIdentity': 0.2,
        'belly': 0.08,
        'topDimpleDepth': 0.02,
        'topDimpleRadius': 0.18,
        'bottomDimpleDepth': 0.012,
        'bottomDimpleRadius': 0.1
    }
    
    apple = AppleProfile()
    
    # 创建图形
    fig = plt.figure(figsize=(16, 10))
    
    # 1. 原始sin^power曲线分析
    ax1 = plt.subplot(2, 3, 1)
    t_values = np.linspace(0, 1, 100)
    
    # 不同power值的曲线
    powers = [0.55, 0.7, 0.85, 1.0]
    for power in powers:
        r_values = np.power(np.sin(np.pi * t_values), power)
        ax1.plot(t_values, r_values, label=f'power={power}')
    
    ax1.set_title('基础曲线: sin(πt)^power')
    ax1.set_xlabel('t (0=底部, 1=顶部)')
    ax1.set_ylabel('r (半径)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 当前苹果剖面曲线
    ax2 = plt.subplot(2, 3, 2)
    profile_points = apple.generate_profile(default_params)
    ax2.plot(profile_points[:, 1], profile_points[:, 0], 'b-', linewidth=2, label='当前剖面')
    ax2.set_title('当前苹果剖面曲线')
    ax2.set_xlabel('y (高度)')
    ax2.set_ylabel('r (半径)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. 改进的苹果剖面曲线建议
    ax3 = plt.subplot(2, 3, 3)
    
    # 当前曲线
    ax3.plot(profile_points[:, 1], profile_points[:, 0], 'b-', linewidth=2, label='当前曲线')
    
    # 改进建议：更自然的苹果形状
    def improved_apple_profile(t, params):
        R = params['baseRadius']
        
        # 使用更平滑的曲线，避免尖顶
        # 组合多个sin函数来创建更自然的形状
        base1 = np.sin(np.pi * t)
        base2 = np.sin(2 * np.pi * t) * 0.3  # 添加二次谐波
        
        # 更平缓的power函数
        power = 0.7 + params['roundness'] * 0.3
        combined = base1 + base2
        base = np.power(np.maximum(0, combined), power)
        
        r = base * R * params['widthScale']
        
        # 更自然的顶部和底部处理
        top_pinch = np.exp(-np.power((t - 0.85) / 0.2, 2)) * params['appleIdentity'] * 0.4
        bottom_pinch = np.exp(-np.power((t - 0.15) / 0.25, 2)) * params['appleIdentity'] * 0.3
        r *= (1 - top_pinch - bottom_pinch)
        
        return np.maximum(0, r)
    
    # 生成改进的剖面
    improved_points = []
    H = apple.apple_height(default_params)
    for i in range(apple.profile_points + 1):
        t = i / apple.profile_points
        r = improved_apple_profile(t, default_params)
        y = -H / 2 + t * H
        improved_points.append((r, y))
    
    improved_points = np.array(improved_points)
    ax3.plot(improved_points[:, 1], improved_points[:, 0], 'r--', linewidth=2, label='改进建议')
    
    ax3.set_title('改进的苹果剖面曲线')
    ax3.set_xlabel('y (高度)')
    ax3.set_ylabel('r (半径)')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. 3D旋转可视化 - 当前形状
    ax4 = plt.subplot(2, 3, 4, projection='3d')
    X, Y, Z = apple.generate_3d_surface(default_params)
    ax4.plot_surface(X, Y, Z, alpha=0.7, cmap='YlOrRd', edgecolor='none')
    ax4.set_title('当前苹果3D形状')
    ax4.set_xlabel('X')
    ax4.set_ylabel('Y')
    ax4.set_zlabel('Z')
    
    # 5. 3D旋转可视化 - 改进形状
    ax5 = plt.subplot(2, 3, 5, projection='3d')
    
    # 生成改进形状的3D表面
    improved_profile = improved_points
    angles = np.linspace(0, 2 * np.pi, apple.lathe_segments)
    X_imp = np.zeros((len(angles), len(improved_profile)))
    Y_imp = np.zeros((len(angles), len(improved_profile)))
    Z_imp = np.zeros((len(angles), len(improved_profile)))
    
    for i, angle in enumerate(angles):
        for j, (r, y) in enumerate(improved_profile):
            X_imp[i, j] = r * np.cos(angle)
            Y_imp[i, j] = y
            Z_imp[i, j] = r * np.sin(angle)
    
    ax5.plot_surface(X_imp, Y_imp, Z_imp, alpha=0.7, cmap='YlGn', edgecolor='none')
    ax5.set_title('改进苹果3D形状')
    ax5.set_xlabel('X')
    ax5.set_ylabel('Y')
    ax5.set_zlabel('Z')
    
    # 6. 旋转动画原理示意图
    ax6 = plt.subplot(2, 3, 6)
    
    # 显示旋转原理
    angles_demo = np.linspace(0, 2 * np.pi, 8)
    colors = plt.cm.viridis(np.linspace(0, 1, len(angles_demo)))
    
    for i, (angle, color) in enumerate(zip(angles_demo, colors)):
        x_rotated = profile_points[:, 0] * np.cos(angle)
        ax6.plot(x_rotated, profile_points[:, 1], color=color, alpha=0.7, 
                label=f'{int(np.degrees(angle))}°' if i % 2 == 0 else "")
    
    ax6.set_title('LatheGeometry旋转原理')
    ax6.set_xlabel('X')
    ax6.set_ylabel('Y')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def create_rotation_animation():
    """创建旋转动画展示LatheGeometry原理"""
    
    default_params = {
        'baseRadius': 0.12,
        'heightScale': 1.02,
        'widthScale': 1,
        'roundness': 0.92,
        'appleIdentity': 0.2,
        'belly': 0.08,
        'topDimpleDepth': 0.02,
        'topDimpleRadius': 0.18,
        'bottomDimpleDepth': 0.012,
        'bottomDimpleRadius': 0.1
    }
    
    apple = AppleProfile()
    profile_points = apple.generate_profile(default_params)
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    def animate(frame):
        ax.cla()
        
        # 当前旋转角度
        angle = frame * 2 * np.pi / 60
        
        # 绘制当前角度的剖面
        x_current = profile_points[:, 0] * np.cos(angle)
        z_current = profile_points[:, 0] * np.sin(angle)
        y_current = profile_points[:, 1]
        
        ax.plot(x_current, y_current, z_current, 'r-', linewidth=3, label='当前剖面')
        
        # 绘制已经旋转的部分
        angles_drawn = np.linspace(0, angle, 30)
        for a in angles_drawn:
            x_drawn = profile_points[:, 0] * np.cos(a)
            z_drawn = profile_points[:, 0] * np.sin(a)
            ax.plot(x_drawn, y_current, z_drawn, 'b-', alpha=0.1)
        
        # 设置坐标轴
        ax.set_xlim([-0.15, 0.15])
        ax.set_ylim([-0.15, 0.15])
        ax.set_zlim([-0.15, 0.15])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'LatheGeometry旋转原理 - 角度: {int(np.degrees(angle))}°')
        
        # 固定视角
        ax.view_init(elev=20, azim=frame * 6)
    
    ani = animation.FuncAnimation(fig, animate, frames=60, interval=50, repeat=True)
    
    plt.show()
    return ani

if __name__ == "__main__":
    print("苹果剖面曲线和3D旋转可视化")
    print("=" * 50)
    
    # 显示静态分析图
    plot_apple_analysis()
    
    # 询问用户是否要看动画
    response = input("\n是否要查看旋转动画？(y/n): ")
    if response.lower() == 'y':
        print("正在生成旋转动画...")
        create_rotation_animation()
    
    print("\n分析完成！")