# Thuat toan cham phieu, duoc goi tu giao dien app.py
# find_corners: tim 4 o vuong den o 4 goc phieu
# grade_image: nan phieu, doc o to, tra dap an theo ma de va tinh diem
import cv2
import numpy as np
from templates import NGUONG_TO

# Ti le cao/rong cua tu giac 4 goc duoc phep lech toi da 30% so voi phieu mau
SAI_LECH_TI_LE = 0.3


def find_corners(anh, mau):
    # Tra ve [goc, loi]
    # goc: 4 diem (tren trai, tren phai, duoi trai, duoi phai) tren anh goc, None neu khong tim duoc
    # loi: chuoi mo ta loi, "" neu tim duoc

    # Thu nho anh (chieu rong 1000) de tim phieu cho nhanh
    ti_le = anh.shape[1] / 1000
    anh_nho = cv2.resize(anh, (1000, int(anh.shape[0] / ti_le)))

    xam = cv2.cvtColor(anh_nho, cv2.COLOR_BGR2GRAY)
    mo = cv2.GaussianBlur(xam, (5, 5), 0)
    nguong = cv2.adaptiveThreshold(mo, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 51, 15)
    contours, _ = cv2.findContours(nguong, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    dien_tich_anh = anh_nho.shape[0] * anh_nho.shape[1]

    # Giu lai contour 4 dinh, gan vuong, ben trong to den. Moi phan tu: [dien tich, x tam, y tam]
    markers = []
    for c in contours:
        dien_tich = cv2.contourArea(c)
        if dien_tich < 30 or dien_tich > 0.01 * dien_tich_anh:
            continue
        chu_vi = cv2.arcLength(c, True)
        xap_xi = cv2.approxPolyDP(c, 0.04 * chu_vi, True)
        if len(xap_xi) != 4:
            continue
        (cx, cy), (w, h), _ = cv2.minAreaRect(c)
        if w == 0 or h == 0:
            continue
        if w / h < 0.7 or w / h > 1.3:
            continue
        if dien_tich / (w * h) < 0.75:
            continue
        x, y, w, h = cv2.boundingRect(c)
        giua = nguong[y + h // 4:y + h - h // 4, x + w // 4:x + w - w // 4]
        if giua.size == 0 or cv2.countNonZero(giua) / giua.size < 0.8:
            continue
        markers.append([dien_tich, cx, cy])

    if len(markers) < 4:
        return [None, "khong tim du 4 o goc"]

    # Chi giu cac o vuong lon (o goc to hon cac o vuong nho canh cot cau hoi)
    markers.sort(reverse=True)
    dien_tich_lon_nhat = markers[0][0]
    cac_o_lon = []
    for m in markers:
        if m[0] >= 0.5 * dien_tich_lon_nhat:
            cac_o_lon.append(m)

    # 4 goc la 4 o nam ngoai cung
    tren_trai = cac_o_lon[0]
    duoi_phai = cac_o_lon[0]
    tren_phai = cac_o_lon[0]
    duoi_trai = cac_o_lon[0]
    for m in cac_o_lon:
        if m[1] + m[2] < tren_trai[1] + tren_trai[2]:
            tren_trai = m
        if m[1] + m[2] > duoi_phai[1] + duoi_phai[2]:
            duoi_phai = m
        if m[1] - m[2] > tren_phai[1] - tren_phai[2]:
            tren_phai = m
        if m[1] - m[2] < duoi_trai[1] - duoi_trai[2]:
            duoi_trai = m

    if tren_trai == tren_phai or tren_trai == duoi_trai or duoi_phai == tren_phai or duoi_phai == duoi_trai:
        return [None, "khong tim du 4 o goc"]

    goc = np.float32([
        [tren_trai[1] * ti_le, tren_trai[2] * ti_le],
        [tren_phai[1] * ti_le, tren_phai[2] * ti_le],
        [duoi_trai[1] * ti_le, duoi_trai[2] * ti_le],
        [duoi_phai[1] * ti_le, duoi_phai[2] * ti_le],
    ])

    # Kiem tra ti le cao/rong cua tu giac so voi phieu mau.
    # Neu chon nham o vuong o giua mep phieu thi ti le se lech nhieu.
    goc_mau = mau["goc"]
    rong_mau = goc_mau[1][0] - goc_mau[0][0]
    cao_mau = goc_mau[2][1] - goc_mau[0][1]
    canh_tren = ((goc[1][0] - goc[0][0]) ** 2 + (goc[1][1] - goc[0][1]) ** 2) ** 0.5
    canh_duoi = ((goc[3][0] - goc[2][0]) ** 2 + (goc[3][1] - goc[2][1]) ** 2) ** 0.5
    canh_trai = ((goc[2][0] - goc[0][0]) ** 2 + (goc[2][1] - goc[0][1]) ** 2) ** 0.5
    canh_phai = ((goc[3][0] - goc[1][0]) ** 2 + (goc[3][1] - goc[1][1]) ** 2) ** 0.5
    if canh_tren + canh_duoi == 0:
        return [None, "khong tim du 4 o goc"]
    ti_le_anh = (canh_trai + canh_phai) / (canh_tren + canh_duoi)
    ti_le_mau = cao_mau / rong_mau
    if ti_le_anh < ti_le_mau * (1 - SAI_LECH_TI_LE) or ti_le_anh > ti_le_mau * (1 + SAI_LECH_TI_LE):
        return [None, "4 goc tim duoc khong khop ti le phieu (anh chup qua nghieng?)"]

    return [goc, ""]


def grade_image(anh, mau, cac_de):
    # anh: anh mau BGR
    # mau: 1 muc trong DANH_SACH_MAU
    # cac_de: tu dien ma de -> dap an. Dap an la danh sach theo phan, moi phan la danh sach theo cau.
    #         Cau khong cham de chuoi rong "".
    # Tra ve tu dien ket qua (xem cuoi ham)
    cac_phan = mau["cac_phan"]
    cac_nhom = mau["cac_nhom"]
    RONG = mau["rong"]
    CAO = mau["cao"]
    BAN_KINH = mau["ban_kinh"]

    ket_qua = {
        "trang_thai": "",
        "sbd": "",
        "ma_de": "",
        "bai_lam": [],
        "diem_phan": [],
        "tong_diem": 0,
        "cau_sai": "",
        "anh_ket_qua": None,
    }

    # ---------------- Buoc 1-2: tim 4 goc ----------------
    goc, loi = find_corners(anh, mau)
    if goc is None:
        ket_qua["trang_thai"] = "loi: " + loi
        return ket_qua

    # ---------------- Buoc 3: hieu chinh phoi canh ----------------
    diem_chuan = np.float32(mau["goc"])
    ma_tran = cv2.getPerspectiveTransform(goc, diem_chuan)
    phieu = cv2.warpPerspective(anh, ma_tran, (RONG, CAO))

    # ---------------- Buoc 4: nhi phan hoa ----------------
    phieu_xam = cv2.cvtColor(phieu, cv2.COLOR_BGR2GRAY)
    phieu_mo = cv2.GaussianBlur(phieu_xam, (5, 5), 0)
    cua_so = 4 * BAN_KINH + 1
    phieu_nguong = cv2.adaptiveThreshold(phieu_mo, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, cua_so, 15)

    # ---------------- Danh sach tat ca o tren phieu ----------------
    o_nhom = []
    o_x = []
    o_y = []
    o_r = []
    o_ky_hieu = []
    for g in range(len(cac_nhom)):
        for o in cac_nhom[g]["cac_o"]:
            o_nhom.append(g)
            o_x.append(o[0])
            o_y.append(o[1])
            o_r.append(o[2])
            o_ky_hieu.append(o[3])
    SO_O = len(o_nhom)

    # ---------------- Buoc 5: tim vet to bang connected components ----------------
    so_vung, _, stats, tam = cv2.connectedComponentsWithStats(phieu_nguong, 8)
    tam_x = []
    tam_y = []
    for i in range(SO_O):
        tam_x.append(o_x[i])
        tam_y.append(o_y[i])
    r_nho = min(o_r)
    r_lon = max(o_r)
    for k in range(1, so_vung):
        w = stats[k, cv2.CC_STAT_WIDTH]
        h = stats[k, cv2.CC_STAT_HEIGHT]
        dien_tich = stats[k, cv2.CC_STAT_AREA]
        if w < 1.2 * r_nho or h < 1.2 * r_nho or w > 3 * r_lon or h > 3 * r_lon:
            continue
        if w / h < 0.6 or w / h > 1.6:
            continue
        if dien_tich / (w * h) < 0.5:
            continue
        cx = tam[k][0]
        cy = tam[k][1]
        o_gan_nhat = -1
        kc_nho_nhat = 0
        for i in range(SO_O):
            kc = ((cx - o_x[i]) ** 2 + (cy - o_y[i]) ** 2) ** 0.5
            if kc > o_r[i]:
                continue
            if o_gan_nhat == -1 or kc < kc_nho_nhat:
                o_gan_nhat = i
                kc_nho_nhat = kc
        if o_gan_nhat == -1:
            continue
        tam_x[o_gan_nhat] = int(round(cx))
        tam_y[o_gan_nhat] = int(round(cy))

    # ---------------- Buoc 6: do ti le muc trong tung o ----------------
    chon = []
    for g in range(len(cac_nhom)):
        chon.append([])
    for i in range(SO_O):
        nua = int(o_r[i] * 0.6)
        vung = phieu_nguong[tam_y[i] - nua:tam_y[i] + nua, tam_x[i] - nua:tam_x[i] + nua]
        if vung.size == 0:
            continue
        if cv2.countNonZero(vung) / vung.size > NGUONG_TO:
            chon[o_nhom[i]].append(o_ky_hieu[i])

    # Ket qua moi nhom: "_" bo trong, "X" to nhieu o, con lai la ky hieu duoc to
    ket_qua_nhom = []
    for g in range(len(cac_nhom)):
        if len(chon[g]) == 0:
            ket_qua_nhom.append("_")
        elif len(chon[g]) > 1:
            ket_qua_nhom.append("X")
        else:
            ket_qua_nhom.append(chon[g][0])

    # ---------------- Buoc 7: ghep bai lam tung cau ----------------
    bai_lam = []
    for phan in cac_phan:
        ds = []
        for cau in range(phan["so_cau"]):
            ds.append("")
        bai_lam.append(ds)
    sbd = ""
    ma_de = ""
    for g in range(len(cac_nhom)):
        nhom = cac_nhom[g]
        kq = ket_qua_nhom[g]
        if nhom["phan"] == -1:
            sbd = sbd + kq
        elif nhom["phan"] == -2:
            ma_de = ma_de + kq
        elif cac_phan[nhom["phan"]]["loai"] == "so":
            if kq != "_":
                bai_lam[nhom["phan"]][nhom["cau"]] += kq
        else:
            bai_lam[nhom["phan"]][nhom["cau"]] += kq
    for p in range(len(cac_phan)):
        if cac_phan[p]["loai"] != "so":
            continue
        for cau in range(len(bai_lam[p])):
            if "X" in bai_lam[p][cau]:
                bai_lam[p][cau] = "X"
            if bai_lam[p][cau] == "":
                bai_lam[p][cau] = "_"
    ket_qua["sbd"] = sbd
    ket_qua["ma_de"] = ma_de

    # ---------------- Chon dap an theo ma de ----------------
    # Dung dap an cua ma de doc duoc. Neu ky thi chi co 1 de thi dung de do.
    dap_an = None
    if ma_de in cac_de:
        dap_an = cac_de[ma_de]
    elif len(cac_de) == 1:
        for ma in cac_de:
            dap_an = cac_de[ma]

    # Chuoi bai lam de luu: cau abcd viet lien, loai khac cach nhau dau cach
    for p in range(len(cac_phan)):
        if cac_phan[p]["loai"] == "abcd":
            ket_qua["bai_lam"].append("".join(bai_lam[p]))
        else:
            ket_qua["bai_lam"].append(" ".join(bai_lam[p]))

    if dap_an is None:
        ket_qua["trang_thai"] = "loi: khong co dap an cho ma de " + ma_de
        ket_qua["anh_ket_qua"] = phieu.copy()
        cv2.putText(ket_qua["anh_ket_qua"], "SBD: " + sbd + "   Ma de: " + ma_de + " (chua co dap an)", (RONG // 2 - 380, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
        return ket_qua

    # ---------------- Buoc 8: tinh diem tung phan ----------------
    # Cau co dap an rong "" thi khong cham
    diem_phan = []
    cau_dung = []
    cac_cau_sai = ""
    tong_diem = 0
    for p in range(len(cac_phan)):
        phan = cac_phan[p]
        so_cau_cham = 0
        for cau in range(len(dap_an[p])):
            if dap_an[p][cau] != "":
                so_cau_cham += 1
        diem = 0
        ds_dung = []
        for cau in range(phan["so_cau"]):
            if cau >= len(dap_an[p]) or dap_an[p][cau] == "":
                ds_dung.append(None)
                continue
            dung = False
            if phan["loai"] == "abcd":
                if "diem_moi_cau" in phan:
                    diem_moi_cau = phan["diem_moi_cau"]
                else:
                    diem_moi_cau = 10 / so_cau_cham
                if bai_lam[p][cau] == dap_an[p][cau]:
                    dung = True
                    diem += diem_moi_cau
            elif phan["loai"] == "dung_sai":
                so_y_dung = 0
                for y in range(4):
                    if bai_lam[p][cau][y] == dap_an[p][cau][y]:
                        so_y_dung += 1
                diem += phan["diem_theo_so_y_dung"][so_y_dung]
                if so_y_dung == 4:
                    dung = True
            else:
                if bai_lam[p][cau] == dap_an[p][cau]:
                    dung = True
                else:
                    try:
                        so_bai_lam = float(bai_lam[p][cau].replace(",", "."))
                        so_dap_an = float(dap_an[p][cau].replace(",", "."))
                        if abs(so_bai_lam - so_dap_an) < 1e-9:
                            dung = True
                    except ValueError:
                        dung = False
                if dung:
                    diem += phan["diem_moi_cau"]
            ds_dung.append(dung)
            if not dung:
                if len(cac_phan) > 1:
                    cac_cau_sai = cac_cau_sai + "P" + str(p + 1) + "."
                cac_cau_sai = cac_cau_sai + str(cau + 1) + " "
        diem = round(diem, 2)
        diem_phan.append(diem)
        cau_dung.append(ds_dung)
        tong_diem += diem
    tong_diem = round(tong_diem, 2)

    # ---------------- Buoc 9: ve ket qua ----------------
    # Xanh dam: to dung. Xanh mong: o dung ma khong to. Do: to sai.
    anh_kq = phieu.copy()
    for i in range(SO_O):
        nhom = cac_nhom[o_nhom[i]]
        p = nhom["phan"]
        if p < 0:
            continue
        cau = nhom["cau"]
        if cau_dung[p][cau] is None:
            continue
        ky_hieu = o_ky_hieu[i]
        da_to = ky_hieu in chon[o_nhom[i]]
        if cac_phan[p]["loai"] == "so":
            if da_to and cau_dung[p][cau]:
                cv2.circle(anh_kq, (o_x[i], o_y[i]), o_r[i] + 4, (0, 200, 0), 3)
            elif da_to:
                cv2.circle(anh_kq, (o_x[i], o_y[i]), o_r[i] + 4, (0, 0, 255), 3)
            continue
        if cac_phan[p]["loai"] == "abcd":
            la_dap_an = ky_hieu == dap_an[p][cau]
        else:
            la_dap_an = ky_hieu == dap_an[p][cau][nhom["phu"]]
        if la_dap_an and da_to:
            cv2.circle(anh_kq, (o_x[i], o_y[i]), o_r[i] + 4, (0, 200, 0), 3)
        elif la_dap_an:
            cv2.circle(anh_kq, (o_x[i], o_y[i]), o_r[i] + 4, (0, 200, 0), 1)
        elif da_to:
            cv2.circle(anh_kq, (o_x[i], o_y[i]), o_r[i] + 4, (0, 0, 255), 3)

    chu_diem = "Diem: " + str(tong_diem)
    if len(cac_phan) > 1:
        chu_diem = chu_diem + "  ("
        for p in range(len(cac_phan)):
            chu_diem = chu_diem + "P" + str(p + 1) + ": " + str(diem_phan[p])
            if p < len(cac_phan) - 1:
                chu_diem = chu_diem + ", "
        chu_diem = chu_diem + ")"
    cv2.putText(anh_kq, chu_diem, (60, CAO - 25), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)
    cv2.putText(anh_kq, "SBD: " + sbd + "   Ma de: " + ma_de, (RONG // 2 - 250, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)

    ket_qua["trang_thai"] = "ok"
    ket_qua["diem_phan"] = diem_phan
    ket_qua["tong_diem"] = tong_diem
    ket_qua["cau_sai"] = cac_cau_sai.strip()
    ket_qua["anh_ket_qua"] = anh_kq
    return ket_qua
