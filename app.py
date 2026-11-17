# Ung dung cham bai trac nghiem
# Chay: streamlit run app.py
# Ket qua: anh da cham va file diem.csv nam trong thu muc ket_qua
import os
import csv
import cv2
import numpy as np
import streamlit as st
from cau_hinh import NGUONG_TO, CHU, DANH_SACH_MAU

# ---------------- Giao dien ----------------
st.title("Hệ thống chấm bài trắc nghiệm")

cac_ten_mau = []
for ten in DANH_SACH_MAU:
    cac_ten_mau.append(ten)
ten_mau = st.selectbox("Chọn mẫu phiếu", cac_ten_mau)
mau = DANH_SACH_MAU[ten_mau]

SO_CAU_PHIEU = mau["so_cau"]
RONG = mau["rong"]
CAO = mau["cao"]
BAN_KINH = mau["ban_kinh"]
BAN_KINH_SO = mau["ban_kinh_so"]

dap_an = st.text_input("Nhập đáp án (tối đa " + str(SO_CAU_PHIEU) + " chữ viết liền, ví dụ ABCDABCD...)")
dap_an = dap_an.upper().replace(" ", "")
cac_file = st.file_uploader("Chọn ảnh phiếu (chọn được nhiều ảnh)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
luu_buoc = st.checkbox("Lưu ảnh từng bước vào thư mục buoc_trung_gian")
bam_cham = st.button("Chấm bài")

if bam_cham:
    # ---------------- Kiem tra dau vao ----------------
    # De co the it cau hon phieu: chi cham so cau bang do dai dap an
    SO_CAU = len(dap_an)
    if SO_CAU == 0 or SO_CAU > SO_CAU_PHIEU:
        st.error("Đáp án phải có từ 1 đến " + str(SO_CAU_PHIEU) + " chữ, đang có " + str(SO_CAU))
        st.stop()
    for c in dap_an:
        if c not in CHU:
            st.error("Đáp án chỉ được chứa các chữ " + "".join(CHU) + ", gặp chữ: " + c)
            st.stop()
    if len(cac_file) == 0:
        st.error("Chưa chọn ảnh nào")
        st.stop()

    os.makedirs("ket_qua", exist_ok=True)
    if luu_buoc:
        os.makedirs("buoc_trung_gian", exist_ok=True)

    # ---------------- Danh sach tat ca o tron tren phieu ----------------
    # Moi o gom: loai ("cau", "sbd", "ma_de"), chi so 1, chi so 2, x, y, ban kinh
    # Voi "cau": chi so 1 = so thu tu cau (tu 0), chi so 2 = lua chon (0..3)
    # Voi "sbd", "ma_de": chi so 1 = cot, chi so 2 = chu so (0..9)
    o_loai = []
    o_a = []
    o_b = []
    o_x = []
    o_y = []
    o_r = []
    for khoi in mau["khoi_cau"]:
        for dong in range(len(khoi["y"])):
            cau = khoi["cau_dau"] - 1 + dong
            if cau >= SO_CAU:
                continue
            for j in range(len(CHU)):
                o_loai.append("cau")
                o_a.append(cau)
                o_b.append(j)
                o_x.append(khoi["x"][j])
                o_y.append(khoi["y"][dong])
                o_r.append(BAN_KINH)
    for cot in range(len(mau["sbd_x"])):
        for so in range(10):
            o_loai.append("sbd")
            o_a.append(cot)
            o_b.append(so)
            o_x.append(mau["sbd_x"][cot])
            o_y.append(mau["sbd_y"][so])
            o_r.append(BAN_KINH_SO)
    for cot in range(len(mau["ma_de_x"])):
        for so in range(10):
            o_loai.append("ma_de")
            o_a.append(cot)
            o_b.append(so)
            o_x.append(mau["ma_de_x"][cot])
            o_y.append(mau["ma_de_y"][so])
            o_r.append(BAN_KINH_SO)
    SO_O = len(o_loai)

    # Moi dong: [ten anh, trang thai, sbd, ma de, so cau dung, so cau, diem, bai lam, cac cau sai]
    bang_diem = []

    for file in cac_file:
        ten_anh = file.name
        ten_khong_duoi = os.path.splitext(ten_anh)[0]

        # ---------------- Buoc 1: doc anh ----------------
        du_lieu = np.frombuffer(file.read(), dtype=np.uint8)
        anh = cv2.imdecode(du_lieu, cv2.IMREAD_COLOR)
        if anh is None:
            bang_diem.append([ten_anh, "loi: khong doc duoc anh", "", "", "", "", "", "", ""])
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
            bang_diem.append([ten_anh, "loi: khong tim du 4 o goc", "", "", "", "", "", "", ""])
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
            bang_diem.append([ten_anh, "loi: khong tim du 4 o goc", "", "", "", "", "", "", ""])
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
        so_vet_to = 0
        for k in range(1, so_vung):
            x = stats[k, cv2.CC_STAT_LEFT]
            y = stats[k, cv2.CC_STAT_TOP]
            w = stats[k, cv2.CC_STAT_WIDTH]
            h = stats[k, cv2.CC_STAT_HEIGHT]
            dien_tich = stats[k, cv2.CC_STAT_AREA]

            # Loc theo kich thuoc, do vuong va do dac
            if w < 1.2 * BAN_KINH_SO or h < 1.2 * BAN_KINH_SO or w > 3 * BAN_KINH or h > 3 * BAN_KINH:
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
            so_vet_to += 1
            cv2.rectangle(anh_o, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # ---------------- Buoc 6: do ti le muc trong tung o ----------------
        # Chi do o vuong nho o giua o tron de khong tinh vien o va chu so in san
        ti_le_to = []
        for i in range(SO_O):
            nua = int(o_r[i] * 0.6)
            vung = phieu_nguong[tam_y[i] - nua:tam_y[i] + nua, tam_x[i] - nua:tam_x[i] + nua]
            if vung.size == 0:
                ti_le_to.append(0)
            else:
                ti_le_to.append(cv2.countNonZero(vung) / vung.size)
            cv2.circle(anh_o, (tam_x[i], tam_y[i]), o_r[i], (0, 165, 255), 1)

        # Gom cac o duoc to theo tung cau, tung cot so bao danh, ma de
        to_cau = []
        for i in range(SO_CAU):
            to_cau.append([])
        to_sbd = []
        for i in range(len(mau["sbd_x"])):
            to_sbd.append([])
        to_ma_de = []
        for i in range(len(mau["ma_de_x"])):
            to_ma_de.append([])
        for i in range(SO_O):
            if ti_le_to[i] <= NGUONG_TO:
                continue
            if o_loai[i] == "cau":
                to_cau[o_a[i]].append(o_b[i])
            elif o_loai[i] == "sbd":
                to_sbd[o_a[i]].append(o_b[i])
            else:
                to_ma_de[o_a[i]].append(o_b[i])

        # Bai lam: "-" la bo trong, "X" la to nhieu o
        bai_lam = ""
        for cau in range(SO_CAU):
            if len(to_cau[cau]) == 0:
                bai_lam = bai_lam + "-"
            elif len(to_cau[cau]) > 1:
                bai_lam = bai_lam + "X"
            else:
                bai_lam = bai_lam + CHU[to_cau[cau][0]]

        # So bao danh, ma de: "_" la cot bo trong, "X" la cot to nhieu so
        sbd = ""
        for cot in range(len(to_sbd)):
            if len(to_sbd[cot]) == 0:
                sbd = sbd + "_"
            elif len(to_sbd[cot]) > 1:
                sbd = sbd + "X"
            else:
                sbd = sbd + str(to_sbd[cot][0])
        ma_de = ""
        for cot in range(len(to_ma_de)):
            if len(to_ma_de[cot]) == 0:
                ma_de = ma_de + "_"
            elif len(to_ma_de[cot]) > 1:
                ma_de = ma_de + "X"
            else:
                ma_de = ma_de + str(to_ma_de[cot][0])

        # ---------------- Buoc 7: tinh diem va ve ket qua ----------------
        # Xanh dam: chon dung. Xanh mong: dap an dung ma khong chon. Do: chon sai
        ket_qua = phieu.copy()
        so_cau_dung = 0
        cac_cau_sai = ""
        for i in range(SO_O):
            if o_loai[i] != "cau":
                continue
            cau = o_a[i]
            j = o_b[i]
            la_dap_an = CHU[j] == dap_an[cau]
            da_chon = j in to_cau[cau]
            if la_dap_an and da_chon:
                cv2.circle(ket_qua, (o_x[i], o_y[i]), BAN_KINH + 4, (0, 200, 0), 4)
            elif la_dap_an:
                cv2.circle(ket_qua, (o_x[i], o_y[i]), BAN_KINH + 4, (0, 200, 0), 2)
            elif da_chon:
                cv2.circle(ket_qua, (o_x[i], o_y[i]), BAN_KINH + 4, (0, 0, 255), 4)
        for cau in range(SO_CAU):
            if bai_lam[cau] == dap_an[cau]:
                so_cau_dung += 1
            else:
                cac_cau_sai = cac_cau_sai + str(cau + 1) + " "

        diem = round(so_cau_dung * 10 / SO_CAU, 2)
        chu_diem = "Diem: " + str(diem) + "  (" + str(so_cau_dung) + "/" + str(SO_CAU) + ")"
        cv2.putText(ket_qua, chu_diem, (RONG // 2 - 250, CAO - 25), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)
        cv2.putText(ket_qua, "SBD: " + sbd + "   Ma de: " + ma_de, (RONG // 2 - 250, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3)

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

        bang_diem.append([ten_anh, "ok", sbd, ma_de, so_cau_dung, SO_CAU, diem, bai_lam, cac_cau_sai.strip()])

        # Hien anh ket qua len giao dien (doi BGR sang RGB)
        st.image(cv2.cvtColor(ket_qua, cv2.COLOR_BGR2RGB), caption=ten_anh + " - " + chu_diem, width=500)

    # ---------------- Ghi file diem tong hop ----------------
    tieu_de = ["ten_anh", "trang_thai", "sbd", "ma_de", "so_cau_dung", "so_cau", "diem", "bai_lam", "cac_cau_sai"]
    f = open("ket_qua/diem.csv", "w", newline="", encoding="utf-8-sig")
    ghi = csv.writer(f)
    ghi.writerow(["mau_phieu", ten_mau])
    ghi.writerow(["dap_an", dap_an])
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
