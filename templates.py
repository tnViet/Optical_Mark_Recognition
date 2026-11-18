# Cau hinh cac mau phieu (lay tu file pdf trong anh_mau, doi sang png o 150 dpi)
# Toa do do tren anh png cua mau phieu, don vi pixel

# O co ti le pixel muc lon hon nguong nay thi coi la da to
NGUONG_TO = 0.5

# Y nghia cac thong so cua moi mau:
#   rong, cao   : kich thuoc phieu sau khi nan thang
#   goc         : tam 4 o vuong den o 4 goc: tren trai, tren phai, duoi trai, duoi phai
#   ban_kinh    : ban kinh o tron cau hoi
#   ban_kinh_so : ban kinh o tron so bao danh va ma de
#   sbd_x       : x cua 6 cot so bao danh, sbd_y: y cua 10 hang so 0..9
#   ma_de_x     : x cua 3 cot ma de, ma_de_y: y cua 10 hang so 0..9
#   cac_phan    : cac phan cua phieu, moi phan co ten, loai va toa do o
#
# Co 3 loai phan:
#   "abcd"     : moi cau chon 1 trong 4 o A B C D
#                khoi: cac khoi cau, moi khoi gom cau_dau (so thu tu cau dau tien trong phan),
#                x (x cua 4 o A B C D), y (y cua tung cau trong khoi, tu tren xuong)
#                diem_moi_cau: neu khong co thi chia deu 10 diem cho so cau cham
#   "dung_sai" : moi cau co 4 y a b c d, moi y chon Dung (D) hoac Sai (S)
#                cau: moi cau gom x (x cua o Dung, o Sai), y (y cua 4 y a b c d)
#                diem_theo_so_y_dung: diem cua cau khi dung 0, 1, 2, 3, 4 y
#   "so"       : moi cau to 4 cot de ghi 1 so, vi du -1,5 hoac 2025
#                cau: moi cau gom x (x cua 4 cot), y_tru (y cua o dau -, chi co o cot 1),
#                y_phay (y cua o dau phay, chi co o cot 2 va 3), y_so (y cua 10 hang so 0..9)
DANH_SACH_MAU = {
    "Mau 20 cau": {
        "rong": 1241,
        "cao": 1754,
        "goc": [[174, 216], [1090, 216], [174, 1568], [1090, 1568]],
        "ban_kinh": 15,
        "ban_kinh_so": 15,
        "sbd_x": [408, 445, 482, 519, 556, 594],
        "sbd_y": [616, 658, 702, 744, 788, 832, 876, 918, 962, 1004],
        "ma_de_x": [673, 710, 747],
        "ma_de_y": [616, 658, 702, 744, 788, 832, 876, 918, 962, 1004],
        "cac_phan": [
            {"ten": "Trac nghiem", "loai": "abcd", "khoi": [
                {"cau_dau": 1, "x": [445, 482, 519, 556],
                 "y": [1092, 1134, 1178, 1220, 1264, 1308, 1352, 1394, 1438, 1480]},
                {"cau_dau": 11, "x": [673, 710, 747, 784],
                 "y": [1092, 1134, 1178, 1220, 1264, 1308, 1352, 1394, 1438, 1480]}
            ]}
        ]
    },
    "Mau 40 cau": {
        "rong": 1241,
        "cao": 1754,
        "goc": [[174, 216], [1090, 216], [174, 1568], [1090, 1568]],
        "ban_kinh": 15,
        "ban_kinh_so": 15,
        "sbd_x": [296, 333, 370, 407, 444, 482],
        "sbd_y": [616, 656, 700, 742, 788, 830, 874, 916, 962, 1004],
        "ma_de_x": [561, 598, 635],
        "ma_de_y": [616, 656, 700, 742, 788, 830, 874, 916, 962, 1004],
        "cac_phan": [
            {"ten": "Trac nghiem", "loai": "abcd", "khoi": [
                {"cau_dau": 1, "x": [789, 826, 863, 900],
                 "y": [616, 656, 700, 742, 788, 830, 874, 916, 962, 1004]},
                {"cau_dau": 11, "x": [333, 370, 408, 444],
                 "y": [1092, 1132, 1176, 1219, 1264, 1306, 1350, 1392, 1438, 1480]},
                {"cau_dau": 21, "x": [561, 598, 636, 672],
                 "y": [1092, 1132, 1176, 1219, 1264, 1306, 1350, 1392, 1438, 1480]},
                {"cau_dau": 31, "x": [789, 826, 863, 900],
                 "y": [1092, 1132, 1176, 1219, 1264, 1306, 1350, 1392, 1438, 1480]}
            ]}
        ]
    },
    "Mau 50 cau": {
        "rong": 1240,
        "cao": 1753,
        "goc": [[96, 110], [1148, 110], [96, 1666], [1148, 1666]],
        "ban_kinh": 13,
        "ban_kinh_so": 10,
        "sbd_x": [902, 926, 948, 971, 994, 1017],
        "sbd_y": [225, 258, 291, 324, 357, 390, 424, 456, 490, 522],
        "ma_de_x": [1074, 1097, 1120],
        "ma_de_y": [225, 258, 291, 324, 358, 390, 424, 456, 490, 522],
        "cac_phan": [
            {"ten": "Trac nghiem", "loai": "abcd", "khoi": [
                {"cau_dau": 1, "x": [304, 380, 458, 533],
                 "y": [706, 742, 779, 816, 852, 890, 927, 964, 1000, 1037, 1076, 1113, 1150, 1186, 1223, 1262, 1299, 1336, 1372, 1409, 1446, 1483, 1520, 1557, 1594]},
                {"cau_dau": 26, "x": [787, 864, 940, 1016],
                 "y": [706, 742, 779, 816, 852, 890, 927, 964, 1000, 1037, 1076, 1113, 1150, 1186, 1223, 1262, 1299, 1336, 1372, 1409, 1446, 1483, 1520, 1557, 1594]}
            ]}
        ]
    },
    "Mau 100 cau": {
        "rong": 1241,
        "cao": 1754,
        "goc": [[174, 216], [1090, 216], [174, 1568], [1090, 1568]],
        "ban_kinh": 12,
        "ban_kinh_so": 12,
        "sbd_x": [277, 307, 335, 365, 394, 423],
        "sbd_y": [444, 474, 509, 542, 577, 610, 644, 678, 713, 746],
        "ma_de_x": [486, 515, 544],
        "ma_de_y": [442, 475, 510, 542, 578, 611, 645, 678, 713, 746],
        "cac_phan": [
            {"ten": "Trac nghiem", "loai": "abcd", "khoi": [
                {"cau_dau": 1, "x": [661, 690, 719, 748],
                 "y": [442, 475, 510, 542, 578, 611, 645, 678, 714, 746]},
                {"cau_dau": 11, "x": [839, 868, 897, 926],
                 "y": [442, 475, 510, 542, 578, 611, 645, 678, 714, 746]},
                {"cau_dau": 21, "x": [306, 335, 364, 393],
                 "y": [814, 847, 882, 914, 950, 983, 1017, 1050, 1086, 1118]},
                {"cau_dau": 31, "x": [486, 515, 544, 573],
                 "y": [814, 847, 882, 914, 950, 983, 1017, 1050, 1086, 1118]},
                {"cau_dau": 41, "x": [661, 690, 719, 748],
                 "y": [814, 847, 882, 914, 950, 983, 1017, 1050, 1086, 1118]},
                {"cau_dau": 51, "x": [839, 868, 897, 926],
                 "y": [814, 847, 882, 914, 950, 983, 1017, 1050, 1086, 1118]},
                {"cau_dau": 61, "x": [306, 335, 364, 393],
                 "y": [1184, 1217, 1252, 1284, 1320, 1353, 1387, 1420, 1456, 1488]},
                {"cau_dau": 71, "x": [486, 515, 544, 573],
                 "y": [1184, 1217, 1252, 1284, 1320, 1353, 1387, 1420, 1456, 1488]},
                {"cau_dau": 81, "x": [661, 690, 719, 748],
                 "y": [1184, 1217, 1252, 1284, 1320, 1353, 1387, 1420, 1456, 1488]},
                {"cau_dau": 91, "x": [839, 868, 897, 926],
                 "y": [1184, 1217, 1252, 1284, 1320, 1353, 1387, 1420, 1456, 1488]}
            ]}
        ]
    },
    "Mau 120 cau": {
        "rong": 1240,
        "cao": 1753,
        "goc": [[77, 76], [1162, 76], [77, 1677], [1162, 1677]],
        "ban_kinh": 12,
        "ban_kinh_so": 10,
        "sbd_x": [908, 932, 956, 979, 1002, 1026],
        "sbd_y": [195, 229, 263, 297, 331, 365, 399, 433, 467, 501],
        "ma_de_x": [1085, 1108, 1132],
        "ma_de_y": [195, 229, 263, 297, 331, 365, 399, 433, 467, 501],
        "cac_phan": [
            {"ten": "Trac nghiem", "loai": "abcd", "khoi": [
                {"cau_dau": 1, "x": [181, 226, 270, 313],
                 "y": [613, 648, 682, 716, 750, 786, 820, 856, 890, 924, 958, 992, 1028, 1062, 1096, 1132, 1166, 1202, 1236, 1270, 1306, 1340, 1374, 1408, 1444, 1480, 1514, 1549, 1584, 1618]},
                {"cau_dau": 31, "x": [445, 490, 534, 578],
                 "y": [613, 648, 682, 716, 750, 786, 820, 856, 890, 924, 958, 992, 1028, 1062, 1096, 1132, 1166, 1202, 1236, 1270, 1306, 1340, 1374, 1408, 1444, 1480, 1514, 1549, 1584, 1618]},
                {"cau_dau": 61, "x": [708, 752, 796, 840],
                 "y": [613, 648, 682, 716, 750, 786, 820, 856, 890, 924, 958, 992, 1028, 1062, 1096, 1132, 1166, 1202, 1236, 1270, 1306, 1340, 1374, 1408, 1444, 1480, 1514, 1549, 1584, 1618]},
                {"cau_dau": 91, "x": [970, 1015, 1059, 1102],
                 "y": [613, 648, 682, 716, 750, 786, 820, 856, 890, 924, 958, 992, 1028, 1062, 1096, 1132, 1166, 1202, 1236, 1270, 1306, 1340, 1374, 1408, 1444, 1480, 1514, 1549, 1584, 1618]}
            ]}
        ]
    },
    "Mau THPT 3 phan": {
        "rong": 1240,
        "cao": 1754,
        "goc": [[78, 76], [1162, 76], [78, 1678], [1162, 1678]],
        "ban_kinh": 10,
        "ban_kinh_so": 10,
        "sbd_x": [909, 933, 956, 979, 1003, 1027],
        "sbd_y": [195, 229, 263, 297, 331, 365, 399, 433, 467, 501],
        "ma_de_x": [1086, 1109, 1132],
        "ma_de_y": [195, 229, 263, 297, 331, 365, 399, 433, 467, 501],
        "cac_phan": [
            {"ten": "Phan I", "loai": "abcd", "diem_moi_cau": 0.25, "khoi": [
                {"cau_dau": 1, "x": [174, 225, 276, 326],
                 "y": [670, 696, 722, 748, 774, 802, 828, 854, 880, 906]},
                {"cau_dau": 11, "x": [428, 480, 530, 582],
                 "y": [670, 696]}
            ]},
            {"ten": "Phan II", "loai": "dung_sai", "diem_theo_so_y_dung": [0, 0.1, 0.25, 0.5, 1], "cau": [
                {"x": [174, 224], "y": [1050, 1076, 1104, 1130]},
                {"x": [276, 326], "y": [1050, 1076, 1104, 1130]},
                {"x": [430, 480], "y": [1050, 1076, 1104, 1130]},
                {"x": [532, 582], "y": [1050, 1076, 1104, 1130]}
            ]},
            {"ten": "Phan III", "loai": "so", "diem_moi_cau": 0.5, "cau": [
                {"x": [166, 200, 236, 272], "y_tru": 1285, "y_phay": 1312,
                 "y_so": [1340, 1366, 1394, 1422, 1448, 1474, 1502, 1528, 1556, 1583]},
                {"x": [328, 364, 398, 434], "y_tru": 1285, "y_phay": 1312,
                 "y_so": [1340, 1366, 1394, 1422, 1448, 1474, 1502, 1528, 1556, 1583]},
                {"x": [492, 526, 561, 596], "y_tru": 1285, "y_phay": 1312,
                 "y_so": [1340, 1366, 1394, 1422, 1448, 1474, 1502, 1528, 1556, 1583]},
                {"x": [654, 690, 726, 761], "y_tru": 1285, "y_phay": 1312,
                 "y_so": [1340, 1366, 1394, 1422, 1448, 1474, 1502, 1528, 1556, 1583]},
                {"x": [818, 854, 888, 924], "y_tru": 1285, "y_phay": 1312,
                 "y_so": [1340, 1366, 1394, 1422, 1448, 1474, 1502, 1528, 1556, 1583]},
                {"x": [982, 1016, 1051, 1086], "y_tru": 1285, "y_phay": 1312,
                 "y_so": [1340, 1366, 1394, 1422, 1448, 1474, 1502, 1528, 1556, 1583]}
            ]}
        ]
    }
}

