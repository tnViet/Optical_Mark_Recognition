# Ung dung cham bai trac nghiem
# Chay: streamlit run app.py
# Ket qua: anh da cham va file diem.csv nam trong thu muc ket_qua
import os
import csv
import cv2
import numpy as np
import streamlit as st
from cau_hinh import NGUONG_TO, DANH_SACH_MAU

# ---------------- Giao dien ----------------
st.title("Hệ thống chấm bài trắc nghiệm")

cac_ten_mau = []
for ten in DANH_SACH_MAU:
    cac_ten_mau.append(ten)
ten_mau = st.selectbox("Chọn mẫu phiếu", cac_ten_mau)
mau = DANH_SACH_MAU[ten_mau]
cac_phan = mau["cac_phan"]
cac_nhom = mau["cac_nhom"]
RONG = mau["rong"]
CAO = mau["cao"]
BAN_KINH = mau["ban_kinh"]

# Moi phan 1 o nhap dap an
cac_chuoi_dap_an = []
for phan in cac_phan:
    if phan["loai"] == "abcd":
        nhan_o = "Đáp án " + phan["ten"] + " (tối đa " + str(phan["so_cau"]) + " chữ ABCD viết liền, ví dụ ABCDABCD)"
    elif phan["loai"] == "dung_sai":
        nhan_o = "Đáp án " + phan["ten"] + " (mỗi câu 4 chữ D/S, cách nhau dấu cách, ví dụ DSDS DDSS)"
    else:
        nhan_o = "Đáp án " + phan["ten"] + " (mỗi câu 1 số, cách nhau dấu cách, ví dụ -1,5 12 0,25)"
    cac_chuoi_dap_an.append(st.text_input(nhan_o))

