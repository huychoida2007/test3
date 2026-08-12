"""
projection_math.py
--------------------
Module chứa các công thức toán học cho phép chiếu vật thể 3D lên màn hình 2D

Quy trình chiếu gồm 3 bước:
    Bước 1: world_to_obs()          - (x,y,z) -> (x0,y0,z0)   [Tọa độ mắt quan sát]
    Bước 2: project_perspective()   - (x0,y0,z0) -> (xE,yE)   [Phối cảnh]
            hoặc project_parallel() - (x0,y0,z0) -> (xE,yE)   [Song song]
    Bước 3: to_canvas_coords()      - (xE,yE) -> (Canvas_X, Canvas_Y)
"""

import math


def world_to_obs(x, y, z, theta_deg, phi_deg, R):
    """
    BƯỚC 1: Chuyển từ Tọa độ thế giới (x, y, z) sang Tọa độ mắt quan sát (x0, y0, z0).

    Dựa trên ma trận biến đổi tổng quát T = A.B.C.D (Trang 81 Giáo trình):
        x0 = -x*sin(theta) + y*cos(theta)
        y0 = -x*cos(theta)*sin(phi) - y*sin(theta)*sin(phi) + z*cos(phi)
        z0 = -x*cos(theta)*cos(phi) - y*sin(theta)*cos(phi) - z*sin(phi) + R

    Tham số:
        x, y, z      : Tọa độ điểm trong không gian thế giới
        theta_deg    : Góc theta (độ) - góc quay quanh mặt phẳng XY
        phi_deg      : Góc phi (độ)   - góc quay lên xuống
        R            : Khoảng cách từ gốc O đến gốc hệ quan sát O'

    Trả về: (x0, y0, z0) - tọa độ điểm trong hệ quan sát.
    """
    # Đổi góc từ độ sang radian trước khi tính sin, cos (bắt buộc theo yêu cầu)
    theta = math.radians(theta_deg)
    phi = math.radians(phi_deg)

    sin_t, cos_t = math.sin(theta), math.cos(theta)
    sin_p, cos_p = math.sin(phi), math.cos(phi)

    x0 = -x * sin_t + y * cos_t
    y0 = -x * cos_t * sin_p - y * sin_t * sin_p + z * cos_p
    z0 = -x * cos_t * cos_p - y * sin_t * cos_p - z * sin_p + R

    return x0, y0, z0


def project_perspective(x0, y0, z0, D):
    """
    BƯỚC 2 (Phép chiếu Phối cảnh - Perspective - Mục 6.3.1, Trang 81):
        xE = D * (x0 / z0)
        yE = D * (y0 / z0)

    Có kiểm tra an toàn Clipping: nếu z0 <= 0.1 thì gán z0 = 0.1
    để tránh lỗi chia cho 0 (ZeroDivisionError).

    Tham số:
        x0, y0, z0 : Tọa độ điểm trong hệ quan sát
        D          : Khoảng cách từ mặt phẳng quan sát đến mắt (tâm chiếu)

    Trả về: (xE, yE) - tọa độ điểm trên mặt phẳng chiếu (màn hình logic).
    """
    z0 = max(0.1, z0)  # Clipping an toàn, tránh chia cho 0 hoặc số âm gây lật ảnh

    xE = D * (x0 / z0)
    yE = D * (y0 / z0)
    return xE, yE


def project_parallel(x0, y0, z0):
    """
    BƯỚC 2 (Phép chiếu Song song - Parallel - Mục 6.3.2, Trang 81):
        xE = x0
        yE = y0

    Lưu ý: Phép chiếu song song KHÔNG nhân với D theo đúng giáo trình
    (vì tâm chiếu đặt ở vô cực nên ảnh không bị thu phóng theo phối cảnh).

    Trả về: (xE, yE) - tọa độ điểm trên mặt phẳng chiếu.
    """
    xE = x0
    yE = y0
    return xE, yE


def to_canvas_coords(xE, yE, center_x, center_y):
    """
    BƯỚC 3: Quy đổi tọa độ chiếu (xE, yE) sang tọa độ vẽ trên Canvas Tkinter
    (Mục 6.4, Trang 83):
        Canvas_X = Center_X + round(xE)
        Canvas_Y = Center_Y - round(yE)

    Lưu ý: Trục Y bị lật ngược (dùng dấu trừ) vì hệ tọa độ màn hình máy tính
    có gốc ở góc trên-trái và trục Y hướng xuống dưới, ngược với hệ tọa độ
    toán học thông thường (trục Y hướng lên trên).

    Trả về: (canvas_x, canvas_y) - tọa độ nguyên để vẽ trên Canvas.
    """
    canvas_x = center_x + round(xE)
    canvas_y = center_y - round(yE)
    return canvas_x, canvas_y