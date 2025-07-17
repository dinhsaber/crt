import crt
import vss_1
import random
import json
import os
import cv2
import numpy as np
import glob
from math import gcd
from itertools import combinations
import pandas as pd

SERVER_DIR = "server_crt"
N_CLIENTS = 5
CLIENT_IDS = [f'Client_{i}' for i in range(N_CLIENTS)]


def is_image_file(filename):
    return filename.lower().endswith((".png", ".jpg", ".jpeg"))



def random_coprime_moduli(n, min_val=2, max_val=256):
    from math import gcd
    moduli = []
    while len(moduli) < n:
        candidate = random.randint(min_val, max_val)
        if all(gcd(candidate, m) == 1 for m in moduli):
            moduli.append(candidate)
    return moduli

def save_server_files(moduli, client_ids, image_id, k, shape,key_vss):
    with open(os.path.join(SERVER_DIR, f"meta_{image_id}.json"), "w") as f:
        json.dump({"moduli": [int(m) for m in moduli], "client_ids": client_ids, "shape": shape, "k": k, 'key_vss': key_vss.tolist()}, f)

def save_client_files(shares, client_ids, image_id):
    for i, (share, client_id) in enumerate(zip(shares, client_ids)):
        packet = {
            "image_id": image_id,
            "share_data": share.tolist(),
            "client_id": client_id
        }
        # Lưu ảnh share 
        # share_img = np.clip(share, 0, 255).astype(np.uint8)
        # cv2.imwrite(f"encode_{image_id}_{client_id}.png", share_img)
        with open(os.path.join(client_id, f"share_{image_id}_{i}.json"), "w") as f:
            json.dump(packet, f)
def encode_images_from_folder(folder, k):
    meta_index_path = "server_crt/meta_index.csv"
    if not os.path.exists(meta_index_path):
        pd.DataFrame(columns=["image_id", "meta_file"]).to_csv(meta_index_path, index=False)
    meta_index_df = pd.read_csv(meta_index_path)
    files = [f for f in os.listdir(folder) if is_image_file(f)]
    if not files:
        print("Không có ảnh hợp lệ trong thư mục!")
        return
    for filename in files:
        img_path = os.path.join(folder, filename)
        image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        key_vss, img_vss = vss_1.encode_vss(image)
        image = img_vss
        if image is None:
            print(f"Không đọc được ảnh: {filename}")
            continue

        # tạo id share
        while True:
            image_id = str(random.randint(1, 100))
            if image_id not in meta_index_df["image_id"].astype(str).values:
                break

        # tạo moduli 
        moduli = random_coprime_moduli(N_CLIENTS)
        print(f"Ảnh {filename} - module: {moduli}")
        shares = crt.CRT.encode_shares(image, moduli)
        save_client_files(shares, CLIENT_IDS, image_id)
        save_server_files(moduli, CLIENT_IDS, image_id, k, shares[0].shape, key_vss)
        print(f"Đã chia shares cho ảnh {filename}, image_id: {image_id}, đã lưu {len(shares)} ảnh mã hóa encrypted_{image_id}_<client>.png")

        # Thêm vào meta_index.csv
        meta_file = f"meta_{image_id}.json"
        meta_index_df = pd.concat([meta_index_df, pd.DataFrame([[image_id, meta_file]], columns=["image_id", "meta_file"])] , ignore_index=True)
        meta_index_df.to_csv(meta_index_path, index=False)






def batch_recover_from_share_folder():
    meta_csv = pd.read_csv('server_crt/meta_index.csv')
    print('Các id khôi phục:')
    print(meta_csv['image_id'].to_string(index=False))
    ids_input = input("Nhập các image_id muốn khôi phục (cách nhau bởi dấu cách): ").strip()
    selected_ids = ids_input.split()

    client_dirs = {}
    for cid in CLIENT_IDS:
        dir_path = input(f"Nhập thư mục chứa share cho {cid} (Enter để bỏ qua client này): ").strip()
        if dir_path and os.path.isdir(dir_path):
            client_dirs[cid] = dir_path
    share_records = []
    for image_id in selected_ids:
        for cid in CLIENT_IDS:
            dir_path = client_dirs.get(cid)
            if not dir_path:
                continue
            for fname in os.listdir(dir_path):
                if fname.startswith(f"share_{image_id}_") and fname.endswith(".json"):
                    share_path = os.path.join(dir_path, fname)
                    idx_share = int(fname.split("_")[-1].split(".")[0])
                    share_records.append({
                        "image_id": image_id,
                        "client_id": cid,
                        "share_path": share_path,
                        "idx_share": idx_share,
                        "fname": fname
                    })
    df = pd.DataFrame(share_records)
    if df.empty:
        print("share ko hợp")
        return
    df = df.sort_values(by=["image_id", "client_id", "idx_share"]).reset_index(drop=True)
    print(df)

    # Khôi phục
    for image_id in selected_ids:
        meta_path = os.path.join(SERVER_DIR, f"meta_{image_id}.json")
        if not os.path.exists(meta_path):
            print(f"{image_id} không tồn tại")
            continue
        with open(meta_path, "r") as f:
            meta = json.load(f)
            moduli = meta["moduli"]
            k = meta["k"]
            key_vss = np.array(meta["key_vss"])
        df_img = df[df["image_id"] == image_id]
        print(df_img)
        if len(df_img) < k:
            print(f"Không đủ {k} share khôi phục image_id {image_id}!")
            continue
        df_img = df_img.sort_values(by="idx_share").head(k)
        residues = []
        indices = []
        used_clients = []
        for _, row in df_img.iterrows():
            with open(row["share_path"], "r") as f:
                packet = json.load(f)
                residues.append(np.array(packet["share_data"]))
                indices.append(row["idx_share"])
                used_clients.append(row["client_id"])
        selected_moduli = [moduli[i] for i in indices]

        rec_img = crt.CRT.decode_secret(residues, selected_moduli)

        rec_img = np.clip(rec_img, 0, 255).astype(np.uint8)
        rec_img = vss_1.decode_vss(rec_img, key_vss)

        cv2.imwrite(f"reconstructed_{image_id}.png", rec_img)
        print(f"Ảnh khôi phục : reconstructed_{image_id}.png (shares từ: {', '.join(used_clients)})")








def main_menu():
    while True:
        print("\nMenu:")
        print("1. Mã hóa")
        print("2. Khôi phục")
        choice = input("Chọn chức năng: ")
        if choice == "1":
            folder = input("Nhập thư mục chứa ảnh: ").strip()
            if not os.path.exists(folder) or not os.path.isdir(folder):
                print("Không tìm thấy thư mục!")
                continue
            try:
                k = int(input(f"Nhập k (k <= {N_CLIENTS}): ").strip())
                if k < 2 or k > N_CLIENTS:
                    print(f"k từ 2 đến {N_CLIENTS}")
                    continue
            except Exception:
                print("Giá trị không hợp lệ!")
                continue
            encode_images_from_folder(folder, k)
        elif choice == "2":
            batch_recover_from_share_folder()


if __name__ == "__main__":
    os.makedirs(SERVER_DIR, exist_ok=True)
    for client in CLIENT_IDS:
        os.makedirs(client, exist_ok=True)
    main_menu() 