"""
geometry_data.py
-----------------
Module định nghĩa dữ liệu hình học 3D dùng cho chương trình mô phỏng
phép chiếu 3D -> 2D (Chương 6 - Giáo trình Đồ họa máy tính - Phạm Anh Phương).

Nội dung:
    - class ToaDo3D  : Biểu diễn 1 điểm trong không gian (x, y, z)
    - class WireFrame : Biểu diễn mô hình khung dây
    - ham tao_khoi_lap_phuong() : Khởi tạo khối lập phương đơn vị tại gốc O
"""
import math


class ToaDo3D:
    """Lớp biểu diễn một điểm trong không gian 3 chiều (x, y, z)."""

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"ToaDo3D(x={self.x}, y={self.y}, z={self.z})"

class WireFrame:
    """
    Lớp biểu diễn mô hình khung dây (Wireframe) - đúng theo Mục 6.5 Giáo trình:
    Đối tượng 3D được mô tả bằng 2 danh sách:
        - Danh sách đỉnh: lưu tọa độ (x, y, z) của các đỉnh.
        - Danh sách cạnh: lưu chỉ số đỉnh đầu và đỉnh cuối của từng cạnh.
    """

    def __init__(self):
        self.dinh = []   # Danh sách các đỉnh (mỗi phần tử là 1 đối tượng ToaDo3D)
        self.canh = []   # Danh sách các cạnh (mỗi phần tử là tuple (i, j) chỉ số đỉnh)

    def them_dinh(self, x, y, z):
        """Thêm 1 đỉnh mới vào danh sách đỉnh."""
        self.dinh.append(ToaDo3D(x, y, z))

    def them_canh(self, i, j):
        """Thêm 1 cạnh nối đỉnh có chỉ số i và đỉnh có chỉ số j."""
        self.canh.append((i, j))

def tao_khoi_lap_phuong():
    """
    Khởi tạo Khối lập phương đơn vị (Unit Cube) đặt tại gốc O,
    đúng theo Mục 6.5 Giáo trình (Hình 6.12):

        P1(0,0,0), P2(0,1,0), P3(1,1,0), P4(1,0,0),
        P5(1,0,1), P6(0,0,1), P7(0,1,1), P8(1,1,1)

    Danh sách 12 cạnh nối các cặp chỉ số đỉnh (đánh số từ 0):
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,5), (1,6), (2,7), (3,4)

    Trả về: đối tượng WireFrame đã khởi tạo đầy đủ.
    """
    wf = WireFrame()

    # ---- Danh sách 8 đỉnh của khối lập phương (theo đúng thứ tự P1..P8) ----
    wf.them_dinh(0, 0, 0)  # P1 -> chỉ số 0
    wf.them_dinh(0, 1, 0)  # P2 -> chỉ số 1
    wf.them_dinh(1, 1, 0)  # P3 -> chỉ số 2
    wf.them_dinh(1, 0, 0)  # P4 -> chỉ số 3
    wf.them_dinh(1, 0, 1)  # P5 -> chỉ số 4
    wf.them_dinh(0, 0, 1)  # P6 -> chỉ số 5
    wf.them_dinh(0, 1, 1)  # P7 -> chỉ số 6
    wf.them_dinh(1, 1, 1)  # P8 -> chỉ số 7

    # ---- Danh sách 12 cạnh (nối theo chỉ số đỉnh, bắt đầu từ 0) ----
    ds_canh = [
        (0, 1), (1, 2), (2, 3), (3, 0),   # Mặt đáy P1-P2-P3-P4
        (4, 5), (5, 6), (6, 7), (7, 4),   # Mặt trên P5-P6-P7-P8
        (0, 5), (1, 6), (2, 7), (3, 4),   # Các cạnh đứng nối 2 mặt
    ]
    for (i, j) in ds_canh:
        wf.them_canh(i, j)

    return wf

def tao_hinh_chop_tu_giac():
    """Khởi tạo Hình chóp tứ giác đều đặt tại gốc O."""
    wf = WireFrame()
    # 4 đỉnh đáy (mặt z=0)
    wf.them_dinh(-0.8, -0.8, 0.0)  # P0
    wf.them_dinh(-0.8,  0.8, 0.0)  # P1
    wf.them_dinh( 0.8,  0.8, 0.0)  # P2
    wf.them_dinh( 0.8, -0.8, 0.0)  # P3
    # 1 đỉnh chóp (z=1.5)
    wf.them_dinh( 0.0,  0.0, 1.5)  # P4

    # 4 cạnh đáy + 4 cạnh bên
    ds_canh = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Đáy
        (0, 4), (1, 4), (2, 4), (3, 4)   # Các cạnh bên nối lên đỉnh
    ]
    for i, j in ds_canh:
        wf.them_canh(i, j)
    return wf

