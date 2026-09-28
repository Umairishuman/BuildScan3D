import json
import numpy as np
import matplotlib.pyplot as plt
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=str, required=True, help="Path to transforms.json")
    args = parser.parse_args()

    with open(args.json, 'r') as f:
        data = json.load(f)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    positions = []
    
    for frame in data['frames']:
        c2w = np.array(frame['transform_matrix'])
        pos = c2w[:3, 3]
        positions.append(pos)
        
        # In OpenGL, the camera looks down the -Z axis.
        # We multiply by 0.1 to make the view direction line 10cm long
        z_dir = -c2w[:3, 2] * 0.1 
        
        # Plot view direction (Blue)
        ax.plot([pos[0], pos[0] + z_dir[0]], 
                [pos[1], pos[1] + z_dir[1]], 
                [pos[2], pos[2] + z_dir[2]], color='blue', alpha=0.7)
        
        # Plot camera center (Red)
        ax.scatter(pos[0], pos[1], pos[2], color='red', s=10)

    positions = np.array(positions)
    
    # Plot the full trajectory line
    ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], color='black', linestyle='--', alpha=0.5)

    # Set equal aspect ratio to prevent stretching
    max_range = np.array([positions[:,0].max()-positions[:,0].min(), 
                          positions[:,1].max()-positions[:,1].min(), 
                          positions[:,2].max()-positions[:,2].min()]).max() / 2.0
    
    mid_x = (positions[:,0].max()+positions[:,0].min()) * 0.5
    mid_y = (positions[:,1].max()+positions[:,1].min()) * 0.5
    mid_z = (positions[:,2].max()+positions[:,2].min()) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.set_zlabel('Z (meters)')
    ax.set_title('Camera Trajectory & View Directions (-Z)')
    plt.show()

if __name__ == '__main__':
    main()