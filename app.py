# Ung dung cham bai trac nghiem - giao dien desktop
# Chay: python app.py
# Du lieu moi ky thi nam trong thu muc exams/<ten ky thi>:
#   de.json   : mau phieu va dap an cac ma de
#   diem.csv  : ket qua tat ca cac lan cham (cham nhieu lan se duoc gop vao day)
#   images/   : anh ket qua va anh phieu loi
import os
import csv
import json
import shutil
import datetime
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageDraw
from templates import DANH_SACH_MAU
from grader import grade_image

# ---------------- Mau sac (theo file design: navy - slate - sage) ----------------
XANH_DAM = "#0F172A"
XANH_DAM_HOVER = "#020617"
XAM = "#64748B"
XAM_CHU = "#475569"
XAM_NHAT = "#94A3B8"
XANH_LA = "#059669"
XANH_LA_DAM = "#047857"
XANH_LA_NEN = "#DCFCE7"
XANH_LA_CHU = "#16A34A"
XANH_LA_CHON = "#A7F3D0"
VANG_NEN = "#FEF9C3"
VANG_CHU = "#CA8A04"
DO = "#EF4444"
DO_DAM = "#DC2626"
DO_NEN = "#FEE2E2"
XANH_DUONG = "#0EA5E9"
XANH_DUONG_NEN = "#E0F2FE"
TIM_NEN = "#E0E7FF"
TIM = "#4F46E5"
NEN = "#F8FAFC"
NEN_MENU = "#F1F5F9"
THE = "#FFFFFF"
VIEN = "#E2E8F0"
VIEN_DAM = "#CBD5E1"
FONT = "Plus Jakarta Sans"

# So cot cua bang nhap dap an
SO_COT_DAP_AN = 4

THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))
THU_MUC_KY_THI = os.path.join(THU_MUC_GOC, "exams")

# Nap font Plus Jakarta Sans trong thu muc fonts (neu co)
for ten_font in ["PlusJakartaSans-Regular.ttf", "PlusJakartaSans-Bold.ttf"]:
    duong_dan_font = os.path.join(THU_MUC_GOC, "fonts", ten_font)
    if os.path.exists(duong_dan_font):
        ctk.FontManager.load_font(duong_dan_font)

ctk.set_appearance_mode("light")

# Doi trang thai loi (khong dau, luu trong file csv) sang tieng Viet de hien thi
DICH_LOI = {
    "loi: khong tim du 4 o goc": "Không tìm đủ 4 ô vuông góc phiếu",
    "loi: 4 goc tim duoc khong khop ti le phieu (anh chup qua nghieng?)": "Ảnh chụp quá nghiêng, 4 góc không khớp tỉ lệ phiếu",
    "loi: khong doc duoc anh": "Không đọc được ảnh",
}