# ---------------- Tao danh sach nhom o cho tung mau ----------------
# Moi nhom la cac o ma hoc sinh chi duoc to 1 o: 1 cau ABCD, 1 y dung/sai, 1 cot cua cau dien so,
# 1 cot so bao danh hoac ma de.
# Moi nhom: phan (chi so phan, -1 la so bao danh, -2 la ma de), cau (so thu tu cau trong phan, tu 0),
# phu (thu tu y a b c d voi cau dung/sai, thu tu cot voi cau dien so),
# cac_o (moi o: [x, y, ban kinh, ky hieu])
for ten_mau in DANH_SACH_MAU:
    mau = DANH_SACH_MAU[ten_mau]
    r = mau["ban_kinh"]
    r_so = mau["ban_kinh_so"]
    cac_nhom = []

    for p in range(len(mau["cac_phan"])):
        phan = mau["cac_phan"][p]
        so_cau = 0

        if phan["loai"] == "abcd":
            for khoi in phan["khoi"]:
                for dong in range(len(khoi["y"])):
                    cac_o = []
                    chu = ["A", "B", "C", "D"]
                    for j in range(4):
                        cac_o.append([khoi["x"][j], khoi["y"][dong], r, chu[j]])
                    cau = khoi["cau_dau"] - 1 + dong
                    cac_nhom.append({"phan": p, "cau": cau, "phu": 0, "cac_o": cac_o})
                    if cau + 1 > so_cau:
                        so_cau = cau + 1

        if phan["loai"] == "dung_sai":
            for cau in range(len(phan["cau"])):
                c = phan["cau"][cau]
                for y in range(len(c["y"])):
                    cac_o = [[c["x"][0], c["y"][y], r, "D"], [c["x"][1], c["y"][y], r, "S"]]
                    cac_nhom.append({"phan": p, "cau": cau, "phu": y, "cac_o": cac_o})
            so_cau = len(phan["cau"])

        if phan["loai"] == "so":
            for cau in range(len(phan["cau"])):
                c = phan["cau"][cau]
                for cot in range(4):
                    cac_o = []
                    if cot == 0:
                        cac_o.append([c["x"][cot], c["y_tru"], r, "-"])
                    if cot == 1 or cot == 2:
                        cac_o.append([c["x"][cot], c["y_phay"], r, ","])
                    for so in range(10):
                        cac_o.append([c["x"][cot], c["y_so"][so], r, str(so)])
                    cac_nhom.append({"phan": p, "cau": cau, "phu": cot, "cac_o": cac_o})
            so_cau = len(phan["cau"])

        phan["so_cau"] = so_cau

    for cot in range(len(mau["sbd_x"])):
        cac_o = []
        for so in range(10):
            cac_o.append([mau["sbd_x"][cot], mau["sbd_y"][so], r_so, str(so)])
        cac_nhom.append({"phan": -1, "cau": cot, "phu": 0, "cac_o": cac_o})
    for cot in range(len(mau["ma_de_x"])):
        cac_o = []
        for so in range(10):
            cac_o.append([mau["ma_de_x"][cot], mau["ma_de_y"][so], r_so, str(so)])
        cac_nhom.append({"phan": -2, "cau": cot, "phu": 0, "cac_o": cac_o})

    mau["cac_nhom"] = cac_nhom
