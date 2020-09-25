# coding: utf-8
import numpy as np
import cv2
import random

from union_find import UnionFind

def create_bool_voxel(char_voxel):

    #if os.path.exists("boolean_voxel_sample.npy"):
    #    voxel = np.load("boolean_voxel_sample.npy")
    #    return voxel
    voxel = np.zeros(char_voxel.shape, dtype=bool)
    for i in range(1,char_voxel.shape[0]):
        #filename = "../../../summercamp_data/Problem01/Problem01_{:04}.bmp".format(i)
        if i % 10 == 0:
            print(i)
        img = char_voxel[i,:,:]#cv2.imread(filename)
        edge = cv2.Canny(img,3,12)
        voxel[i,:,:] = (edge != 0)
    voxel[0,:,:]=False
    voxel[:,0,:]=False
    voxel[:,:,0]=False
    voxel[char_voxel.shape[0]-1,:,:]=False
    voxel[:,char_voxel.shape[1]-1,:]=False
    voxel[:,:,char_voxel.shape[2]-1]=False
    #np.save("boolean_voxel_sample", voxel)
    return voxel

def create_bool_voxel_d2(char_voxel):

    #if os.path.exists("boolean_voxel_sample.npy"):
    #    voxel = np.load("boolean_voxel_sample.npy")
    #    return voxel
    voxel_xy = np.zeros(char_voxel.shape, dtype=bool)
    voxel_xz = np.zeros(char_voxel.shape, dtype=bool)
    for i in range(1,char_voxel.shape[0]):
        #filename = "../../../summercamp_data/Problem01/Problem01_{:04}.bmp".format(i)
        if i % 10 == 0:
            print(i)
        img = char_voxel[i,:,:]#cv2.imread(filename)
        edge = cv2.Canny(img,3,12)
        voxel_xy[i,:,:] = (edge != 0)
    for i in range(1,char_voxel.shape[1]):
        #filename = "../../../summercamp_data/Problem01/Problem01_{:04}.bmp".format(i)
        if i % 10 == 0:
            print(i)
        img = char_voxel[:,i,:]#cv2.imread(filename)
        edge = cv2.Canny(img,3,12)
        voxel_xz[:,i,:] = (edge != 0)
    voxel = voxel_xy | voxel_xz
    voxel[0,:,:]=False
    voxel[:,0,:]=False
    voxel[:,:,0]=False
    voxel[char_voxel.shape[0]-1,:,:]=False
    voxel[:,char_voxel.shape[1]-1,:]=False
    voxel[:,:,char_voxel.shape[2]-1]=False
    np.save("boolean_voxel_sample", voxel)
    return voxel

def get_normals(char_voxel, targets):
    target_length = targets.shape[0]
    wei = [1,2,1,2,4,2,1,2,1]
    p1 = [-1,0,1,-1,0,1,-1,0,1]
    p2 = [-1,-1,-1,0,0,0,1,1,1]
    sobel = np.zeros((target_length, 3), np.float32)
    tx = targets[:,0]
    ty = targets[:,1]
    tz = targets[:,2]

    for i in range(9):
        sobel[:, 0] += (char_voxel[tx+1, ty+p1[i], tz+p2[i]] - char_voxel[tx-1, ty+p1[i], tz+p2[i]]) * wei[i]
        sobel[:, 1] += (char_voxel[tx+p1[i], ty+1, tz+p2[i]] - char_voxel[tx+p1[i], ty-1, tz+p2[i]]) * wei[i]
        sobel[:, 2] += (char_voxel[tx+p2[i], ty+p1[i], tz+1] - char_voxel[tx+p2[i], ty+p1[i], tz-1]) * wei[i]
    length = np.sqrt(sobel[:,0]*sobel[:,0] + sobel[:,1]*sobel[:,1] + sobel[:,2]*sobel[:,2])
    length[length<=0.00001]=1.0
    normals = np.zeros((target_length, 3), np.float32)
    normals[:,0] = sobel[:,0]/length
    normals[:,1] = sobel[:,1]/length
    normals[:,2] = sobel[:,2]/length
    return normals
def get_normal(char_voxel, x,y,z):
    if x<2 or y<2 or z<2 or x > char_voxel.shape[0]-3 or y > char_voxel.shape[1]-3 or z > char_voxel.shape[2]-3:
        return np.array([0.5,0.5,0.5])
    gaus = [[1,2,1],[2,4,2],[1,2,1]]
    dx = np.average(char_voxel[x+1,y-1:y+2,z-1:z+2],weights = gaus) - np.average(char_voxel[x-1,y-1:y+2,z-1:z+2],weights = gaus)
    dy = np.average(char_voxel[x-1:x+2,y+1,z-1:z+2],weights = gaus) - np.average(char_voxel[x-1:x+2,y-1,z-1:z+2],weights = gaus)
    dz = np.average(char_voxel[x-1:x+2,y-1:y+2,z+1],weights = gaus) - np.average(char_voxel[x-1:x+2,y-1:y+2,z-1],weights = gaus)
    length = np.sqrt(dx*dx+dy*dy+dz*dz)
    if length<=0.000000001:
        return np.array([0.5,0.5,0.5])
    return np.array([0.5 + 0.5*dx/length,0.5 + 0.5*dy/length,0.5 + 0.5*dz/length])

