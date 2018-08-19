import cv2
import bezier
import numpy as np
import math
import matplotlib.pyplot as plt

from pprint import pprint

_filterSize = 32

# TODO:制御点を動かす
def createFilter(n,ratio):
    _r = (_filterSize / 2 - 1)*ratio
    _center = (_filterSize / 2, _filterSize / 2)

    angle = 360 / n

    vertex_tmp = []
    # print(vertex_tmp)

    # 頂点と制御点生成
    for i in range(1, n + 1):
        x = _center[0] + _r * math.cos(math.radians(angle * i))
        y = _center[1] + _r * math.sin(math.radians(angle * i))
        controlPoint_x = _center[0] + _r * math.cos(math.radians(angle * i + angle / 2))
        controlPoint_y = _center[1] + _r * math.sin(math.radians(angle * i + angle / 2))

        # vertex = np.append(vertex,x)
        # vertex = np.append(vertex,y)
        # vertex = np.append(vertex,controlPoint_x)
        # vertex = np.append(vertex,controlPoint_y)
        vertex_tmp.extend([x, y, controlPoint_x, controlPoint_y])

    # print(vertex_tmp)
    vertex_tmp.extend(vertex_tmp[0:2])
    # print(vertex_tmp)
    vertex = np.ndarray((2, n * 2 + 1), dtype=np.float64)
    vertex[0] = vertex_tmp[0::2]
    vertex[1] = vertex_tmp[1::2]
    # pprint(vertex)



    # 補間
    points = np.array([])
    filterPoints = [];

    # python3のroundは特殊なので定義
    round = lambda x: int((x * 2 + 1) / 2)

    for i in range(0, 2*(n-1)+1, 2):
        # 0~1で座標値を計算
        node = np.ndarray((2, 3), dtype=np.float64)
        node[0] = vertex[0][i:i + 3]
        node[1] = vertex[1][i:i + 3]
        curve = bezier.Curve(node, degree=2)
        # 1.0が重複するけどスルー
        for n in [0.1 * x for x in range(10)]:
            point = curve.evaluate(n)
            # pprint(point)
            points = np.append(points, point)
            filterPoints.append([round(point[0][0]), round(point[1][0])])

    # matplotでのテスト
    # x = points[0::2]
    # y = points[1::2]
    #pprint(points)
    #print(len(points))
    # plt.plot(x,y)
    # plt.show()
    #pprint(filterPoints)

    np_filterPoints = np.array(filterPoints)
    #pprint(np_filterPoints)

    # 0埋めしたフィルター
    filter = np.zeros((_filterSize,_filterSize),np.uint8)
    cv2.fillConvexPoly(filter,np_filterPoints,(255))
    # cv2.imshow("filter",filter)
    # cv2.waitKey(0)
    # cv2.imwrite("./squareFilter.png",filter)

    return filter


if __name__ == "__main__":
    filterIMG = createFilter(4,1)
    # cv2.imshow("filter",filterIMG)
    #     # cv2.waitKey(0)