"""
main.py
--------
Chỉ sử dụng thư viện chuẩn: tkinter và math (thông qua projection_math).
Chạy trực tiếp bằng lệnh:  python main.py

Tác giả thực hiện: Hoàng Đình Quảng (Lunia)
"""

import tkinter as tk
from tkinter import ttk

from geometry_data import DANH_SACH_VAT_THE
from projection_math import (
    project_parallel,
    project_perspective,
    to_canvas_coords,
    world_to_obs,
)

# ==========================================================================
# ĐỊNH NGHĨA CÁC KỊCH BẢN (PRESET) GÓC NHÌN
# ==========================================================================
DANH_SACH_PRESET = {
    "1. Phối cảnh chuẩn": {
        "theta": 40,
        "phi": 20,
        "R": 15,
        "D": 150,
        "mode": "perspective",
    },
    "2. Song song chuẩn": {
        "theta": 40,
        "phi": 20,
        "R": 15,
        "D": 150,
        "mode": "parallel",
    },
    "3. Top View (Nhìn từ trên)": {"theta": 0, "phi": 90},
    "4. Bottom View (Nhìn từ dưới)": {"theta": 0, "phi": -90},
    "5. Front View (Nhìn chính diện)": {"theta": 0, "phi": 0},
    "6. Isometric View (Góc nghiêng 3D)": {"theta": 45, "phi": 35},
    "7. Zoom In Phối cảnh (Tăng D)": {
        "theta": 40,
        "phi": 20,
        "R": 15,     # Giữ R chuẩn
        "D": 350,    # Tăng D để phóng to
        "mode": "perspective",
    },
    "8. Quan sát xa Phối cảnh (Tăng R)": {
        "theta": 40,
        "phi": 20,
        "R": 30,     # Tăng R gấp đôi để lùi ra xa
        "D": 150,    # Giữ D chuẩn
        "mode": "perspective",
    },
}


