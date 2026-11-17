# Tao anh test gia lap cho tung mau phieu: to bai lam, sbd, ma de roi lam nghieng, phoi canh, them bong, nhieu
# Chay: python tao_anh_test.py  -> tao anh trong thu muc anh_test
# File anh_test/bai_lam_that.csv ghi bai lam that cua tung anh de doi chieu voi ket qua cham
# (cac phan cach nhau dau |, cung cach ghi voi cot bai_lam trong ket_qua/diem.csv)
import os
import csv
import cv2
import numpy as np
from cau_hinh import DANH_SACH_MAU

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
    cac_phan = mau["cac_phan"]
    phieu_goc = cv2.imread(mau["file"])
    if phieu_goc is None:
        print("Khong doc duoc " + mau["file"])
        continue
    rong = phieu_goc.shape[1]
    cao = phieu_goc.shape[0]

    for n in range(3):
        phieu = phieu_goc.copy()
        mau_but = int(np.random.randint(30, 90))

        # bai_lam[p][cau] la bai lam that cua cau, ghi giong cach app ghi
        bai_lam = []
        for phan in cac_phan:
            ds = []
            for cau in range(phan["so_cau"]):
                ds.append("")
            bai_lam.append(ds)
        sbd = ""
        ma_de = ""

        for nhom in mau["cac_nhom"]:
            cac_o = nhom["cac_o"]
            p = nhom["phan"]
            xac_suat = np.random.rand()

            # Chon cac o se to trong nhom
            cac_o_to = []
            if p < 0:
                cac_o_to.append(int(np.random.randint(0, len(cac_o))))
            elif cac_phan[p]["loai"] == "so":
                # Cot dien so: co the bo trong
                if xac_suat > 0.25:
                    cac_o_to.append(int(np.random.randint(0, len(cac_o))))
            else:
                if xac_suat < 0.05:
                    cac_o_to = []
                elif xac_suat > 0.97:
                    o_1 = int(np.random.randint(0, len(cac_o)))
                    o_2 = (o_1 + 1 + int(np.random.randint(0, len(cac_o) - 1))) % len(cac_o)
                    cac_o_to = [o_1, o_2]
                else:
                    cac_o_to.append(int(np.random.randint(0, len(cac_o))))

            # Ket qua cua nhom
            if len(cac_o_to) == 0:
                kq = "_"
            elif len(cac_o_to) > 1:
                kq = "X"
            else:
                kq = cac_o[cac_o_to[0]][3]
            if p == -1:
                sbd = sbd + kq
            elif p == -2:
                ma_de = ma_de + kq
            elif cac_phan[p]["loai"] == "so":
                if kq != "_":
                    bai_lam[p][nhom["cau"]] += kq
            else:
                bai_lam[p][nhom["cau"]] += kq

            # To len phieu: vet to lech va nho hon o mot chut cho giong to tay
            for j in cac_o_to:
                x = cac_o[j][0] + int(np.random.randint(-2, 3))
                y = cac_o[j][1] + int(np.random.randint(-2, 3))
                r = cac_o[j][2] - int(np.random.randint(0, 3))
                cv2.circle(phieu, (x, y), r, (mau_but, mau_but, mau_but), -1)

        # Cau dien so bo trong ca 4 cot ghi la "_"
        for p in range(len(cac_phan)):
            for cau in range(len(bai_lam[p])):
                if bai_lam[p][cau] == "":
                    bai_lam[p][cau] = "_"

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

        chuoi_bai_lam = ""
        for p in range(len(cac_phan)):
            if cac_phan[p]["loai"] == "abcd":
                chuoi_bai_lam = chuoi_bai_lam + "".join(bai_lam[p])
            else:
                chuoi_bai_lam = chuoi_bai_lam + " ".join(bai_lam[p])
            if p < len(cac_phan) - 1:
                chuoi_bai_lam = chuoi_bai_lam + "|"
        bang_bai_lam.append([ten_anh, ten_mau, sbd, ma_de, chuoi_bai_lam])
        print("Da tao anh_test/" + ten_anh)

f = open("anh_test/bai_lam_that.csv", "w", newline="", encoding="utf-8-sig")
ghi = csv.writer(f)
ghi.writerow(["ten_anh", "mau_phieu", "sbd", "ma_de", "bai_lam"])
for dong in bang_bai_lam:
    ghi.writerow(dong)
f.close()
