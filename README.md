# crt
Thuật toán crt
**tạo ra số modulu tương ứng số lượng share nhưng bị giới hạn số lượng modulu (m) với điều kiện sau:**
+ ước chung (gcd(mi,kj) == 1)
+ vì tích giữa (k-1) modulu phải nhỏ hơn điểm ảnh. 
+ tích của tất cả module > điểm ảnh

**Nếu không thõa dieu kien chỉ cần 2 shares bất kì sẽ có thể khôi phục**


ví dụ điểm ảnh là 100, với 10 client và k = 3 là thì chỉ có 
min_modulus ≥ secret_max^{1/k}:  min_modulus >= 100^(1/3) = 4.46 ~ 5
max_modulus < secret_max^{1/(k-1)}: max_modulus < 100^(1/2) = 10 
**--> modulu chỉ tồn tại trong khoảng [5,9] với mỗi số modulu tạo ra 1 share do đó chỉ có thể tồn tại tối đa 2 shares** 

#### bỏ điều kiện Áp dụng phép xor trước khi dùng crt: 
- anh sẽ bị mất hết các dac trung khi dung XOR 
- vì đã bỏ các dieu kien thì chỉ cần 2 share là có thể khôi phục anh,  nhưng anh da XOR nên có khôi phục cũng ko thể nhìn ra phải cần key từ server de phục hồi

## Ảnh gốc ![test1](https://github.com/user-attachments/assets/0e6cce60-6c15-461f-96a1-6f423921ed39)
## Chỉ dùng CRT thì share sẽ thế này có thể bị nhìn ra: <img width="1201" height="640" alt="image" src="https://github.com/user-attachments/assets/d88da8b5-0b62-483c-8c30-042389ff01e6" />
## áp dụng XOR trước khi crt để mất hoàn toàn đặc trưng ảnh: <img width="1200" height="630" alt="encode_40_Client_3" src="https://github.com/user-attachments/assets/cd18cf07-7f12-43e2-80ca-abf8d9fdb24a" />