def draw_icon(loai, mau, co):
    # Ve bieu tuong don gian bang PIL (ve to gap 4 lan roi thu nho cho net muot)
    # loai: "de", "cham", "thong_ke", "logo", "phieu", "dung", "loi", "diem", "them", "tai"
    k = co * 4
    anh = Image.new("RGBA", (k, k), (0, 0, 0, 0))
    ve = ImageDraw.Draw(anh)
    net = max(4, k // 11)
    if loai == "de":
        # To giay co 3 dong ke
        ve.rounded_rectangle([k * 0.2, k * 0.1, k * 0.8, k * 0.9], radius=k * 0.08, outline=mau, width=net)
        for y in [0.35, 0.52, 0.69]:
            ve.line([k * 0.32, k * y, k * 0.68, k * y], fill=mau, width=net)
    elif loai == "cham" or loai == "dung":
        # O vuong co dau tich
        ve.rounded_rectangle([k * 0.12, k * 0.12, k * 0.88, k * 0.88], radius=k * 0.16, outline=mau, width=net)
        ve.line([k * 0.3, k * 0.52, k * 0.45, k * 0.67, k * 0.72, k * 0.36], fill=mau, width=net, joint="curve")
    elif loai == "thong_ke" or loai == "diem":
        # Bieu do cot
        ve.line([k * 0.12, k * 0.88, k * 0.88, k * 0.88], fill=mau, width=net)
        cac_cot = [[0.2, 0.55], [0.43, 0.3], [0.66, 0.45]]
        for cot in cac_cot:
            ve.rounded_rectangle([k * cot[0], k * cot[1], k * (cot[0] + 0.15), k * 0.8], radius=k * 0.03, fill=mau)
    elif loai == "logo":
        # Dau tich lon mau trang
        ve.line([k * 0.24, k * 0.52, k * 0.42, k * 0.7, k * 0.76, k * 0.32], fill=mau, width=net * 2, joint="curve")
    elif loai == "phieu":
        # 2 to giay chong len nhau
        ve.rounded_rectangle([k * 0.3, k * 0.1, k * 0.85, k * 0.75], radius=k * 0.08, outline=mau, width=net)
        ve.rounded_rectangle([k * 0.15, k * 0.25, k * 0.7, k * 0.9], radius=k * 0.08, outline=mau, width=net, fill=(255, 255, 255, 0))
    elif loai == "loi":
        # Hinh tron co dau X
        ve.ellipse([k * 0.12, k * 0.12, k * 0.88, k * 0.88], outline=mau, width=net)
        ve.line([k * 0.36, k * 0.36, k * 0.64, k * 0.64], fill=mau, width=net)
        ve.line([k * 0.64, k * 0.36, k * 0.36, k * 0.64], fill=mau, width=net)
    elif loai == "them":
        # Dau cong
        ve.line([k * 0.5, k * 0.2, k * 0.5, k * 0.8], fill=mau, width=net)
        ve.line([k * 0.2, k * 0.5, k * 0.8, k * 0.5], fill=mau, width=net)
    elif loai == "tai":
        # Mui ten di xuong va khay
        ve.line([k * 0.5, k * 0.15, k * 0.5, k * 0.62], fill=mau, width=net)
        ve.line([k * 0.3, k * 0.44, k * 0.5, k * 0.64, k * 0.7, k * 0.44], fill=mau, width=net, joint="curve")
        ve.line([k * 0.18, k * 0.66, k * 0.18, k * 0.84, k * 0.82, k * 0.84, k * 0.82, k * 0.66], fill=mau, width=net, joint="curve")
    anh = anh.resize((co, co), Image.LANCZOS)
    return ctk.CTkImage(light_image=anh, size=(co, co))


class DropdownItem(ctk.CTkButton):
    # 1 dong trong danh sach cua Dropdown, bam vao thi bao cho Dropdown biet gia tri duoc chon
    def __init__(self, master, hop_chon, gia_tri, dang_chon):
        mau_nen = "transparent"
        mau_chu = XAM_CHU
        if dang_chon:
            mau_nen = NEN_MENU
            mau_chu = XANH_DAM
        super().__init__(master, text="  " + gia_tri, command=self.on_click, height=40, corner_radius=8, anchor="w",
                         fg_color=mau_nen, hover_color=NEN, text_color=mau_chu, font=(FONT, 14, "bold"))
        self.hop_chon = hop_chon
        self.gia_tri = gia_tri

    def on_click(self):
        self.hop_chon.pick(self.gia_tri)


class Dropdown(ctk.CTkButton):
    # O chon: nut nen trang vien xam. Bam vao thi hien danh sach ngay ben duoi, chon xong thi goi ham_chon(gia_tri)
    def __init__(self, master, cac_gia_tri, ham_chon, width=260):
        super().__init__(master, text="", command=self.open_list, width=width, height=44, corner_radius=8,
                         fg_color=THE, hover_color=NEN, text_color=XANH_DAM, border_width=1, border_color=VIEN,
                         font=(FONT, 14, "bold"), anchor="w")
        # Mui ten o ben phai nut
        self.mui_ten = ctk.CTkLabel(self, text="▾", font=(FONT, 15, "bold"), text_color=XAM, fg_color="transparent", width=20)
        self.mui_ten.place(relx=1.0, rely=0.5, x=-22, anchor="center")
        self.mui_ten.bind("<Button-1>", self.on_arrow_click)
        self.cac_gia_tri = list(cac_gia_tri)
        self.ham_chon = ham_chon
        self.gia_tri = ""
        self.cua_so = None
        if len(self.cac_gia_tri) > 0:
            self.set(self.cac_gia_tri[0])

    def set(self, gia_tri):
        self.gia_tri = gia_tri
        self.configure(text="  " + gia_tri)

    def get(self):
        return self.gia_tri

    def set_values(self, cac_gia_tri):
        self.cac_gia_tri = list(cac_gia_tri)

    def on_arrow_click(self, su_kien):
        self.open_list()

    def open_list(self):
        if self.cua_so is not None:
            self.close_list()
            return
        if len(self.cac_gia_tri) == 0:
            return
        # Cua so khong vien, dat ngay duoi nut, moi gia tri la 1 dong DropdownItem
        self.cua_so = tk.Toplevel(self)
        self.cua_so.overrideredirect(True)
        self.cua_so.configure(bg=VIEN)
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        rong = self.winfo_width()
        if len(self.cac_gia_tri) > 7:
            khung = ctk.CTkScrollableFrame(self.cua_so, fg_color=THE, corner_radius=0, height=7 * 44)
        else:
            khung = ctk.CTkFrame(self.cua_so, fg_color=THE, corner_radius=0)
        khung.pack(fill="both", expand=True, padx=1, pady=1)
        ctk.CTkFrame(khung, fg_color="transparent", height=4).pack()
        for gia_tri in self.cac_gia_tri:
            DropdownItem(khung, self, gia_tri, gia_tri == self.gia_tri).pack(fill="x", padx=6, pady=1)
        ctk.CTkFrame(khung, fg_color="transparent", height=4).pack()
        self.cua_so.bind("<Escape>", self.on_escape)
        self.cua_so.bind("<FocusOut>", self.on_focus_out)
        self.cua_so.update_idletasks()
        cao = self.cua_so.winfo_reqheight()
        self.cua_so.geometry(str(rong) + "x" + str(cao) + "+" + str(x) + "+" + str(y))
        self.cua_so.focus_force()

    def pick(self, gia_tri):
        self.close_list()
        self.set(gia_tri)
        if self.ham_chon is not None:
            self.ham_chon(gia_tri)

    def on_focus_out(self, su_kien):
        # Chi dong khi tieu diem roi khoi ca cua so danh sach (khong dong khi bam vao 1 dong ben trong)
        self.after(150, self.check_close)

    def check_close(self):
        if self.cua_so is None:
            return
        dang_focus = self.cua_so.focus_get()
        if dang_focus is None or not str(dang_focus).startswith(str(self.cua_so)):
            self.close_list()

    def on_escape(self, su_kien):
        self.close_list()

    def close_list(self):
        if self.cua_so is not None:
            self.cua_so.destroy()
            self.cua_so = None


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chấm trắc nghiệm")
        self.geometry("1400x860")
        self.minsize(1180, 720)
        self.configure(fg_color=NEN)
        os.makedirs(THU_MUC_KY_THI, exist_ok=True)

        # Neu may khong co font Plus Jakarta Sans thi dung Segoe UI
        global FONT
        if FONT not in tkfont.families(self):
            FONT = "Segoe UI"

        # Trang thai chung
        self.ky_thi = ""
        self.thong_tin = None
        self.mau = None
        self.de_dang_sua = ""
        self.bien_dap_an = []
        self.anh_da_chon = []
        self.ket_qua_anh = []
        self.tab_dang_mo = ""

        # Kieu bang (Treeview): khong vien, dong cao, tieu de chu nho in hoa mau xam
        kieu = ttk.Style()
        kieu.theme_use("clam")
        kieu.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        kieu.configure("Treeview", font=(FONT, 12), rowheight=46, background=THE, fieldbackground=THE, foreground=XANH_DAM, borderwidth=0)
        kieu.configure("Treeview.Heading", font=(FONT, 10, "bold"), background=NEN, foreground=XAM, relief="flat", padding=(10, 12))
        kieu.map("Treeview", background=[("selected", NEN_MENU)], foreground=[("selected", XANH_DAM)])
        kieu.map("Treeview.Heading", background=[("active", NEN)])

        # ---------------- Cot menu ben trai ----------------
        menu = ctk.CTkFrame(self, fg_color=NEN_MENU, corner_radius=0, width=244)
        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)
        logo = ctk.CTkFrame(menu, fg_color="transparent")
        logo.pack(anchor="w", padx=18, pady=(26, 34))
        o_logo = ctk.CTkLabel(logo, text="", image=draw_icon("logo", "#FFFFFF", 24), width=44, height=44, fg_color=XANH_DAM, corner_radius=10)
        o_logo.pack(side="left")
        chu_logo = ctk.CTkFrame(logo, fg_color="transparent")
        chu_logo.pack(side="left", padx=10)
        ctk.CTkLabel(chu_logo, text="Chấm Trắc Nghiệm", font=(FONT, 16, "bold"), text_color=XANH_DAM, height=22).pack(anchor="w")
        ctk.CTkLabel(chu_logo, text="XỬ LÝ ẢNH  ·  OMR", font=(FONT, 10, "bold"), text_color=XAM, height=16).pack(anchor="w")
        self.nut_tab_de = ctk.CTkButton(menu, text="  Đề & đáp án", command=self.open_answer_tab, height=48, anchor="w",
                                        font=(FONT, 15), corner_radius=8, compound="left")
        self.nut_tab_de.pack(fill="x", padx=16, pady=3)
        self.nut_tab_anh = ctk.CTkButton(menu, text="  Chấm bài", command=self.open_grading_tab, height=48, anchor="w",
                                         font=(FONT, 15), corner_radius=8, compound="left")
        self.nut_tab_anh.pack(fill="x", padx=16, pady=3)
        self.nut_tab_tk = ctk.CTkButton(menu, text="  Thống kê", command=self.open_stats_tab, height=48, anchor="w",
                                        font=(FONT, 15), corner_radius=8, compound="left")
        self.nut_tab_tk.pack(fill="x", padx=16, pady=3)
        # Moi nut menu co 2 bieu tuong: mau xam (chua chon) va mau dam (dang chon)
        self.bieu_tuong_menu = {
            "de": [draw_icon("de", XAM, 20), draw_icon("de", XANH_DAM, 20)],
            "anh": [draw_icon("cham", XAM, 20), draw_icon("cham", XANH_DAM, 20)],
            "tk": [draw_icon("thong_ke", XAM, 20), draw_icon("thong_ke", XANH_DAM, 20)],
        }

        # The ky thi o cuoi menu
        the_ky_thi = ctk.CTkFrame(menu, fg_color=THE, corner_radius=12, border_width=1, border_color=VIEN)
        the_ky_thi.pack(side="bottom", fill="x", padx=16, pady=20)
        ctk.CTkLabel(the_ky_thi, text="KỲ THI ĐANG CHỌN", font=(FONT, 10, "bold"), text_color=XAM).pack(anchor="w", padx=16, pady=(14, 0))
        self.nhan_ky_thi_menu = ctk.CTkLabel(the_ky_thi, text="Chưa có kỳ thi", font=(FONT, 14, "bold"), text_color=XANH_DAM, wraplength=190, justify="left")
        self.nhan_ky_thi_menu.pack(anchor="w", padx=16)
        self.nhan_mau_menu = ctk.CTkLabel(the_ky_thi, text="", font=(FONT, 12), text_color=XAM_CHU)
        self.nhan_mau_menu.pack(anchor="w", padx=16, pady=(0, 14))

        # ---------------- Ben phai: tieu de trang + noi dung tab ----------------
        phai = ctk.CTkFrame(self, fg_color=NEN, corner_radius=0)
        phai.pack(side="left", fill="both", expand=True)
        dau_trang = ctk.CTkFrame(phai, fg_color="transparent")
        dau_trang.pack(fill="x", padx=(24, 24), pady=(26, 20))
        trai_dau = ctk.CTkFrame(dau_trang, fg_color="transparent")
        trai_dau.pack(side="left")
        self.nhan_tieu_de = ctk.CTkLabel(trai_dau, text="", font=(FONT, 32, "bold"), text_color=XANH_DAM, height=40)
        self.nhan_tieu_de.pack(anchor="w")
        dong_phu = ctk.CTkFrame(trai_dau, fg_color="transparent")
        dong_phu.pack(anchor="w")
        self.nhan_phu_de = ctk.CTkLabel(dong_phu, text="", font=(FONT, 15), text_color=XAM_CHU, height=24)
        self.nhan_phu_de.pack(side="left")
        self.nhan_trang_thai_de = ctk.CTkLabel(dong_phu, text="", font=(FONT, 15, "bold"), text_color=XANH_LA, height=24)
        self.nhan_trang_thai_de.pack(side="left")
        ctk.CTkButton(dau_trang, text="Tạo kỳ thi", image=draw_icon("them", "#FFFFFF", 16), compound="left", command=self.open_create_exam_dialog,
                      height=46, corner_radius=8, font=(FONT, 15, "bold"), fg_color=XANH_DAM, hover_color=XANH_DAM_HOVER).pack(side="right")
        self.chon_ky_thi_menu = Dropdown(dau_trang, [], self.select_exam, width=280)
        self.chon_ky_thi_menu.pack(side="right", padx=12)

        # Moi tab la 1 khung, chi hien khung cua tab dang mo
        self.tab_de = ctk.CTkFrame(phai, fg_color=NEN, corner_radius=0)
        self.tab_anh = ctk.CTkFrame(phai, fg_color=NEN, corner_radius=0)
        self.tab_tk = ctk.CTkFrame(phai, fg_color=NEN, corner_radius=0)

        self.build_answer_tab()
        self.build_grading_tab()
        self.build_stats_tab()
        self.open_answer_tab()

        self.refresh_exam_list("")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # Mo cua so toan man hinh tren Windows
        if os.name == "nt":
            self.after(100, self.maximize)


    # =====================================================================
    # Ky thi
    # =====================================================================
    def refresh_exam_list(self, ten_chon):
        # Doc ten cac thu muc trong ky_thi, chon ky thi ten_chon (hoac ky thi dau tien)
        cac_ky_thi = []
        for ten in sorted(os.listdir(THU_MUC_KY_THI)):
            if os.path.isfile(os.path.join(THU_MUC_KY_THI, ten, "de.json")):
                cac_ky_thi.append(ten)
        self.chon_ky_thi_menu.set_values(cac_ky_thi)
        if len(cac_ky_thi) == 0:
            self.chon_ky_thi_menu.set("Chưa có kỳ thi")
            self.update_header()
            return
        if ten_chon == "" or ten_chon not in cac_ky_thi:
            ten_chon = cac_ky_thi[0]
        self.chon_ky_thi_menu.set(ten_chon)
        self.select_exam(ten_chon)

    def select_exam(self, ten):
        # Tu luu dap an dang nhap cua ky thi cu truoc khi doi
        if self.thong_tin is not None and not self.save_answers(False):
            self.chon_ky_thi_menu.set(self.ky_thi)
            return
        self.de_dang_sua = ""
        f = open(os.path.join(THU_MUC_KY_THI, ten, "de.json"), encoding="utf-8")
        self.thong_tin = json.load(f)
        f.close()
        self.ky_thi = ten
        self.mau = DANH_SACH_MAU[self.thong_tin["mau"]]
        self.build_answer_grid()
        self.refresh_code_list("")
        self.ket_qua_anh = []
        for dong in self.bang_anh.get_children():
            self.bang_anh.delete(dong)
        self.refresh_stats()
        self.update_header()

    def open_create_exam_dialog(self):
        self.hop = ctk.CTkToplevel(self)
        self.hop.title("Tạo kỳ thi")
        self.hop.geometry("480x380")
        self.hop.resizable(False, False)
        self.hop.configure(fg_color=THE)
        self.hop.transient(self)
        self.hop.grab_set()
        ctk.CTkLabel(self.hop, text="Tạo kỳ thi mới", font=(FONT, 24, "bold"), text_color=XANH_DAM).pack(anchor="w", padx=32, pady=(28, 0))
        ctk.CTkLabel(self.hop, text="Đặt tên và chọn mẫu phiếu dùng cho kỳ thi", font=(FONT, 13), text_color=XAM_CHU).pack(anchor="w", padx=32, pady=(0, 18))
        ctk.CTkLabel(self.hop, text="Tên kỳ thi", font=(FONT, 14, "bold"), text_color=XANH_DAM).pack(anchor="w", padx=32, pady=(0, 6))
        self.o_ten_ky_thi = ctk.CTkEntry(self.hop, height=42, corner_radius=8, font=(FONT, 14), fg_color=THE, border_width=1, border_color=VIEN,
                                         text_color=XANH_DAM, placeholder_text="Ví dụ: Giữa kỳ Toán 12A1")
        self.o_ten_ky_thi.pack(fill="x", padx=32)
        ctk.CTkLabel(self.hop, text="Mẫu phiếu", font=(FONT, 14, "bold"), text_color=XANH_DAM).pack(anchor="w", padx=32, pady=(16, 6))
        cac_mau = []
        for ten in DANH_SACH_MAU:
            cac_mau.append(ten)
        self.chon_mau_moi = Dropdown(self.hop, cac_mau, None, width=416)
        self.chon_mau_moi.pack(anchor="w", padx=32)
        ctk.CTkButton(self.hop, text="Tạo kỳ thi", command=self.create_exam, height=48, corner_radius=8, font=(FONT, 15, "bold"),
                      fg_color=XANH_DAM, hover_color=XANH_DAM_HOVER).pack(fill="x", padx=32, pady=28)

    def create_exam(self):
        ten = self.o_ten_ky_thi.get().strip()
        # Bo cac ky tu khong duoc dung trong ten thu muc
        for c in '\\/:*?"<>|':
            ten = ten.replace(c, "")
        if ten == "":
            messagebox.showerror("Lỗi", "Chưa nhập tên kỳ thi", parent=self.hop)
            return
        thu_muc = os.path.join(THU_MUC_KY_THI, ten)
        if os.path.exists(thu_muc):
            messagebox.showerror("Lỗi", "Kỳ thi này đã có", parent=self.hop)
            return
        os.makedirs(os.path.join(thu_muc, "images"))
        thong_tin = {"mau": self.chon_mau_moi.get(), "cac_de": {}}
        f = open(os.path.join(thu_muc, "de.json"), "w", encoding="utf-8")
        json.dump(thong_tin, f, ensure_ascii=False, indent=1)
        f.close()
        self.chon_mau_moi.close_list()
        self.hop.destroy()
        self.refresh_exam_list(ten)
        self.open_answer_tab()

    def save_exam_data(self):
        f = open(os.path.join(THU_MUC_KY_THI, self.ky_thi, "de.json"), "w", encoding="utf-8")
        json.dump(self.thong_tin, f, ensure_ascii=False, indent=1)
        f.close()

    def check_exam_selected(self):
        if self.thong_tin is None:
            messagebox.showinfo("Chưa có kỳ thi", "Hãy tạo hoặc chọn một kỳ thi trước")
            return False
        return True


    # =====================================================================
    # Tab 1: De & dap an
    # =====================================================================
    def build_answer_tab(self):
        self.tab_de.grid_columnconfigure(1, weight=1)
        self.tab_de.grid_rowconfigure(0, weight=1)

        # Cot trai: danh sach ma de
        trai = ctk.CTkFrame(self.tab_de, fg_color=THE, corner_radius=12, border_width=1, border_color=VIEN, width=210)
        trai.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        trai.pack_propagate(False)
        ctk.CTkLabel(trai, text="Mã đề", font=(FONT, 20, "bold"), text_color=XANH_DAM).pack(anchor="w", padx=22, pady=(22, 0))
        ctk.CTkLabel(trai, text="Bấm vào mã đề để xem\nvà sửa đáp án", font=(FONT, 12), text_color=XAM_CHU, justify="left").pack(anchor="w", padx=22, pady=(0, 12))
        khung_ds = ctk.CTkFrame(trai, fg_color=THE, corner_radius=8, border_width=1, border_color=VIEN)
        khung_ds.pack(fill="both", expand=True, padx=18)
        self.ds_de = tk.Listbox(khung_ds, font=(FONT, 14), height=10, activestyle="none", bd=0, highlightthickness=0,
                                bg=THE, fg=XAM_CHU, selectbackground=NEN_MENU, selectforeground=XANH_DAM, exportselection=False, cursor="hand2")
        self.ds_de.pack(fill="both", expand=True, padx=6, pady=8)
        self.ds_de.bind("<<ListboxSelect>>", self.select_version)
        ctk.CTkLabel(trai, text="Mã đề mới (3 số)", font=(FONT, 13, "bold"), text_color=XANH_DAM).pack(anchor="w", padx=22, pady=(16, 6))
        self.o_ma_de = ctk.CTkEntry(trai, height=42, corner_radius=8, font=(FONT, 15), fg_color=THE, border_width=1, border_color=VIEN, text_color=XANH_DAM)
        self.o_ma_de.pack(fill="x", padx=18)
        ctk.CTkButton(trai, text="Thêm đề", image=draw_icon("them", "#FFFFFF", 14), compound="left", command=self.add_version, height=42,
                      corner_radius=8, font=(FONT, 14, "bold"), fg_color=XANH_DAM, hover_color=XANH_DAM_HOVER).pack(fill="x", padx=18, pady=(10, 6))
        ctk.CTkButton(trai, text="Xóa đề đang chọn", command=self.delete_version, height=40, corner_radius=8, font=(FONT, 13, "bold"),
                      fg_color="transparent", text_color=DO_DAM, hover_color=DO_NEN).pack(fill="x", padx=18, pady=(0, 18))

        # Cot phai: bang chon dap an
        phai = ctk.CTkFrame(self.tab_de, fg_color=THE, corner_radius=12, border_width=1, border_color=VIEN)
        phai.grid(row=0, column=1, sticky="nsew")
        thanh = ctk.CTkFrame(phai, fg_color="transparent")
        thanh.pack(fill="x", padx=24, pady=(22, 4))
        self.nhan_de = ctk.CTkLabel(thanh, text="Chưa chọn đề", font=(FONT, 22, "bold"), text_color=XANH_DAM)
        self.nhan_de.pack(side="left")
        self.nhan_so_cau = ctk.CTkLabel(thanh, text="", font=(FONT, 11, "bold"), text_color=XANH_LA_CHU, fg_color=XANH_LA_NEN, corner_radius=4, height=24)
        self.nhan_so_cau.pack(side="left", padx=14)
        ctk.CTkButton(thanh, text="Lưu đáp án", command=self.save_answers, height=42, width=140, corner_radius=8, font=(FONT, 14, "bold"),
                      fg_color=XANH_DAM, hover_color=XANH_DAM_HOVER).pack(side="right")
        ctk.CTkButton(thanh, text="Xóa hết", command=self.clear_answers, height=42, width=96, corner_radius=8, font=(FONT, 14, "bold"),
                      fg_color="transparent", text_color=XAM_CHU, hover_color=NEN_MENU).pack(side="right", padx=8)
        ctk.CTkLabel(phai, text="Bấm A, B, C, D để chọn đáp án. Ô màu xanh là đáp án đã chọn.", font=(FONT, 13), text_color=XAM_CHU).pack(anchor="w", padx=24)

        thanh2 = ctk.CTkFrame(phai, fg_color="transparent")
        thanh2.pack(fill="x", padx=24, pady=(14, 12))
        ctk.CTkLabel(thanh2, text="Nhập nhanh", font=(FONT, 13, "bold"), text_color=XANH_DAM).pack(side="left")
        self.o_nhap_nhanh = ctk.CTkEntry(thanh2, height=42, corner_radius=8, font=(FONT, 14), fg_color=THE, border_width=1, border_color=VIEN,
                                         text_color=XANH_DAM, placeholder_text="Chuỗi ABCD cho phần trắc nghiệm, ví dụ ABCDDCBA_A (dấu _ là bỏ trống)")
        self.o_nhap_nhanh.pack(side="left", fill="x", expand=True, padx=12)
        ctk.CTkButton(thanh2, text="Điền", command=self.quick_fill, height=42, width=90, corner_radius=8, font=(FONT, 14, "bold"),
                      fg_color="transparent", text_color=XANH_DAM, border_width=1, border_color=XANH_DAM, hover_color=NEN_MENU).pack(side="left")

        ctk.CTkFrame(phai, fg_color=VIEN, height=1).pack(fill="x")
        self.khung_bang = ctk.CTkScrollableFrame(phai, fg_color=THE, scrollbar_button_color=VIEN, scrollbar_button_hover_color=VIEN_DAM)
        self.khung_bang.pack(fill="both", expand=True, padx=8, pady=(6, 14))

    def build_answer_grid(self):
        # Tao lai bang chon dap an theo mau phieu cua ky thi
        for w in self.khung_bang.winfo_children():
            w.destroy()
        self.bien_dap_an = []
        tat_ca_hang = []
        cac_phan = self.mau["cac_phan"]
        for p in range(len(cac_phan)):
            phan = cac_phan[p]
            if len(cac_phan) > 1:
                ten_phan = "PHẦN " + str(p + 1)
                if phan["loai"] == "abcd":
                    ten_phan = ten_phan + "  ·  TRẮC NGHIỆM ABCD"
                elif phan["loai"] == "dung_sai":
                    ten_phan = ten_phan + "  ·  ĐÚNG / SAI"
                else:
                    ten_phan = ten_phan + "  ·  ĐIỀN SỐ"
                ctk.CTkLabel(self.khung_bang, text=ten_phan, font=(FONT, 11, "bold"), text_color=XAM).pack(anchor="w", padx=12, pady=(16, 6))
            khung = tk.Frame(self.khung_bang, bg=THE)
            khung.pack(fill="x", anchor="w")
            bien_phan = []
            hang_phan = []
            for cau in range(phan["so_cau"]):
                hang = tk.Frame(khung, bg=THE, padx=0, pady=4)
                tk.Label(hang, text=str(cau + 1), font=(FONT, 13, "bold"), width=3, anchor="e", bg=THE, fg=XAM).pack(side="left", padx=(0, 4))
                if phan["loai"] == "abcd":
                    # Nut chua chon: nen teal nhat. Nut da chon: nen vang
                    bien = tk.StringVar(value="")
                    for chu in ["A", "B", "C", "D"]:
                        tk.Radiobutton(hang, text=chu, value=chu, variable=bien, indicatoron=0, width=1, font=(FONT, 13, "bold"),
                                       bg=NEN_MENU, fg=XAM_CHU, selectcolor=XANH_LA_CHON, activebackground=VIEN, activeforeground=XANH_DAM,
                                       relief="flat", bd=0, padx=7, pady=7, cursor="hand2", offrelief="flat").pack(side="left", padx=1)
                    bien_phan.append(bien)
                elif phan["loai"] == "dung_sai":
                    ds_bien = []
                    for y in ["a", "b", "c", "d"]:
                        tk.Label(hang, text=y, font=(FONT, 13, "bold"), bg=THE, fg=XAM).pack(side="left", padx=(10, 3))
                        bien = tk.StringVar(value="")
                        for chu in ["Đ", "S"]:
                            tk.Radiobutton(hang, text=chu, value=chu, variable=bien, indicatoron=0, width=1, font=(FONT, 13, "bold"),
                                           bg=NEN_MENU, fg=XAM_CHU, selectcolor=XANH_LA_CHON, activebackground=VIEN, activeforeground=XANH_DAM,
                                           relief="flat", bd=0, padx=9, pady=7, cursor="hand2", offrelief="flat").pack(side="left", padx=1)
                        ds_bien.append(bien)
                    bien_phan.append(ds_bien)
                else:
                    bien = tk.StringVar(value="")
                    tk.Entry(hang, textvariable=bien, font=(FONT, 15), width=8, relief="flat", bd=0, bg=THE, fg=XANH_DAM,
                             highlightthickness=1, highlightbackground=VIEN_DAM, highlightcolor=XANH_DAM).pack(side="left", ipady=7)
                    bien_phan.append(bien)
                hang_phan.append(hang)
            self.bien_dap_an.append(bien_phan)
            tat_ca_hang.append(hang_phan)

        # Xep cac cau thanh SO_COT_DAP_AN cot: cau 1, 2, 3... di tu tren xuong, het cot thi sang cot ben phai
        # Cau dung/sai dai hon nen chi xep 2 cot
        for p in range(len(tat_ca_hang)):
            hang_phan = tat_ca_hang[p]
            so_cot = SO_COT_DAP_AN
            if cac_phan[p]["loai"] == "dung_sai":
                so_cot = 2
            so_hang = (len(hang_phan) + so_cot - 1) // so_cot
            for i in range(len(hang_phan)):
                hang_phan[i].grid(row=i % so_hang, column=i // so_hang, sticky="w", padx=(0, 4))

    def refresh_code_list(self, ma_chon):
        self.ds_de.delete(0, "end")
        cac_ma = sorted(self.thong_tin["cac_de"])
        # Moi dong: ma de va so cau da nhap dap an
        tong_so_cau = 0
        for phan in self.mau["cac_phan"]:
            tong_so_cau += phan["so_cau"]
        for ma in cac_ma:
            so_cau_da_nhap = 0
            for phan in self.thong_tin["cac_de"][ma]:
                for gia_tri in phan:
                    if gia_tri != "":
                        so_cau_da_nhap += 1
            self.ds_de.insert("end", "  " + ma + "    " + str(so_cau_da_nhap) + "/" + str(tong_so_cau))
        if len(cac_ma) == 0:
            self.de_dang_sua = ""
            self.nhan_de.configure(text="Chưa có đề nào")
            self.nhan_so_cau.configure(text="  THÊM MÃ ĐỀ Ở CỘT BÊN TRÁI  ")
            self.clear_answers()
            return
        if ma_chon not in cac_ma:
            ma_chon = cac_ma[0]
        vi_tri = cac_ma.index(ma_chon)
        self.ds_de.selection_clear(0, "end")
        self.ds_de.selection_set(vi_tri)
        self.show_answers(ma_chon)

    def select_version(self, su_kien):
        chon = self.ds_de.curselection()
        if len(chon) == 0:
            return
        cac_ma = sorted(self.thong_tin["cac_de"])
        ma_moi = cac_ma[chon[0]]
        if ma_moi == self.de_dang_sua:
            return
        # Tu luu dap an cua de dang sua truoc khi chuyen sang de khac
        if not self.save_answers(False):
            vi_tri = cac_ma.index(self.de_dang_sua)
            self.ds_de.selection_clear(0, "end")
            self.ds_de.selection_set(vi_tri)
            return
        self.refresh_code_list(ma_moi)

    def show_answers(self, ma):
        # Dua dap an da luu cua ma de len bang chon
        self.de_dang_sua = ma
        self.nhan_de.configure(text="Đáp án mã đề " + ma)
        dap_an = self.thong_tin["cac_de"][ma]
        so_cau_da_nhap = 0
        tong_so_cau = 0
        for p in range(len(dap_an)):
            for gia_tri in dap_an[p]:
                tong_so_cau += 1
                if gia_tri != "":
                    so_cau_da_nhap += 1
        self.nhan_so_cau.configure(text="  ĐÃ NHẬP " + str(so_cau_da_nhap) + "/" + str(tong_so_cau) + " CÂU  ")
        cac_phan = self.mau["cac_phan"]
        for p in range(len(cac_phan)):
            for cau in range(cac_phan[p]["so_cau"]):
                gia_tri = ""
                if p < len(dap_an) and cau < len(dap_an[p]):
                    gia_tri = dap_an[p][cau]
                if cac_phan[p]["loai"] == "dung_sai":
                    for y in range(4):
                        if gia_tri == "":
                            self.bien_dap_an[p][cau][y].set("")
                        elif gia_tri[y] == "D":
                            self.bien_dap_an[p][cau][y].set("Đ")
                        else:
                            self.bien_dap_an[p][cau][y].set("S")
                else:
                    self.bien_dap_an[p][cau].set(gia_tri)

    def add_version(self):
        if not self.check_exam_selected():
            return
        ma = self.o_ma_de.get().strip()
        if len(ma) != 3 or not ma.isdigit():
            messagebox.showerror("Lỗi", "Mã đề phải gồm đúng 3 chữ số, ví dụ 101")
            return
        if ma in self.thong_tin["cac_de"]:
            messagebox.showerror("Lỗi", "Mã đề " + ma + " đã có")
            return
        if not self.save_answers(False):
            return
        dap_an = []
        for phan in self.mau["cac_phan"]:
            ds = []
            for cau in range(phan["so_cau"]):
                ds.append("")
            dap_an.append(ds)
        self.thong_tin["cac_de"][ma] = dap_an
        self.save_exam_data()
        self.o_ma_de.delete(0, "end")
        self.refresh_code_list(ma)
        self.update_header()

    def delete_version(self):
        if self.de_dang_sua == "":
            return
        if not messagebox.askyesno("Xóa đề", "Xóa mã đề " + self.de_dang_sua + "?"):
            return
        del self.thong_tin["cac_de"][self.de_dang_sua]
        self.de_dang_sua = ""
        self.save_exam_data()
        self.refresh_code_list("")
        self.update_header()

    def clear_answers(self):
        if self.mau is None:
            return
        cac_phan = self.mau["cac_phan"]
        for p in range(len(self.bien_dap_an)):
            for cau in range(len(self.bien_dap_an[p])):
                if cac_phan[p]["loai"] == "dung_sai":
                    for y in range(4):
                        self.bien_dap_an[p][cau][y].set("")
                else:
                    self.bien_dap_an[p][cau].set("")

    def quick_fill(self):
        # Dien chuoi ABCD vao phan ABCD dau tien, bo qua dau cach, dau _ la bo trong
        if self.mau is None:
            return
        chuoi = self.o_nhap_nhanh.get().upper().replace(" ", "")
        p = -1
        for i in range(len(self.mau["cac_phan"])):
            if self.mau["cac_phan"][i]["loai"] == "abcd":
                p = i
                break
        if p == -1:
            return
        so_cau = self.mau["cac_phan"][p]["so_cau"]
        if len(chuoi) > so_cau:
            messagebox.showerror("Lỗi", "Phần này chỉ có " + str(so_cau) + " câu, chuỗi đang có " + str(len(chuoi)) + " ký tự")
            return
        for i in range(len(chuoi)):
            c = chuoi[i]
            if c not in "ABCD_":
                messagebox.showerror("Lỗi", "Chỉ dùng chữ A, B, C, D và dấu _, gặp: " + c)
                return
        for i in range(len(chuoi)):
            if chuoi[i] == "_":
                self.bien_dap_an[p][i].set("")
            else:
                self.bien_dap_an[p][i].set(chuoi[i])

    def save_answers(self, thong_bao=True):
        # Luu dap an tren bang vao de dang sua. thong_bao=False: tu luu khi chuyen de, khong hien hop thoai "Da luu"
        # Tra ve False neu dap an nhap chua hop le
        if self.de_dang_sua == "" or self.mau is None:
            if thong_bao:
                messagebox.showinfo("Chưa chọn đề", "Hãy thêm hoặc chọn một mã đề")
            return True
        cac_phan = self.mau["cac_phan"]
        dap_an = []
        so_cau_co_dap_an = 0
        for p in range(len(cac_phan)):
            ds = []
            for cau in range(cac_phan[p]["so_cau"]):
                if cac_phan[p]["loai"] == "dung_sai":
                    # Cau dung/sai: chon du 4 y hoac bo trong ca cau
                    chuoi = ""
                    so_y = 0
                    for y in range(4):
                        gia_tri = self.bien_dap_an[p][cau][y].get()
                        if gia_tri == "Đ":
                            chuoi = chuoi + "D"
                            so_y += 1
                        elif gia_tri == "S":
                            chuoi = chuoi + "S"
                            so_y += 1
                    if so_y != 0 and so_y != 4:
                        messagebox.showerror("Lỗi", "Mã đề " + self.de_dang_sua + ", phần " + str(p + 1) + " câu " + str(cau + 1) + ": cần chọn đủ 4 ý a, b, c, d")
                        return False
                    ds.append(chuoi)
                elif cac_phan[p]["loai"] == "so":
                    chuoi = self.bien_dap_an[p][cau].get().strip().replace(".", ",")
                    if len(chuoi) > 4:
                        messagebox.showerror("Lỗi", "Phần " + str(p + 1) + " câu " + str(cau + 1) + ": số tối đa 4 ký tự")
                        return False
                    for c in chuoi:
                        if c not in "-,0123456789":
                            messagebox.showerror("Lỗi", "Phần " + str(p + 1) + " câu " + str(cau + 1) + ": chỉ dùng chữ số, dấu - và dấu phẩy")
                            return False
                    ds.append(chuoi)
                else:
                    ds.append(self.bien_dap_an[p][cau].get())
                if ds[-1] != "":
                    so_cau_co_dap_an += 1
            dap_an.append(ds)
        self.thong_tin["cac_de"][self.de_dang_sua] = dap_an
        self.save_exam_data()
        if thong_bao:
            self.refresh_code_list(self.de_dang_sua)
            messagebox.showinfo("Đã lưu", "Đã lưu đáp án mã đề " + self.de_dang_sua + " (" + str(so_cau_co_dap_an) + " câu có đáp án)")
        return True


    # =====================================================================
    # Ghi ket qua vao ky thi
    # =====================================================================
    def save_result(self, ten_anh, anh_goc, kq):
        # Luu anh (anh ket qua neu cham duoc, anh goc neu loi) va ghi 1 dong vao diem.csv cua ky thi
        thu_muc = os.path.join(THU_MUC_KY_THI, self.ky_thi)
        bay_gio = datetime.datetime.now()
        ten_luu = bay_gio.strftime("%Y%m%d_%H%M%S_%f") + "_" + os.path.splitext(ten_anh)[0] + ".jpg"
        duong_dan_anh = os.path.join(thu_muc, "images", ten_luu)
        if kq["anh_ket_qua"] is not None:
            cv2.imencode(".jpg", kq["anh_ket_qua"])[1].tofile(duong_dan_anh)
        else:
            anh_luu = anh_goc
            if anh_goc.shape[1] > 1600:
                anh_luu = cv2.resize(anh_goc, (1600, int(anh_goc.shape[0] * 1600 / anh_goc.shape[1])))
            cv2.imencode(".jpg", anh_luu)[1].tofile(duong_dan_anh)

        cac_phan = self.mau["cac_phan"]
        duong_dan_csv = os.path.join(thu_muc, "diem.csv")
        co_file = os.path.exists(duong_dan_csv)
        f = open(duong_dan_csv, "a", newline="", encoding="utf-8-sig")
        ghi = csv.writer(f)
        if not co_file:
            tieu_de = ["thoi_gian", "nguon", "ten_anh", "trang_thai", "sbd", "ma_de"]
            for p in range(len(cac_phan)):
                tieu_de.append("bai_lam P" + str(p + 1))
                tieu_de.append("diem P" + str(p + 1))
            tieu_de.append("tong_diem")
            tieu_de.append("cac_cau_sai")
            tieu_de.append("anh")
            ghi.writerow(tieu_de)
        # Cot nguon giu lai de doc duoc file diem.csv cu
        dong = [bay_gio.strftime("%Y-%m-%d %H:%M:%S"), "anh", ten_anh, kq["trang_thai"], kq["sbd"], kq["ma_de"]]
        for p in range(len(cac_phan)):
            if p < len(kq["bai_lam"]):
                dong.append(kq["bai_lam"][p])
            else:
                dong.append("")
            if p < len(kq["diem_phan"]):
                dong.append(kq["diem_phan"][p])
            else:
                dong.append("")
        if kq["trang_thai"] == "ok":
            dong.append(kq["tong_diem"])
        else:
            dong.append("")
        dong.append(kq["cau_sai"])
        dong.append(ten_luu)
        ghi.writerow(dong)
        f.close()
        return duong_dan_anh

    def translate_status(self, trang_thai):
        if trang_thai == "ok":
            return "OK"
        if trang_thai in DICH_LOI:
            return DICH_LOI[trang_thai]
        if trang_thai.startswith("loi: khong co dap an cho ma de"):
            return "Chưa có đáp án cho mã đề " + trang_thai.replace("loi: khong co dap an cho ma de", "").strip()
        return trang_thai

    def show_image(self, nhan, anh, rong_toi_da, cao_toi_da):
        # Hien anh OpenCV (BGR) len 1 CTkLabel, giu ti le, vua khung rong_toi_da x cao_toi_da
        if rong_toi_da < 50 or cao_toi_da < 50:
            rong_toi_da = 600
            cao_toi_da = 600
        h = anh.shape[0]
        w = anh.shape[1]
        ti_le = min(rong_toi_da / w, cao_toi_da / h)
        rong = max(1, int(w * ti_le))
        cao = max(1, int(h * ti_le))
        anh_nho = cv2.resize(anh, (rong, cao), interpolation=cv2.INTER_AREA)
        anh_pil = Image.fromarray(cv2.cvtColor(anh_nho, cv2.COLOR_BGR2RGB))
        anh_ctk = ctk.CTkImage(light_image=anh_pil, size=(rong, cao))
        nhan.configure(image=anh_ctk, text="")
        # Giu tham chieu toi anh, neu khong Python se xoa anh va o hien thi bi trong
        nhan.anh_giu = anh_ctk


    # =====================================================================
    # Tab 2: Cham bai
    # =====================================================================
    def build_grading_tab(self):
        self.tab_anh.grid_columnconfigure(0, weight=3, uniform="cot")
        self.tab_anh.grid_columnconfigure(1, weight=2, uniform="cot")
        self.tab_anh.grid_rowconfigure(1, weight=1)

        thanh = ctk.CTkFrame(self.tab_anh, fg_color=THE, corner_radius=12, border_width=1, border_color=VIEN)
        thanh.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        ctk.CTkButton(thanh, text="Chọn ảnh...", command=self.choose_images, height=44, width=140, corner_radius=8, font=(FONT, 14, "bold"),
                      fg_color="transparent", text_color=XANH_DAM, border_width=1, border_color=XANH_DAM, hover_color=NEN_MENU).pack(side="left", padx=20, pady=18)
        self.nhan_so_anh = ctk.CTkLabel(thanh, text="Chưa chọn ảnh", font=(FONT, 14), text_color=XAM_CHU)
        self.nhan_so_anh.pack(side="left")
        self.nut_cham_anh = ctk.CTkButton(thanh, text="Chấm bài", image=draw_icon("cham", "#FFFFFF", 18), compound="left", command=self.grade_images,
                                          height=44, width=150, corner_radius=8, font=(FONT, 15, "bold"), fg_color=XANH_DAM, hover_color=XANH_DAM_HOVER)
        self.nut_cham_anh.pack(side="right", padx=20)
        self.thanh_tien_do = ctk.CTkProgressBar(thanh, width=240, height=8, corner_radius=4, progress_color=XANH_LA, fg_color=NEN_MENU)
        self.thanh_tien_do.set(0)
        self.thanh_tien_do.pack(side="right", padx=8)

        # Ben trai: anh ket qua lon
        khung_anh = ctk.CTkFrame(self.tab_anh, fg_color=THE, corner_radius=12, border_width=1, border_color=VIEN)
        khung_anh.grid(row=1, column=0, sticky="nsew", padx=(0, 20))
        self.nhan_anh_kq = ctk.CTkLabel(khung_anh, text="Chọn ảnh rồi bấm Chấm bài.\nBấm vào một dòng bên phải để xem ảnh kết quả.",
                                        font=(FONT, 15), text_color=XAM)
        self.nhan_anh_kq.pack(fill="both", expand=True, padx=14, pady=14)

        # Ben phai: bang ket qua va chi tiet
        khung_bang = ctk.CTkFrame(self.tab_anh, fg_color=THE, corner_radius=12, border_width=1, border_color=VIEN)
        khung_bang.grid(row=1, column=1, sticky="nsew")
        ctk.CTkLabel(khung_bang, text="Kết quả", font=(FONT, 20, "bold"), text_color=XANH_DAM).pack(anchor="w", padx=24, pady=(20, 0))
        ctk.CTkLabel(khung_bang, text="Bấm vào một dòng để xem ảnh và chi tiết", font=(FONT, 13), text_color=XAM_CHU).pack(anchor="w", padx=24, pady=(0, 12))
        # O chi tiet dat o day duoi truoc de bang khong chiem het cho
        self.chi_tiet_anh = ctk.CTkTextbox(khung_bang, height=140, corner_radius=8, font=(FONT, 13), fg_color=NEN, border_width=1,
                                           border_color=VIEN, text_color=XANH_DAM, wrap="word")
        self.chi_tiet_anh.pack(side="bottom", fill="x", padx=18, pady=18)
        self.bang_anh = ttk.Treeview(khung_bang, columns=("anh", "sbd", "made", "diem", "tt"), show="headings", height=6)
        cac_cot = [["anh", "ẢNH", 110], ["sbd", "SBD", 75], ["made", "MÃ ĐỀ", 65], ["diem", "ĐIỂM", 60], ["tt", "TRẠNG THÁI", 120]]
        for cot in cac_cot:
            self.bang_anh.heading(cot[0], text=cot[1], anchor="w")
            if cot[0] == "tt" or cot[0] == "anh":
                self.bang_anh.column(cot[0], width=cot[2], minwidth=60, stretch=True)
            else:
                self.bang_anh.column(cot[0], width=cot[2], minwidth=50, stretch=False)
        self.bang_anh.tag_configure("loi", foreground=DO_DAM)
        self.bang_anh.tag_configure("dung", foreground=XANH_LA_CHU)
        self.bang_anh.pack(fill="both", expand=True, padx=18)
        self.bang_anh.bind("<<TreeviewSelect>>", self.select_result_row)

    def choose_images(self):
        cac_file = filedialog.askopenfilenames(title="Chọn ảnh phiếu", filetypes=[("Ảnh", "*.jpg *.jpeg *.png"), ("Tất cả", "*.*")])
        if len(cac_file) == 0:
            return
        self.anh_da_chon = list(cac_file)
        self.nhan_so_anh.configure(text="Đã chọn " + str(len(self.anh_da_chon)) + " ảnh")

    def grade_images(self):
        if not self.check_exam_selected():
            return
        if len(self.thong_tin["cac_de"]) == 0:
            messagebox.showinfo("Chưa có đáp án", "Hãy thêm mã đề và đáp án ở mục Đề & đáp án")
            return
        if len(self.anh_da_chon) == 0:
            messagebox.showinfo("Chưa chọn ảnh", "Hãy bấm Chọn ảnh...")
            return
        self.nut_cham_anh.configure(state="disabled")
        for i in range(len(self.anh_da_chon)):
            duong_dan = self.anh_da_chon[i]
            ten_anh = os.path.basename(duong_dan)
            # Doc anh bang imdecode de doc duoc duong dan co dau tieng Viet
            du_lieu = np.fromfile(duong_dan, dtype=np.uint8)
            anh = cv2.imdecode(du_lieu, cv2.IMREAD_COLOR)
            if anh is None:
                kq = {"trang_thai": "loi: khong doc duoc anh", "sbd": "", "ma_de": "", "bai_lam": [], "diem_phan": [],
                      "tong_diem": 0, "cau_sai": "", "anh_ket_qua": None}
                anh = np.full((200, 200, 3), 255, dtype=np.uint8)
            else:
                kq = grade_image(anh, self.mau, self.thong_tin["cac_de"])
            duong_dan_luu = self.save_result(ten_anh, anh, kq)
            kq["duong_dan_luu"] = duong_dan_luu
            kq["ten_anh"] = ten_anh
            self.ket_qua_anh.append(kq)
            diem = ""
            the = ()
            trang_thai = self.translate_status(kq["trang_thai"])
            if kq["trang_thai"] == "ok":
                diem = str(kq["tong_diem"])
                the = ("dung",)
            else:
                the = ("loi",)
            self.bang_anh.insert("", "end", iid=str(len(self.ket_qua_anh) - 1), values=(ten_anh, kq["sbd"], kq["ma_de"], diem, trang_thai), tags=the)
            self.thanh_tien_do.set((i + 1) / len(self.anh_da_chon))
            self.update()
        self.nut_cham_anh.configure(state="normal")
        cac_dong = self.bang_anh.get_children()
        self.bang_anh.selection_set(cac_dong[-1])
        self.bang_anh.see(cac_dong[-1])

    def select_result_row(self, su_kien):
        chon = self.bang_anh.selection()
        if len(chon) == 0:
            return
        kq = self.ket_qua_anh[int(chon[0])]
        anh = cv2.imdecode(np.fromfile(kq["duong_dan_luu"], dtype=np.uint8), cv2.IMREAD_COLOR)
        self.update_idletasks()
        self.show_image(self.nhan_anh_kq, anh, self.nhan_anh_kq.winfo_width() - 16, self.nhan_anh_kq.winfo_height() - 16)
        noi_dung = "Ảnh: " + kq["ten_anh"] + "\n"
        noi_dung = noi_dung + "SBD: " + kq["sbd"] + "    Mã đề: " + kq["ma_de"] + "\n"
        if kq["trang_thai"] == "ok":
            noi_dung = noi_dung + "Điểm: " + str(kq["tong_diem"])
            if len(kq["diem_phan"]) > 1:
                noi_dung = noi_dung + "   (Từng phần:"
                for d in kq["diem_phan"]:
                    noi_dung = noi_dung + " " + str(d)
                noi_dung = noi_dung + ")"
            noi_dung = noi_dung + "\nCâu sai: " + kq["cau_sai"]
        else:
            noi_dung = noi_dung + "Lỗi: " + self.translate_status(kq["trang_thai"])
        self.chi_tiet_anh.delete("1.0", "end")
        self.chi_tiet_anh.insert("1.0", noi_dung)


    # =====================================================================
    # Tab 3: Thong ke
    # =====================================================================
    def build_stats_tab(self):
        self.tab_tk.grid_columnconfigure(0, weight=1)
        self.tab_tk.grid_rowconfigure(1, weight=1)

        # Hang the so lieu: bieu tuong, nhan nho o goc, ten, so lon, ghi chu nghieng
        hang_the = ctk.CTkFrame(self.tab_tk, fg_color="transparent")
        hang_the.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        cac_the = [
            ["phieu", TIM, TIM_NEN, "Số phiếu đã chấm"],
            ["dung", XANH_LA_CHU, XANH_LA_NEN, "Thí sinh hợp lệ"],
            ["loi", DO_DAM, DO_NEN, "Phiếu lỗi"],
            ["diem", XANH_DUONG, XANH_DUONG_NEN, "Điểm trung bình"],
        ]
        self.the_so_lieu = []
        self.the_nhan_goc = []
        self.the_ghi_chu = []
        for i in range(len(cac_the)):
            hang_the.grid_columnconfigure(i, weight=1, uniform="the")
            the = ctk.CTkFrame(hang_the, fg_color=THE, corner_radius=12, border_width=1, border_color=VIEN, height=186)
            if i < len(cac_the) - 1:
                the.grid(row=0, column=i, sticky="ew", padx=(0, 16))
            else:
                the.grid(row=0, column=i, sticky="ew")
            the.pack_propagate(False)
            dong_tren = ctk.CTkFrame(the, fg_color="transparent")
            dong_tren.pack(fill="x", padx=24, pady=(24, 0))
            ctk.CTkLabel(dong_tren, text="", image=draw_icon(cac_the[i][0], cac_the[i][1], 24), width=48, height=48,
                         fg_color=cac_the[i][2], corner_radius=8).pack(side="left")
            nhan_goc = ctk.CTkLabel(dong_tren, text="", font=(FONT, 11, "bold"), text_color=cac_the[i][1], fg_color=cac_the[i][2], corner_radius=4, height=24)
            nhan_goc.pack(side="right", anchor="n")
            self.the_nhan_goc.append(nhan_goc)
            ctk.CTkLabel(the, text=cac_the[i][3], font=(FONT, 15), text_color=XANH_DAM, height=22).pack(anchor="w", padx=24, pady=(14, 0))
            gia_tri = ctk.CTkLabel(the, text="--", font=(FONT, 30, "bold"), text_color=XANH_DAM, height=38)
            gia_tri.pack(anchor="w", padx=24)
            self.the_so_lieu.append(gia_tri)
            ghi_chu = ctk.CTkLabel(the, text="", font=(FONT, 12, "italic"), text_color=XAM, height=18)
            ghi_chu.pack(anchor="w", padx=24)
            self.the_ghi_chu.append(ghi_chu)

        # Bang tat ca ket qua
        khung_bang = ctk.CTkFrame(self.tab_tk, fg_color=THE, corner_radius=12, border_width=1, border_color=VIEN)
        khung_bang.grid(row=1, column=0, sticky="nsew")
        thanh = ctk.CTkFrame(khung_bang, fg_color="transparent")
        thanh.pack(fill="x", padx=28, pady=(22, 14))
        chu_thanh = ctk.CTkFrame(thanh, fg_color="transparent")
        chu_thanh.pack(side="left")
        ctk.CTkLabel(chu_thanh, text="Tất cả phiếu đã chấm", font=(FONT, 22, "bold"), text_color=XANH_DAM, height=28).pack(anchor="w")
        self.nhan_ghi_chu_tk = ctk.CTkLabel(chu_thanh, text="Kết quả gộp từ mọi lần chấm của kỳ thi", font=(FONT, 13), text_color=XAM_CHU, height=20)
        self.nhan_ghi_chu_tk.pack(anchor="w")
        ctk.CTkButton(thanh, text="Tải file điểm (CSV)", image=draw_icon("tai", XANH_LA, 16), compound="left", command=self.export_csv,
                      height=40, corner_radius=8, font=(FONT, 15, "bold"), fg_color="transparent", text_color=XANH_LA,
                      hover_color=XANH_LA_NEN).pack(side="right")
        ctk.CTkButton(thanh, text="Làm mới", command=self.refresh_stats, height=40, width=100, corner_radius=8, font=(FONT, 14, "bold"),
                      fg_color="transparent", text_color=XAM_CHU, hover_color=NEN_MENU).pack(side="right", padx=8)
        self.bang_tk = ttk.Treeview(khung_bang, columns=("tg", "anh", "sbd", "made", "diem", "tt"), show="headings")
        cac_cot = [["tg", "THỜI GIAN", 170], ["anh", "ẢNH", 200], ["sbd", "SBD", 90], ["made", "MÃ ĐỀ", 80], ["diem", "ĐIỂM", 90], ["tt", "TRẠNG THÁI", 400]]
        for cot in cac_cot:
            self.bang_tk.heading(cot[0], text=cot[1], anchor="w")
            self.bang_tk.column(cot[0], width=cot[2])
        self.bang_tk.tag_configure("dung", foreground=XANH_DAM)
        self.bang_tk.tag_configure("loi", foreground=DO_DAM)
        self.bang_tk.tag_configure("trung", foreground=XAM_NHAT)
        self.bang_tk.pack(fill="both", expand=True, padx=2, pady=(0, 16))

    def refresh_stats(self):
        for dong in self.bang_tk.get_children():
            self.bang_tk.delete(dong)
        if self.thong_tin is None:
            return
        duong_dan_csv = os.path.join(THU_MUC_KY_THI, self.ky_thi, "diem.csv")
        cac_dong = []
        if os.path.exists(duong_dan_csv):
            f = open(duong_dan_csv, encoding="utf-8-sig")
            doc = csv.DictReader(f)
            for dong in doc:
                cac_dong.append(dong)
            f.close()

        # Moi SBD chi tinh lan cham moi nhat (giao vien co the cham lai 1 phieu nhieu lan)
        lan_moi_nhat = {}
        for i in range(len(cac_dong)):
            dong = cac_dong[i]
            if dong["trang_thai"] == "ok":
                lan_moi_nhat[dong["sbd"]] = i
        cac_diem = []
        so_loi = 0
        so_trung = 0
        for i in range(len(cac_dong)):
            dong = cac_dong[i]
            the = ()
            diem = dong["tong_diem"]
            if dong["trang_thai"] != "ok":
                so_loi += 1
                the = ("loi",)
            elif lan_moi_nhat[dong["sbd"]] != i:
                so_trung += 1
                the = ("trung",)
                diem = diem + " (cũ)"
            else:
                the = ("dung",)
                cac_diem.append(float(dong["tong_diem"]))
            trang_thai = self.translate_status(dong["trang_thai"])
            if the == ("trung",):
                trang_thai = "OK (lần chấm cũ)"
            self.bang_tk.insert("", 0, values=(dong["thoi_gian"], dong["ten_anh"], dong["sbd"], dong["ma_de"], diem, trang_thai), tags=the)

        # Dien so lieu vao 4 the
        tong = len(cac_dong)
        self.the_so_lieu[0].configure(text=str(tong))
        self.the_nhan_goc[0].configure(text="  " + str(so_trung) + " CHẤM LẠI  ")
        self.the_ghi_chu[0].configure(text="gồm cả các lần chấm lại")
        self.the_so_lieu[1].configure(text=str(len(cac_diem)))
        self.the_nhan_goc[1].configure(text="  THEO SBD  ")
        self.the_ghi_chu[1].configure(text="mỗi SBD tính lần chấm mới nhất")
        self.the_so_lieu[2].configure(text=str(so_loi))
        if tong > 0:
            self.the_nhan_goc[2].configure(text="  " + str(round(so_loi * 100 / tong)) + "%  ")
        else:
            self.the_nhan_goc[2].configure(text="  0%  ")
        self.the_ghi_chu[2].configure(text="cần chụp lại cho thẳng")
        self.the_nhan_goc[3].configure(text="  THANG 10  ")
        if len(cac_diem) > 0:
            self.the_so_lieu[3].configure(text=str(round(sum(cac_diem) / len(cac_diem), 2)))
            self.the_ghi_chu[3].configure(text="cao nhất " + str(max(cac_diem)) + "  ·  thấp nhất " + str(min(cac_diem)))
        else:
            self.the_so_lieu[3].configure(text="--")
            self.the_ghi_chu[3].configure(text="chưa có điểm")
        if so_trung > 0:
            self.nhan_ghi_chu_tk.configure(text="Kết quả gộp từ mọi lần chấm. " + str(so_trung) + " phiếu chấm trùng SBD, chỉ tính lần mới nhất")
        else:
            self.nhan_ghi_chu_tk.configure(text="Kết quả gộp từ mọi lần chấm của kỳ thi")

    def export_csv(self):
        if not self.check_exam_selected():
            return
        duong_dan_csv = os.path.join(THU_MUC_KY_THI, self.ky_thi, "diem.csv")
        if not os.path.exists(duong_dan_csv):
            messagebox.showinfo("Chưa có điểm", "Kỳ thi này chưa chấm phiếu nào")
            return
        noi_luu = filedialog.asksaveasfilename(title="Lưu file điểm", defaultextension=".csv", initialfile="diem_" + self.ky_thi + ".csv",
                                               filetypes=[("CSV", "*.csv")])
        if noi_luu == "":
            return
        shutil.copyfile(duong_dan_csv, noi_luu)
        messagebox.showinfo("Đã lưu", "Đã lưu file điểm vào:\n" + noi_luu)


    # =====================================================================
    # Chuyen tab
    # =====================================================================
    def update_header(self):
        # Tieu de lon: ten tab. Dong duoi: mau phieu va so ma de cua ky thi, phan mau xanh la trang thai
        if self.tab_dang_mo == "de":
            self.nhan_tieu_de.configure(text="Đề & đáp án")
        elif self.tab_dang_mo == "anh":
            self.nhan_tieu_de.configure(text="Chấm bài")
        else:
            self.nhan_tieu_de.configure(text="Thống kê")
        if self.thong_tin is None:
            self.nhan_phu_de.configure(text="Chưa có kỳ thi — ")
            self.nhan_trang_thai_de.configure(text="bấm Tạo kỳ thi để bắt đầu", text_color=XANH_LA)
            self.nhan_ky_thi_menu.configure(text="Chưa có kỳ thi")
            self.nhan_mau_menu.configure(text="")
            return
        ten_mau = self.thong_tin["mau"].replace("Mau", "Mẫu").replace("cau", "câu").replace("phan", "phần")
        so_de = len(self.thong_tin["cac_de"])
        self.nhan_phu_de.configure(text=self.ky_thi + "  ·  " + ten_mau + " — ")
        if so_de == 0:
            self.nhan_trang_thai_de.configure(text="chưa có mã đề", text_color=VANG_CHU)
        else:
            self.nhan_trang_thai_de.configure(text=str(so_de) + " mã đề sẵn sàng chấm", text_color=XANH_LA)
        self.nhan_ky_thi_menu.configure(text=self.ky_thi)
        self.nhan_mau_menu.configure(text=ten_mau)

    def show_tab(self, ten):
        # An tab cu, hien tab moi va to mau nut menu cua tab dang mo
        if self.tab_dang_mo == "de" and ten != "de":
            self.save_answers(False)
        self.tab_de.pack_forget()
        self.tab_anh.pack_forget()
        self.tab_tk.pack_forget()
        cac_nut = [[self.nut_tab_de, "de"], [self.nut_tab_anh, "anh"], [self.nut_tab_tk, "tk"]]
        for nut in cac_nut:
            if nut[1] == ten:
                nut[0].configure(fg_color=VIEN, text_color=XANH_DAM, hover_color=VIEN, font=(FONT, 15, "bold"), image=self.bieu_tuong_menu[nut[1]][1])
            else:
                nut[0].configure(fg_color="transparent", text_color=XAM_CHU, hover_color=VIEN, font=(FONT, 15), image=self.bieu_tuong_menu[nut[1]][0])
        if ten == "de":
            self.tab_de.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        elif ten == "anh":
            self.tab_anh.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        else:
            self.tab_tk.pack(fill="both", expand=True, padx=24, pady=(0, 24))
            self.refresh_stats()
        self.tab_dang_mo = ten
        self.update_header()

    def maximize(self):
        self.state("zoomed")

    def open_answer_tab(self):
        self.show_tab("de")

    def open_grading_tab(self):
        self.show_tab("anh")

    def open_stats_tab(self):
        self.show_tab("tk")

    def on_close(self):
        if self.tab_dang_mo == "de":
            self.save_answers(False)
        self.destroy()


if __name__ == "__main__":
    ung_dung = App()
    ung_dung.mainloop()
