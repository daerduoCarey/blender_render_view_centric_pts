import os
import numpy as np
from subprocess import call
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_pts(fn):
    with open(fn, 'r') as fin:
        lines = [item.rstrip() for item in fin]
        pts = np.array([[float(line.split()[0]), float(line.split()[1]), float(line.split()[2])] for line in lines], dtype=np.float32)
        return pts

def load_obj(fn, no_normal=False):
    fin = open(fn, 'r')
    lines = [line.rstrip() for line in fin]
    fin.close()

    vertices = []; normals = []; faces = [];
    for line in lines:
        if line.startswith('v '):
            vertices.append(np.float32(line.split()[1:4]))
        elif line.startswith('vn '):
            normals.append(np.float32(line.split()[1:4]))
        elif line.startswith('f '):
            faces.append(np.int32([item.split('/')[0] for item in line.split()[1:4]]))

    mesh = dict()
    mesh['faces'] = np.vstack(faces)
    mesh['vertices'] = np.vstack(vertices)

    if (not no_normal) and (len(normals) > 0):
        assert len(normals) == len(vertices), 'ERROR: #vertices != #normals'
        mesh['normals'] = np.vstack(normals)

    return mesh

cube_mesh = load_obj(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cube.obj'), no_normal=True)
cube_v = cube_mesh['vertices'] / 100
cube_f = cube_mesh['faces']

def render_pts(out_fn, pts):
    all_v = [np.zeros((0, 3), dtype=np.float32)]; 
    all_f = [np.zeros((0, 3), dtype=np.int32)];
    for i in range(pts.shape[0]):
        all_v.append(cube_v + pts[i])
        all_f.append(cube_f + 8 * i)
    all_v = np.vstack(all_v)
    all_f = np.vstack(all_f)
    with open(out_fn+'.obj', 'w') as fout:
        fout.write('mtllib %s\n' % (out_fn.split('/')[-1]+'.mtl'))
        for i in range(all_v.shape[0]):
            fout.write('v %f %f %f\n' % (all_v[i, 0], all_v[i, 1], all_v[i, 2]))
        fout.write('usemtl f0\n')
        for i in range(all_f.shape[0]):
            fout.write('f %d %d %d\n' % (all_f[i, 0], all_f[i, 1], all_f[i, 2]))
    with open(out_fn+'.mtl', 'w') as fout:
        fout.write('newmtl f0\nKd 1 0 0\n')
    cmd = 'cd %s && blender -noaudio --background blank.blend --python render_blender.py %s %s > /dev/null' \
            % (os.path.join(os.path.dirname(os.path.abspath(__file__))), \
            out_fn+'.obj', out_fn)
    call(cmd, shell=True)


def render_pts_with_label(out_fn, pts, label, color_map):
    all_f = dict();
    fmtl = open(out_fn + '.mtl', 'w')
    fobj = open(out_fn + '.obj', 'w')
    fobj.write('mtllib %s' % out_fn+'.mtl\n\n')
    for i in range(pts.shape[0]):
        if str(label[i]) not in all_f.keys():
            all_f[str(label[i])] = [np.zeros((0, 3), dtype=np.int32)]
        cur_v = cube_v + pts[i]
        for j in range(8):
            fobj.write('v %f %f %f\n' % (cur_v[j, 0], cur_v[j, 1], cur_v[j, 2]))
        all_f[str(label[i])].append(cube_f + 8 * i)
    for k in all_f.keys():
        f_arr = np.vstack(all_f[k])
        fmtl.write('newmtl label-%s\n' % k)
        c = color_map(int(k))
        fmtl.write('Kd %f %f %f\n\n' % (c[0], c[1], c[2]))
        fobj.write('\nusemtl label-%s\n' % k)
        for j in range(f_arr.shape[0]):
            fobj.write('f %d %d %d\n' % (f_arr[j, 0], f_arr[j, 1], f_arr[j, 2]))
    fmtl.close()
    fobj.close()
    cmd = 'cd %s && blender -noaudio --background blank.blend --python render_blender.py %s %s > /dev/null' \
            % (os.path.join(os.path.dirname(os.path.abspath(__file__))), \
            out_fn+'.obj', out_fn)
    call(cmd, shell=True)

# main
for item in os.listdir('.'):
    if item.endswith('.pts'):
        pts = load_pts(item)
        render_pts(item.replace('.pts', '.png'), pts)
