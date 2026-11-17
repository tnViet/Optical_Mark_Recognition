# Tao anh test gia lap cho tung mau phieu: to dap an, sbd, ma de roi lam nghieng, phoi canh, them bong, nhieu
# Chay: python tao_anh_test.py  -> tao anh trong thu muc anh_test
# File anh_test/bai_lam_that.csv ghi bai lam that cua tung anh de doi chieu voi ket qua cham
import os
import csv
import cv2
import numpy as np
from cau_hinh import CHU, DANH_SACH_MAU

os.makedirs("anh_test", exist_ok=True)
np.random.seed(1)

# Kich thuoc anh chup gia lap
ANH_RONG = 2200
ANH_CAO = 2900

# Vi tri 4 goc phieu tren anh chup (gia lap 3 kieu chup nghieng): tren trai, tren phai, duoi trai, duoi phai
cac_goc = [
    [[300, 250], [1900, 320], [200, 2500], [2000, 2450]],
    [[450, 180], [1850, 420], [150, 2300], [1750, 2650]],
    [[250, 400], [1950, 200], [350, 2600], [2100, 2500]],
]

bang_bai_lam = []

for ten_mau in DANH_SACH_MAU:
    mau = DANH_SACH_MAU[ten_mau]
    phieu_goc = cv2.imread(mau["file"])
    if phieu_goc is None:
        print("Khong doc duoc " + mau["file"])
        continue
    rong = phieu_goc.shape[1]
    cao = phieu_goc.shape[0]
    so_cot_sbd = len(mau["sbd_x"])
    so_cot_ma_de = len(mau["ma_de_x"])

    for n in range(3):
        phieu = phieu_goc.copy()
        mau_but = int(np.random.randint(30, 90))

        # To so bao danh va ma de ngau nhien
        sbd = ""
        for cot in range(so_cot_sbd):
            so = int(np.random.randint(0, 10))
            sbd = sbd + str(so)
            r = mau["ban_kinh_so"] - 1
            cv2.circle(phieu, (mau["sbd_x"][cot], mau["sbd_y"][so]), r, (mau_but, mau_but, mau_but), -1)
        ma_de = ""
        for cot in range(so_cot_ma_de):
            so = int(np.random.randint(0, 10))
            ma_de = ma_de + str(so)
            r = mau["ban_kinh_so"] - 1
            cv2.circle(phieu, (mau["ma_de_x"][cot], mau["ma_de_y"][so]), r, (mau_but, mau_but, mau_but), -1)

        # To dap an: phan lon to 1 o, mot so cau bo trong hoac to 2 o
        bai_lam = ""
        for khoi in mau["khoi_cau"]:
            for dong in range(len(khoi["y"])):
                xac_suat = np.random.rand()
                if xac_suat < 0.05:
                    bai_lam = bai_lam + "-"
                    continue
                cac_o = [int(np.random.randint(0, 4))]
                if xac_suat > 0.97:
                    o_thu_hai = (cac_o[0] + 1 + int(np.random.randint(0, 3))) % 4
                    cac_o.append(o_thu_hai)
                    bai_lam = bai_lam + "X"
                else:
                    bai_lam = bai_lam + CHU[cac_o[0]]
                for j in cac_o:
                    # Vet to lech va to nho hon o mot chut cho giong to tay
                    lech_x = int(np.random.randint(-2, 3))
                    lech_y = int(np.random.randint(-2, 3))
                    r = mau["ban_kinh"] - int(np.random.randint(0, 3))
                    tam = (khoi["x"][j] + lech_x, khoi["y"][dong] + lech_y)
                    cv2.circle(phieu, tam, r, (mau_but, mau_but, mau_but), -1)

        # Dat phieu len nen theo goc nghieng, phoi canh
        diem_phieu = np.float32([[0, 0], [rong, 0], [0, cao], [rong, cao]])
        diem_anh = np.float32(cac_goc[n])
        ma_tran = cv2.getPerspectiveTransform(diem_phieu, diem_anh)
        nen = np.full((ANH_CAO, ANH_RONG, 3), 90, dtype=np.uint8)
        anh = cv2.warpPerspective(phieu, ma_tran, (ANH_RONG, ANH_CAO), dst=nen, borderMode=cv2.BORDER_TRANSPARENT)

        # Them bong do: toi dan tu trai sang phai
        bong = np.zeros((ANH_CAO, ANH_RONG), dtype=np.float32)
        for x in range(ANH_RONG):
            bong[:, x] = 1.0 - 0.45 * x / ANH_RONG
        anh = anh.astype(np.float32)
        for k in range(3):
            anh[:, :, k] = anh[:, :, k] * bong

        # Them nhieu va lam mo nhe
        nhieu = np.random.normal(0, 8, anh.shape)
        anh = np.clip(anh + nhieu, 0, 255).astype(np.uint8)
        anh = cv2.GaussianBlur(anh, (5, 5), 0)

        ten_mau_file = os.path.splitext(os.path.basename(mau["file"]))[0]
        ten_anh = ten_mau_file + "_test_" + str(n + 1) + ".jpg"
        cv2.imwrite("anh_test/" + ten_anh, anh)
        bang_bai_lam.append([ten_anh, ten_mau, sbd, ma_de, bai_lam])
        print("Da tao anh_test/" + ten_anh)

f = open("anh_test/bai_lam_that.csv", "w", newline="", encoding="utf-8-sig")
ghi = csv.writer(f)
ghi.writerow(["ten_anh", "mau_phieu", "sbd", "ma_de", "bai_lam"])
for dong in bang_bai_lam:
    ghi.writerow(dong)
f.close()