def tao_lang_tru_tam_giac():
    """Khởi tạo Hình lăng trụ tam giác đứng."""
    wf = WireFrame()
    # Đáy dưới (z=0)
    wf.them_dinh( 0.0,  1.0, 0.0)  # P0
    wf.them_dinh(-0.86, -0.5, 0.0) # P1
    wf.them_dinh( 0.86, -0.5, 0.0) # P2
    # Đáy trên (z=1.5)
    wf.them_dinh( 0.0,  1.0, 1.5)  # P3
    wf.them_dinh(-0.86, -0.5, 1.5) # P4
    wf.them_dinh( 0.86, -0.5, 1.5) # P5

    ds_canh = [
        (0, 1), (1, 2), (2, 0),  # Tam giác đáy dưới
        (3, 4), (4, 5), (5, 3),  # Tam giác đáy trên
        (0, 3), (1, 4), (2, 5)   # Các cạnh đứng
    ]
    for i, j in ds_canh:
        wf.them_canh(i, j)
    return wf

def tao_hinh_cau(r=1.2, stacks=8, slices=12):
    """
    Khởi tạo Mặt Cầu 3D (Wireframe Mesh) bằng phương trình tham số (Mục 6.6):
        x = r * cos(v) * cos(u)
        y = r * cos(v) * sin(u)
        z = r * sin(v)
    với u in [0, 2pi], v in [-pi/2, pi/2]
    """
    wf = WireFrame()
    
    # ---- 1. Tạo danh sách các đỉnh ----
    for i in range(stacks + 1):
        v = -math.pi / 2 + i * math.pi / stacks
        for j in range(slices):
            u = j * 2 * math.pi / slices
            x = r * math.cos(v) * math.cos(u)
            y = r * math.cos(v) * math.sin(u)
            z = r * math.sin(v)
            wf.them_dinh(x, y, z)

    # ---- 2. Nối các cạnh tạo lưới (Grid Mesh) ----
    for i in range(stacks):
        for j in range(slices):
            curr = i * slices + j
            next_j = i * slices + (j + 1) % slices
            below = (i + 1) * slices + j

            # Nối vĩ tuyến (vòng tròn ngang)
            wf.them_canh(curr, next_j)
            # Nối kinh tuyến (vòng tròn dọc)
            wf.them_canh(curr, below)

    return wf

def tao_hinh_chop_tam_giac():
    """Khởi tạo Hình chóp tam giác (Tứ diện / Tetrahedron) đặt tại gốc O."""
    wf = WireFrame()
    # 3 đỉnh đáy tam giác (mặt z=0)
    wf.them_dinh( 0.0,   1.0, 0.0)  # P0
    wf.them_dinh(-0.866, -0.5, 0.0)  # P1
    wf.them_dinh( 0.866, -0.5, 0.0)  # P2
    # 1 đỉnh chóp (z=1.5)
    wf.them_dinh( 0.0,   0.0, 1.5)  # P3

    # 3 cạnh đáy + 3 cạnh bên
    ds_canh = [
        (0, 1), (1, 2), (2, 0),  # Đáy tam giác
        (0, 3), (1, 3), (2, 3)   # Các cạnh bên nối lên đỉnh P3
    ]
    for i, j in ds_canh:
        wf.them_canh(i, j)
    return wf

def tao_hinh_xuyen(R_major=1.2, r_minor=0.5, rings=16, tube_sides=10):
    """
    Khởi tạo Hình Xuyến 3D (Torus Mesh) bằng phương trình tham số (Mục 6.6 - Trang 89):
        X = (R + a * cos(v)) * cos(u)
        Y = (R + a * cos(v)) * sin(u)
        Z = a * sin(v)
    với u, v chạy từ 0 đến 2*pi.
    """
    wf = WireFrame()

    # ---- 1. Tạo danh sách các đỉnh ----
    for i in range(rings):
        u = i * 2 * math.pi / rings
        for j in range(tube_sides):
            v = j * 2 * math.pi / tube_sides
            x = (R_major + r_minor * math.cos(v)) * math.cos(u)
            y = (R_major + r_minor * math.cos(v)) * math.sin(u)
            z = r_minor * math.sin(v)
            wf.them_dinh(x, y, z)

    # ---- 2. Tạo lưới cạnh đan khép kín ----
    for i in range(rings):
        next_i = (i + 1) % rings
        for j in range(tube_sides):
            next_j = (j + 1) % tube_sides

            curr = i * tube_sides + j
            ring_next = next_i * tube_sides + j
            tube_next = i * tube_sides + next_j

            # Nối vòng lớn (kinh tuyến)
            wf.them_canh(curr, ring_next)
            # Nối vòng nhỏ (vĩ tuyến)
            wf.them_canh(curr, tube_next)

    return wf

# Từ điển quản lý tất cả các hàm sinh vật thể
DANH_SACH_VAT_THE = {
    "Khối lập phương": tao_khoi_lap_phuong,
    "Hình chóp tứ giác": tao_hinh_chop_tu_giac,
    "Lăng trụ tam giác": tao_lang_tru_tam_giac,
    "Mặt cầu": tao_hinh_cau,
    "Hình chóp tam giác": tao_hinh_chop_tam_giac,
    "Hình xuyến": tao_hinh_xuyen
}