cac_file = st.file_uploader("Chọn ảnh phiếu (chọn được nhiều ảnh)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
luu_buoc = st.checkbox("Lưu ảnh từng bước vào thư mục buoc_trung_gian")
bam_cham = st.button("Chấm bài")

if bam_cham:
    # ---------------- Doc va kiem tra dap an ----------------
    # dap_an[p] la danh sach dap an tung cau cua phan p. Phan de trong thi khong cham.
    dap_an = []
    for p in range(len(cac_phan)):
        phan = cac_phan[p]
        chuoi = cac_chuoi_dap_an[p].upper().replace("Đ", "D").replace(".", ",")
        ds = []
        if phan["loai"] == "abcd":
            for c in chuoi.replace(" ", ""):
                if c not in "ABCD":
                    st.error(phan["ten"] + ": chỉ được dùng chữ A B C D, gặp: " + c)
                    st.stop()
                ds.append(c)
        elif phan["loai"] == "dung_sai":
            for tu in chuoi.split():
                if len(tu) != 4:
                    st.error(phan["ten"] + ": mỗi câu phải có đúng 4 chữ D/S, gặp: " + tu)
                    st.stop()
                for c in tu:
                    if c not in "DS":
                        st.error(phan["ten"] + ": chỉ được dùng chữ D S, gặp: " + c)
                        st.stop()
                ds.append(tu)
        else:
            for tu in chuoi.split():
                if len(tu) > 4:
                    st.error(phan["ten"] + ": mỗi số tối đa 4 ký tự, gặp: " + tu)
                    st.stop()
                for c in tu:
                    if c not in "-,0123456789":
                        st.error(phan["ten"] + ": số chỉ gồm dấu -, dấu phẩy và chữ số, gặp: " + c)
                        st.stop()
                ds.append(tu)
        if len(ds) > phan["so_cau"]:
            st.error(phan["ten"] + ": phiếu chỉ có " + str(phan["so_cau"]) + " câu, đáp án đang có " + str(len(ds)))
            st.stop()
        dap_an.append(ds)

    tong_so_cau = 0
    for ds in dap_an:
        tong_so_cau += len(ds)
    if tong_so_cau == 0:
        st.error("Chưa nhập đáp án")
        st.stop()
    if len(cac_file) == 0:
        st.error("Chưa chọn ảnh nào")
        st.stop()

    os.makedirs("ket_qua", exist_ok=True)
    if luu_buoc:
        os.makedirs("buoc_trung_gian", exist_ok=True)

    # ---------------- Danh sach o can do ----------------
    # Chi lay nhom cua cau co dap an, va nhom so bao danh, ma de
    # Moi o: chi so nhom, x, y, ban kinh, ky hieu
    nhom_dung = []
    for nhom in cac_nhom:
        if nhom["phan"] < 0 or nhom["cau"] < len(dap_an[nhom["phan"]]):
            nhom_dung.append(nhom)
    o_nhom = []
    o_x = []
    o_y = []
    o_r = []
    o_ky_hieu = []
    for g in range(len(nhom_dung)):
        for o in nhom_dung[g]["cac_o"]:
            o_nhom.append(g)
            o_x.append(o[0])
            o_y.append(o[1])
            o_r.append(o[2])
            o_ky_hieu.append(o[3])
    SO_O = len(o_nhom)

    # Moi dong bang diem: ten anh, trang thai, sbd, ma de, (bai lam, diem) cua tung phan, tong diem, cac cau sai
    bang_diem = []
    dong_loi = []
    for i in range(len(cac_phan) * 2 + 4):
        dong_loi.append("")

    for file in cac_file:
        ten_anh = file.name
        ten_khong_duoi = os.path.splitext(ten_anh)[0]

        # ---------------- Buoc 1: doc anh ----------------
        du_lieu = np.frombuffer(file.read(), dtype=np.uint8)
        anh = cv2.imdecode(du_lieu, cv2.IMREAD_COLOR)
        if anh is None:
            bang_diem.append([ten_anh, "loi: khong doc duoc anh"] + dong_loi)
            continue

        # Thu nho anh (chieu rong 1000) de tim phieu cho nhanh
        ti_le = anh.shape[1] / 1000
        anh_nho = cv2.resize(anh, (1000, int(anh.shape[0] / ti_le)))

        # ---------------- Buoc 2: phat hien phieu (tim cac o vuong den) ----------------
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
            (cx, cy), (w, h), goc = cv2.minAreaRect(c)
            if w / h < 0.7 or w / h > 1.3:
                continue
            if dien_tich / (w * h) < 0.75:
                continue
            # Bo cac o vuong rong (o ghi so bao danh): phan giua phai gan nhu den het
            x, y, w, h = cv2.boundingRect(c)
            giua = nguong[y + h // 4:y + h - h // 4, x + w // 4:x + w - w // 4]
            if giua.size == 0 or cv2.countNonZero(giua) / giua.size < 0.8:
                continue
            markers.append([dien_tich, cx, cy])

        if len(markers) < 4:
            bang_diem.append([ten_anh, "loi: khong tim du 4 o goc"] + dong_loi)
            continue

        # Chi giu cac o vuong lon (o goc to hon cac o vuong nho canh cot cau hoi)
        markers.sort(reverse=True)
        dien_tich_lon_nhat = markers[0][0]
        cac_o_lon = []
        for m in markers:
            if m[0] >= 0.5 * dien_tich_lon_nhat:
                cac_o_lon.append(m)

        # 4 goc la 4 o nam ngoai cung: tren-trai co x+y nho nhat, duoi-phai co x+y lon nhat,
        # tren-phai co x-y lon nhat, duoi-trai co x-y nho nhat
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
            bang_diem.append([ten_anh, "loi: khong tim du 4 o goc"] + dong_loi)
            continue

        # ---------------- Buoc 3: hieu chinh phoi canh ----------------
        # Toa do tam 4 o goc tren anh goc (nhan lai voi ti_le)
        diem_anh = np.float32([
            [tren_trai[1] * ti_le, tren_trai[2] * ti_le],
            [tren_phai[1] * ti_le, tren_phai[2] * ti_le],
            [duoi_trai[1] * ti_le, duoi_trai[2] * ti_le],
            [duoi_phai[1] * ti_le, duoi_phai[2] * ti_le],
        ])
        # Toa do tam 4 o goc tren phieu mau
        diem_chuan = np.float32(mau["goc"])
        ma_tran = cv2.getPerspectiveTransform(diem_anh, diem_chuan)
        phieu = cv2.warpPerspective(anh, ma_tran, (RONG, CAO))

        # ---------------- Buoc 4: nhi phan hoa ----------------
        phieu_xam = cv2.cvtColor(phieu, cv2.COLOR_BGR2GRAY)
        phieu_mo = cv2.GaussianBlur(phieu_xam, (5, 5), 0)
        # Nguong thich nghi de chiu duoc bong do, cua so rong gap 2 lan o tron de o to kin khong bi rong ruot
        cua_so = 4 * BAN_KINH + 1
        phieu_nguong = cv2.adaptiveThreshold(phieu_mo, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, cua_so, 15)

        # ---------------- Buoc 5: tim vet to bang connected components ----------------
        # Vet to la vung den dac co kich thuoc gan bang o tron.
        # Moi vet to gan voi o gan nhat, dung tam vet to thay cho tam o tren mau de bu sai lech nho.
        so_vung, nhan, stats, tam = cv2.connectedComponentsWithStats(phieu_nguong, 8)

        tam_x = []
        tam_y = []
        for i in range(SO_O):
            tam_x.append(o_x[i])
            tam_y.append(o_y[i])

        anh_o = phieu.copy()
        r_nho = min(o_r)
        r_lon = max(o_r)
        for k in range(1, so_vung):
            x = stats[k, cv2.CC_STAT_LEFT]
            y = stats[k, cv2.CC_STAT_TOP]
            w = stats[k, cv2.CC_STAT_WIDTH]
            h = stats[k, cv2.CC_STAT_HEIGHT]
            dien_tich = stats[k, cv2.CC_STAT_AREA]

            # Loc theo kich thuoc, do vuong va do dac
            if w < 1.2 * r_nho or h < 1.2 * r_nho or w > 3 * r_lon or h > 3 * r_lon:
                continue
            if w / h < 0.6 or w / h > 1.6:
                continue
            if dien_tich / (w * h) < 0.5:
                continue

            cx = tam[k][0]
            cy = tam[k][1]

            # Tim o gan nhat, tam vet to phai nam trong o
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
            cv2.rectangle(anh_o, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # ---------------- Buoc 6: do ti le muc trong tung o, tim o duoc to ----------------
        # Chi do o vuong nho o giua o tron de khong tinh vien o va chu so in san
        # chon[g] la danh sach ky hieu duoc to trong nhom g
        chon = []
        for g in range(len(nhom_dung)):
            chon.append([])
        for i in range(SO_O):
            nua = int(o_r[i] * 0.6)
            vung = phieu_nguong[tam_y[i] - nua:tam_y[i] + nua, tam_x[i] - nua:tam_x[i] + nua]
            cv2.circle(anh_o, (tam_x[i], tam_y[i]), o_r[i], (0, 165, 255), 1)
            if vung.size == 0:
                continue
            if cv2.countNonZero(vung) / vung.size > NGUONG_TO:
                chon[o_nhom[i]].append(o_ky_hieu[i])

        # Ket qua moi nhom: "_" la bo trong, "X" la to nhieu o, con lai la ky hieu duoc to
        ket_qua_nhom = []
        for g in range(len(nhom_dung)):
            if len(chon[g]) == 0:
                ket_qua_nhom.append("_")
            elif len(chon[g]) > 1:
                ket_qua_nhom.append("X")
            else:
                ket_qua_nhom.append(chon[g][0])

        # ---------------- Buoc 7: ghep bai lam tung cau ----------------
        # Cau abcd: 1 ky tu. Cau dung/sai: 4 ky tu cho 4 y. Cau dien so: ghep cac cot co to, bo cot trong.
        bai_lam = []
        for p in range(len(cac_phan)):
            ds = []
            for cau in range(len(dap_an[p])):
                ds.append("")
            bai_lam.append(ds)
        sbd = ""
        ma_de = ""
        for g in range(len(nhom_dung)):
            nhom = nhom_dung[g]
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

        # ---------------- Buoc 8: tinh diem tung phan ----------------
        diem_phan = []
        cau_dung = []
        cac_cau_sai = ""
        tong_diem = 0
        for p in range(len(cac_phan)):
            phan = cac_phan[p]
            diem = 0
            ds_dung = []
            for cau in range(len(dap_an[p])):
                dung = False
                if phan["loai"] == "abcd":
                    if "diem_moi_cau" in phan:
                        diem_moi_cau = phan["diem_moi_cau"]
                    else:
                        diem_moi_cau = 10 / len(dap_an[p])
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
                    # So sanh chuoi, neu khac thi thu so sanh gia tri (vi du 1,5 va 1,50)
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
        # Cau dien so: o da to mau xanh neu ca cau dung, mau do neu sai.
        ket_qua = phieu.copy()
        for i in range(SO_O):
            nhom = nhom_dung[o_nhom[i]]
            p = nhom["phan"]
            if p < 0:
                continue
            ky_hieu = o_ky_hieu[i]
            da_to = ky_hieu in chon[o_nhom[i]]
            if cac_phan[p]["loai"] == "so":
                if da_to and cau_dung[p][nhom["cau"]]:
                    cv2.circle(ket_qua, (o_x[i], o_y[i]), o_r[i] + 4, (0, 200, 0), 3)
                elif da_to:
                    cv2.circle(ket_qua, (o_x[i], o_y[i]), o_r[i] + 4, (0, 0, 255), 3)
                continue
            if cac_phan[p]["loai"] == "abcd":
                la_dap_an = ky_hieu == dap_an[p][nhom["cau"]]
            else:
                la_dap_an = ky_hieu == dap_an[p][nhom["cau"]][nhom["phu"]]
            if la_dap_an and da_to:
                cv2.circle(ket_qua, (o_x[i], o_y[i]), o_r[i] + 4, (0, 200, 0), 3)
            elif la_dap_an:
                cv2.circle(ket_qua, (o_x[i], o_y[i]), o_r[i] + 4, (0, 200, 0), 1)
            elif da_to:
                cv2.circle(ket_qua, (o_x[i], o_y[i]), o_r[i] + 4, (0, 0, 255), 3)

        chu_diem = "Diem: " + str(tong_diem)
        if len(cac_phan) > 1:
            chu_diem = chu_diem + "  ("
            for p in range(len(cac_phan)):
                chu_diem = chu_diem + "P" + str(p + 1) + ": " + str(diem_phan[p])
                if p < len(cac_phan) - 1:
                    chu_diem = chu_diem + ", "
            chu_diem = chu_diem + ")"
        cv2.putText(ket_qua, chu_diem, (60, CAO - 25), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)
        cv2.putText(ket_qua, "SBD: " + sbd + "   Ma de: " + ma_de, (RONG // 2 - 250, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)

        # Luu anh ket qua va anh tung buoc
        cv2.imwrite("ket_qua/" + ten_khong_duoi + "_ket_qua.jpg", ket_qua)
        if luu_buoc:
            anh_marker = anh_nho.copy()
            for m in cac_o_lon:
                cv2.circle(anh_marker, (int(m[1]), int(m[2])), 15, (0, 0, 255), 3)
            for m in [tren_trai, tren_phai, duoi_trai, duoi_phai]:
                cv2.circle(anh_marker, (int(m[1]), int(m[2])), 25, (0, 200, 0), 4)
            cv2.imwrite("buoc_trung_gian/" + ten_khong_duoi + "_buoc2_nguong_tim_phieu.jpg", nguong)
            cv2.imwrite("buoc_trung_gian/" + ten_khong_duoi + "_buoc2_o_goc.jpg", anh_marker)
            cv2.imwrite("buoc_trung_gian/" + ten_khong_duoi + "_buoc3_phieu_thang.jpg", phieu)
            cv2.imwrite("buoc_trung_gian/" + ten_khong_duoi + "_buoc4_nguong.jpg", phieu_nguong)
            cv2.imwrite("buoc_trung_gian/" + ten_khong_duoi + "_buoc5_cac_o.jpg", anh_o)

        # Ghi 1 dong bang diem. Bai lam cau abcd viet lien, cac loai khac cach nhau dau cach
        dong = [ten_anh, "ok", sbd, ma_de]
        for p in range(len(cac_phan)):
            if cac_phan[p]["loai"] == "abcd":
                dong.append("".join(bai_lam[p]))
            else:
                dong.append(" ".join(bai_lam[p]))
            dong.append(diem_phan[p])
        dong.append(tong_diem)
        dong.append(cac_cau_sai.strip())
        bang_diem.append(dong)

        # Hien anh ket qua len giao dien (doi BGR sang RGB)
        st.image(cv2.cvtColor(ket_qua, cv2.COLOR_BGR2RGB), caption=ten_anh + " - " + chu_diem, width=500)

    # ---------------- Ghi file diem tong hop ----------------
    tieu_de = ["ten_anh", "trang_thai", "sbd", "ma_de"]
    for phan in cac_phan:
        tieu_de.append("bai_lam " + phan["ten"])
        tieu_de.append("diem " + phan["ten"])
    tieu_de.append("tong_diem")
    tieu_de.append("cac_cau_sai")

    f = open("ket_qua/diem.csv", "w", newline="", encoding="utf-8-sig")
    ghi = csv.writer(f)
    ghi.writerow(["mau_phieu", ten_mau])
    for p in range(len(cac_phan)):
        ghi.writerow(["dap_an " + cac_phan[p]["ten"], " ".join(dap_an[p])])
    ghi.writerow(tieu_de)
    for dong in bang_diem:
        ghi.writerow(dong)
    f.close()

    # Hien bang diem
    bang_hien_thi = []
    for dong in bang_diem:
        dong_hien_thi = {}
        for i in range(len(tieu_de)):
            dong_hien_thi[tieu_de[i]] = str(dong[i])
        bang_hien_thi.append(dong_hien_thi)
    st.subheader("Bảng điểm")
    st.table(bang_hien_thi)
    st.success("Đã lưu ảnh kết quả và file diem.csv vào thư mục ket_qua")