def labeling(char_voxel, bool_voxel):
    # labeling target is boundary voxels
    bool_voxel[0,:,:]=False
    bool_voxel[:,0,:]=False
    bool_voxel[:,:,0]=False
    bool_voxel[bool_voxel.shape[0]-1,:,:]=False
    bool_voxel[:,bool_voxel.shape[1]-1,:]=False
    bool_voxel[:,:,bool_voxel.shape[2]-1]=False
    nonzero = np.nonzero(bool_voxel)
    targets = np.array(nonzero).transpose()
    normals = get_normals(char_voxel, targets)
    vnm = np.zeros((char_voxel.shape[0],char_voxel.shape[1],char_voxel.shape[2],3), dtype=np.float32)
    idx = np.zeros(char_voxel.shape, dtype=np.int32)
    labels = np.full(char_voxel.shape, -1, dtype=np.int32)
    target_length = targets.shape[0]
    uf = UnionFind(target_length+1)
    # connection kernel(3x3)
    p0 = [-1,-1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0]
    p1 = [-1,-1,-1,0,0,0,1,1,1,-1,-1,-1,0]
    p2 = [-1,0,1,-1,0,1,-1,0,1,-1,0,1,-1]
    # connection kernel(2x2)
    q1 = [-1,-1,-1,0,0]
    q2 = [-1,0, 1,-1,0]

    arr = np.arange(target_length) + 1
    print(idx[nonzero].shape)
    idx[nonzero] = arr
    vnm[nonzero] = normals
    #search area size
    ss = [char_voxel.shape[0]-2, char_voxel.shape[1]-2, char_voxel.shape[2]-2]
    for i in range(13):
        print("step:{}".format(i))
        v1 = idx[1:1+ss[0], 1:1+ss[1], 1:1+ss[2]]
        v2 = idx[1+p0[i]:1+p0[i]+ss[0], 1+p1[i]:1+p1[i]+ss[1], 1+p2[i]:1+p2[i]+ss[2]]
        do = np.sum(vnm[1:1+ss[0], 1:1+ss[1], 1:1+ss[2]] * vnm[1+p0[i]:1+p0[i]+ss[0], 1+p1[i]:1+p1[i]+ss[1], 1+p2[i]:1+p2[i]+ss[2]], 3)
        v3 = (do > 0.5)
        con = np.nonzero((v1!=0)&(v2!=0)&v3)
        conp = np.array(con)+1
        id1s = idx[tuple(conp.tolist())].tolist()
        conq = np.array(con)
        conq[0,:]+=p0[i]+1
        conq[1,:]+=p1[i]+1
        conq[2,:]+=p2[i]+1
        id2s = idx[tuple(conq.tolist())].tolist()

        ids = zip(id1s, id2s)
        print("connections: {}".format(conp.shape[1]))
        for id1, id2 in ids:
            if id1<=0 or id2 <= 0 or id1 >= target_length-1 or id2 >= target_length-1:
                print(id1,id2)
                continue
            uf.union(id1,id2)
    # labels lookup table
    lut = np.zeros(target_length+1, dtype=np.int32)
    lbl_max = 1
    for i in range(target_length):
        fi = uf.find(i)
        if fi == i and uf.count[i]>100:
            lut[i]=lbl_max
            lbl_max += 1
    print(np.nonzero(lut))
    print("label count: {}".format(lbl_max))
    for i in range(target_length):
        fi = uf.find(i+1)
        if lut[fi]!=0:
            labels[targets[i,0], targets[i,1], targets[i,2]] = lut[fi]
    return labels
# labeling from bool voxel
def labeling_bool(voxel):
    labels = np.full(voxel.shape, 0, dtype=np.int32)
    label_count = 1
    label_count_start = np.zeros(voxel.shape[0]+1, dtype=np.int32)
    kernel = np.ones((5,5),np.uint8)
    for i in range(voxel.shape[0]):
        label_count_start[i] = label_count
        opening = cv2.morphologyEx(voxel[i,:,:].astype(np.uint8), cv2.MORPH_OPEN, kernel)
        current_label_count, layer_label = cv2.connectedComponents(opening)
        lb = layer_label.astype(np.int32)
        lb[lb<0]=0
        lb[np.nonzero(lb)] += label_count
        labels[i,:,:] = np.copy(lb)
        label_count += current_label_count
    label_count_start[voxel.shape[0]] = label_count

    uf = UnionFind(label_count)
    for i in range(voxel.shape[0]-1):
        # put current and next layer labels
        lbp = labels[i,:,:]
        lbq = labels[i+1,:,:]
        for l in range(label_count_start[i], label_count_start[i+1]):
            lbp_match = (lbp==l)
            uf.count[l] = np.count_nonzero(lbp_match)

            # connected labels
            duplicate = lbq[np.nonzero(lbp_match * lbq)]
            label_connected = np.unique(duplicate)
            for lc in label_connected:
                if np.count_nonzero(duplicate == lc) > 10:
                    uf.union(l,lc)
    # labels lookup table
    lut = np.zeros(label_count, dtype=np.int32)
    lbl_max = 1
    for i in range(label_count):
        fi = uf.find(i)
        if fi == i and uf.count[i]>100:
            lut[i]=lbl_max
            lbl_max += 1
    print("label count: {}".format(lbl_max))

    for i in range(voxel.shape[0]-1):
        lb = labels[i,:,:]
        for l in range(label_count_start[i], label_count_start[i+1]):
            lb[lb==l] = lut[uf.find(l)]
    print("finish labeling")
    return labels
# wrapper for code joint
def labeling_module(char_voxel, edge_voxel, bool_voxel):
    labeling_bool(bool_voxel)
    #labeling(char_voxel, bool_voxel)