class ProjectionApp:
    """Lớp chính dựng giao diện Tkinter, quản lý slider và vẽ hình chiếu 3D."""

    # ---- Màu sắc và hằng số giao diện ----
    MAU_NEN_CANVAS = "#1E1E1E"
    MAU_KHOI = "#FFD54A"  # Vàng - vẽ khối lập phương
    MAU_TIA_CHIEU = "#5A5A5A"  # Xám - nét đứt tia chiếu về gốc
    MAU_TRUC_X = "#E53935"  # Đỏ
    MAU_TRUC_Y = "#43A047"  # Xanh lá
    MAU_TRUC_Z = "#1E88E5"  # Xanh dương
    MAU_CHU = "#DDDDDD"
    ROONG_CONTROL = 280  # Chiều rộng cố định của Control Panel

    def __init__(self, root):
        self.root = root
        self.root.title(
            "3D Projection Simulation -  "
            "Dev: Hoàng Đình Quảng (Lunia)"
        )
        self.root.geometry("1000x680")
        self.root.minsize(760, 520)

        # ---- Dữ liệu hình học: Khởi tạo vật thể mặc định ----
        self.wireframe = DANH_SACH_VAT_THE["Khối lập phương"]()

        # ---- Các biến trạng thái tham số phép chiếu ----
        self.bien_vat_the = tk.StringVar(value="Khối lập phương")
        self.bien_theta = tk.DoubleVar(value=40)
        self.bien_phi = tk.DoubleVar(value=20)
        self.bien_R = tk.DoubleVar(value=15)
        self.bien_D = tk.DoubleVar(value=150)
        self.bien_mode = tk.StringVar(value="perspective")  # "perspective" | "parallel"

        # ---- Tâm màn hình Canvas ----
        self.center_x = 400
        self.center_y = 300

        self._dung_giao_dien()
        self._ve_lai()

    # ----------------------------------------------------------------
    # DỰNG GIAO DIỆN
    # ----------------------------------------------------------------
    def _dung_giao_dien(self):
        khung_chinh = tk.Frame(self.root, bg="#252525")
        khung_chinh.pack(fill=tk.BOTH, expand=True)

        # ---- Bảng điều khiển (Control Panel) ----
        khung_dieu_khien = tk.Frame(khung_chinh, width=self.ROONG_CONTROL, bg="#252525")
        khung_dieu_khien.pack(side=tk.LEFT, fill=tk.Y)
        khung_dieu_khien.pack_propagate(False)

        # ---- Khung chứa Canvas ----
        khung_canvas = tk.Frame(khung_chinh, bg=self.MAU_NEN_CANVAS)
        khung_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            khung_canvas, bg=self.MAU_NEN_CANVAS, highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._khi_resize_canvas)

        self._dung_control_panel(khung_dieu_khien)

    def _dung_control_panel(self, parent):
        tieu_de = tk.Label(
            parent,
            text="BẢNG ĐIỀU KHIỂN",
            font=("Segoe UI", 13, "bold"),
            fg="#FFFFFF",
            bg="#252525",
        )
        tieu_de.pack(pady=(14, 10))

        # ---- Combobox Chọn Vật Thể 3D ----
        khung_vat_the = tk.Frame(parent, bg="#252525")
        khung_vat_the.pack(fill=tk.X, padx=16, pady=(0, 10))
        tk.Label(
            khung_vat_the,
            text="Chọn Hình 3D Mô Phỏng:",
            fg="#CCCCCC",
            bg="#252525",
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill=tk.X)

        self.combobox_vat_the = ttk.Combobox(
            khung_vat_the,
            textvariable=self.bien_vat_the,
            values=list(DANH_SACH_VAT_THE.keys()),
            state="readonly",
        )
        self.combobox_vat_the.pack(fill=tk.X, pady=(4, 0))
        self.combobox_vat_the.bind("<<ComboboxSelected>>", self._doi_vat_the)

        # ---- Combobox Preset ----
        khung_preset = tk.Frame(parent, bg="#252525")
        khung_preset.pack(fill=tk.X, padx=16, pady=(0, 14))
        tk.Label(
            khung_preset,
            text="Demo Presets (Kịch bản góc nhìn):",
            fg="#CCCCCC",
            bg="#252525",
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill=tk.X)

        self.bien_preset = tk.StringVar()
        self.combobox_preset = ttk.Combobox(
            khung_preset,
            textvariable=self.bien_preset,
            values=list(DANH_SACH_PRESET.keys()),
            state="readonly",
        )
        self.combobox_preset.pack(fill=tk.X, pady=(4, 0))
        self.combobox_preset.bind("<<ComboboxSelected>>", self._ap_dung_preset)

        # ---- Các Slider ----
        self.scale_theta = self._tao_slider(
            parent, "Góc Theta (θ): 0° -> 360°", self.bien_theta, 0, 360
        )
        self.scale_phi = self._tao_slider(
            parent, "Góc Phi (Φ): -90° -> 90°", self.bien_phi, -90, 90
        )
        self.scale_R = self._tao_slider(
            parent, "Khoảng cách R: 1 -> 50", self.bien_R, 1, 50
        )
        self.scale_D = self._tao_slider(
            parent,
            "Khoảng cách D (Thu phóng phối cảnh): 50 -> 500",
            self.bien_D,
            50,
            500,
        )

        # ---- RadioButton chọn chế độ chiếu ----
        khung_mode = tk.LabelFrame(
            parent,
            text="Chế độ chiếu",
            fg="#FFFFFF",
            bg="#252525",
            font=("Segoe UI", 9, "bold"),
            labelanchor="n",
        )
        khung_mode.pack(fill=tk.X, padx=16, pady=(6, 14))

        tk.Radiobutton(
            khung_mode,
            text="Phép chiếu Phối cảnh",
            value="perspective",
            variable=self.bien_mode,
            command=self._ve_lai,
            fg="#EEEEEE",
            bg="#252525",
            selectcolor="#333333",
            activebackground="#252525",
            activeforeground="#FFFFFF",
            anchor="w",
        ).pack(fill=tk.X, padx=6, pady=2)

        tk.Radiobutton(
            khung_mode,
            text="Phép chiếu Song song",
            value="parallel",
            variable=self.bien_mode,
            command=self._ve_lai,
            fg="#EEEEEE",
            bg="#252525",
            selectcolor="#333333",
            activebackground="#252525",
            activeforeground="#FFFFFF",
            anchor="w",
        ).pack(fill=tk.X, padx=6, pady=2)

        # ---- Nhãn tác giả ----
        tk.Label(
            parent,
            text="Thực hiện: Hoàng Đình Quảng (Lunia)",
            fg="#888888",
            bg="#252525",
            font=("Segoe UI", 8, "italic"),
        ).pack(side=tk.BOTTOM, pady=10)

    def _tao_slider(self, parent, nhan, bien, tu, den):
        """
        Hàm phụ trợ tạo 1 slider có nhãn tiêu đề, real-time redraw.
        Có kèm 1 ô nhập số (Entry) bên phải nhãn để gõ trực tiếp giá trị
        chính xác, vì việc kéo chuột trên Scale nhiều lúc khó căn đúng
        số mong muốn (ví dụ Theta = 37.5°).

        LƯU Ý QUAN TRỌNG: Ô Entry KHÔNG được dùng chung trực tiếp biến
        DoubleVar với Scale. Nếu dùng chung, mỗi lần gõ 1 ký tự, Scale
        sẽ lập tức ép giá trị về đúng bước nhảy (resolution) hợp lệ và
        ghi đè ngược lại ô Entry ngay khi đang gõ dở, khiến không gõ
        được. Do đó Entry dùng 1 StringVar riêng (bien_hien_thi), chỉ
        đồng bộ NGƯỢC từ Scale -> Entry khi kéo, và chỉ đẩy XUÔI từ
        Entry -> Scale khi người dùng nhấn Enter (đã gõ xong).
        """
        khung = tk.Frame(parent, bg="#252525")
        khung.pack(fill=tk.X, padx=16, pady=(0, 10))

        # ---- Hàng nhãn + ô nhập số ----
        # Dùng grid thay vì pack: cột 0 (nhãn) được phép co giãn và tự
        # xuống dòng (wraplength) khi quá dài, cột 1 (ô nhập số) luôn
        # được ghim cố định bên phải, không bao giờ bị nhãn dài đè lên.
        khung_nhan = tk.Frame(khung, bg="#252525")
        khung_nhan.pack(fill=tk.X)
        khung_nhan.grid_columnconfigure(0, weight=1)

        tk.Label(
            khung_nhan,
            text=nhan,
            fg="#CCCCCC",
            bg="#252525",
            font=("Segoe UI", 9),
            anchor="w",
            justify=tk.LEFT,
            wraplength=170,  # Tự xuống dòng nếu nhãn dài (ví dụ nhãn của D)
        ).grid(row=0, column=0, sticky="w")

        # Biến hiển thị riêng cho ô nhập số (KHÔNG phải bien của Scale)
        bien_hien_thi = tk.StringVar(value=f"{bien.get():g}")

        o_nhap = tk.Entry(
            khung_nhan,
            width=6,
            justify="center",
            bg="#3A3A3A",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief=tk.FLAT,
            textvariable=bien_hien_thi,
        )
        o_nhap.grid(row=0, column=1, sticky="ne", padx=(6, 0))


        scale = tk.Scale(
            khung,
            from_=tu,
            to=den,
            orient=tk.HORIZONTAL,
            variable=bien,
            resolution=1,
            showvalue=False,  # Giá trị đã hiển thị trong ô nhập số ở trên
            bg="#252525",
            fg="#FFFFFF",
            troughcolor="#3A3A3A",
            highlightthickness=0,
            activebackground="#4CAF50",
            command=lambda _evt: self._ve_lai(),
        )
        scale.pack(fill=tk.X)

        # ---- Đồng bộ NGƯỢC: khi kéo Scale (hoặc set từ Preset) -> cập nhật ô nhập số ----
        def _dong_bo_o_nhap(*_args):
            bien_hien_thi.set(f"{bien.get():g}")

        bien.trace_add("write", _dong_bo_o_nhap)

        # ---- Xử lý khi người dùng gõ số xong và nhấn Enter (hoặc rời ô nhập) ----
        def _khi_nhap_gia_tri(event=None):
            try:
                gia_tri = float(o_nhap.get())
            except ValueError:
                # Gõ sai định dạng (không phải số) -> giữ nguyên giá trị cũ
                gia_tri = bien.get()

            # Kẹp giá trị trong khoảng [tu, den] để không vượt biên slider
            gia_tri = max(tu, min(den, gia_tri))

            bien.set(gia_tri)  # -> tự kích hoạt trace ở trên, cập nhật lại ô nhập
            self._ve_lai()

        o_nhap.bind("<Return>", _khi_nhap_gia_tri)
        o_nhap.bind("<FocusOut>", _khi_nhap_gia_tri)

        return scale

    # ----------------------------------------------------------------
    # XỬ LÝ SỰ KIỆN
    # ----------------------------------------------------------------
    def _doi_vat_the(self, event=None):
        """Khi đổi tùy chọn trong Combobox Vật thể."""
        ten_vat_the = self.bien_vat_the.get()
        func_tao = DANH_SACH_VAT_THE.get(ten_vat_the)
        if func_tao:
            self.wireframe = func_tao()
            self._ve_lai()

    def _khi_resize_canvas(self, event):
        """Tính lại tâm màn hình khi resize cửa sổ."""
        self.center_x = event.width / 2
        self.center_y = event.height / 2
        self._ve_lai()

    def _ap_dung_preset(self, event=None):
        """Cập nhật Slider khi bấm chọn Preset."""
        ten_preset = self.bien_preset.get()
        thong_so = DANH_SACH_PRESET.get(ten_preset)
        if not thong_so:
            return

        if "theta" in thong_so:
            self.bien_theta.set(thong_so["theta"])
            self.scale_theta.set(thong_so["theta"])
        if "phi" in thong_so:
            self.bien_phi.set(thong_so["phi"])
            self.scale_phi.set(thong_so["phi"])
        if "R" in thong_so:
            self.bien_R.set(thong_so["R"])
            self.scale_R.set(thong_so["R"])
        if "D" in thong_so:
            self.bien_D.set(thong_so["D"])
            self.scale_D.set(thong_so["D"])
        if "mode" in thong_so:
            self.bien_mode.set(thong_so["mode"])

        self._ve_lai()

    # ----------------------------------------------------------------
    # PHÉP CHIẾU 1 ĐIỂM 3D -> TỌA ĐỘ CANVAS
    # ----------------------------------------------------------------
    def _chieu_diem(self, x, y, z):
        theta = self.bien_theta.get()
        phi = self.bien_phi.get()
        R = self.bien_R.get()
        D = self.bien_D.get()

        x0, y0, z0 = world_to_obs(x, y, z, theta, phi, R)

        if self.bien_mode.get() == "perspective":
            xE, yE = project_perspective(x0, y0, z0, D)
            scale = 15.0
        else:
            xE, yE = project_parallel(x0, y0, z0)
            scale = 100.0  # Phóng to cho phép chiếu song song dễ nhìn

        return to_canvas_coords(xE * scale, yE * scale, self.center_x, self.center_y)

    # ----------------------------------------------------------------
    # VẼ TOÀN BỘ CẢNH (REDRAW)
    # ----------------------------------------------------------------
    def _ve_lai(self):
        self.canvas.delete("all")
        goc_canvas = self._chieu_diem(0, 0, 0)

        self._ve_he_truc()
        self._ve_wireframe(goc_canvas)
        self._ve_thong_so()
        self._ve_nhan_tac_gia()

    def _ve_he_truc(self):
        o = self._chieu_diem(0, 0, 0)
        px = self._chieu_diem(2, 0, 0)
        py = self._chieu_diem(0, 2, 0)
        pz = self._chieu_diem(0, 0, 2)

        self.canvas.create_line(*o, *px, fill=self.MAU_TRUC_X, width=2)
        self.canvas.create_text(
            px[0] + 10, px[1], text="X", fill=self.MAU_TRUC_X, font=("Segoe UI", 11, "bold")
        )

        self.canvas.create_line(*o, *py, fill=self.MAU_TRUC_Y, width=2)
        self.canvas.create_text(
            py[0] + 10, py[1], text="Y", fill=self.MAU_TRUC_Y, font=("Segoe UI", 11, "bold")
        )

        self.canvas.create_line(*o, *pz, fill=self.MAU_TRUC_Z, width=2)
        self.canvas.create_text(
            pz[0] + 10, pz[1], text="Z", fill=self.MAU_TRUC_Z, font=("Segoe UI", 11, "bold")
        )

    def _ve_wireframe(self, goc_canvas):
        diem_canvas = [self._chieu_diem(d.x, d.y, d.z) for d in self.wireframe.dinh]

        # 1. Vẽ các cạnh khung dây của vật thể 3D
        for i, j in self.wireframe.canh:
            x1, y1 = diem_canvas[i]
            x2, y2 = diem_canvas[j]
            self.canvas.create_line(x1, y1, x2, y2, fill=self.MAU_KHOI, width=2)

        # 2. CHỈ VẼ NÉT ĐỨT (TIA CHIẾU HỘI TỤ VỀ GỐC) KHI Ở CHẾ ĐỘ PHỐI CẢNH
        if self.bien_mode.get() == "perspective":
            for cx, cy in diem_canvas:
                self.canvas.create_line(
                    cx, cy, goc_canvas[0], goc_canvas[1],
                    fill=self.MAU_TIA_CHIEU, dash=(2, 4), width=1
                )
                
    def _ve_thong_so(self):
        ten_mode = (
            "Phối cảnh (Perspective)"
            if self.bien_mode.get() == "perspective"
            else "Song song (Parallel)"
        )
        noi_dung = (
            f"Hình: {self.bien_vat_the.get()} | "
            f"Chế độ: {ten_mode} | "
            f"Theta: {self.bien_theta.get():.0f}° | "
            f"Phi: {self.bien_phi.get():.0f}° | "
            f"R: {self.bien_R.get():.0f} | "
            f"D: {self.bien_D.get():.0f}"
        )
        self.canvas.create_text(
            12, 14, text=noi_dung, fill=self.MAU_CHU, anchor="w", font=("Consolas", 10)
        )

    def _ve_nhan_tac_gia(self):
        self.canvas.create_text(
            12, 34, text="Thực hiện: Hoàng Đình Quảng (Lunia)",
            fill="#777777", anchor="w", font=("Segoe UI", 9, "italic")
        )

def main():
    root = tk.Tk()
    ProjectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()