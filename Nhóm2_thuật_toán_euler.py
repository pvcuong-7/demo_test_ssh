import math

# Bảng hàm một biến, bắt buộc có dấu ngoặc: ln(x), sin(x), ...
# Hàm lượng giác tính theo radian; ln là logarit tự nhiên, log là logarit cơ số 10
funcs = {
    'sqrt': math.sqrt,
    'ln': math.log,
    'log': math.log10,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'cot': lambda a: 1 / math.tan(a),
    'arcsin': math.asin,
    'arccos': math.acos,
    'arctan': math.atan,
}

# [MỚI] Bảng hằng số
consts = {
    'pi': math.pi,
    'e': math.e,
}

# Danh sách tên hàm và hằng số, dùng để nhận diện khi tách chuỗi
names = list(funcs) + list(consts)


# Trả về tên hàm/hằng bắt đầu tại vị trí i của chuỗi, không có thì trả về None
def match_name(s, i):
    for name in names:
        if s.startswith(name, i):
            return name
    return None


# HÀM 1: TÁCH CHUỖI VÀ CHUYỂN SANG BIỂU THỨC HẬU TỐ
def to_postfix(s):
    tokens = []
    i = 0

    # Bước 1: Tách chuỗi thành các token
    while i < len(s):
        c = s[i]
        name = match_name(s, i)

        # Bỏ qua dấu cách
        if c == ' ':
            i += 1

        # Nhận diện tên hàm (sqrt, ln, log, sin, ...) và hằng số (pi, e)
        elif name:
            tokens.append(name)
            i += len(name)

        # Xử lí số nguyên, số thập phân
        elif c.isdigit() or c == '.':
            num = ''
            while i < len(s) and (s[i].isdigit() or s[i] == '.'):
                num += s[i]
                i += 1

            # [BÁO LỖI] Số sai dạng, ví dụ '.' hoặc '1.2.3'
            if num == '.' or num.count('.') > 1:
                raise ValueError("So khong hop le: '" + num + "'")

            tokens.append(num)

        # Xử lí biến và toán tử
        elif c in 'xy+-*/^()':
            tokens.append(c)
            i += 1

        # Báo lỗi kí tự không hợp lệ
        else:
            raise ValueError("Ky tu khong hop le")

    # Bước 2: Chuyển trung tố sang hậu tố
    f = []
    stack = []

    # Độ ưu tiên
    priority = {
        '+': 1, '-': 1,
        '*': 2, '/': 2,
        'u+': 3, 'u-': 3,
        '^': 4
    }

    expect = True #đánh dấu chờ toán hạng
                  #expect = False: đang chờ toán tử

    for k, t in enumerate(tokens):

        # Biến, hằng số hoặc số được đưa thẳng vào f
        if t in ('x', 'y') or t in consts or t[0].isdigit() or t[0] == '.':
            # [Báo lỗi] Hai toán hạng đứng liền nhau: 2x, x y, 2pi, (x)y
            if not expect:
                raise ValueError("Thieu dau * hoac toan tu truoc '" + t + "'")

            f.append(t)
            expect = False

        # Xử lý hàm (sqrt, ln, log, sin, cos, ...)
        elif t in funcs:
            # [Báo lỗi] Trước hàm phải là toán tử/'(' (vd: 2sin(x)) và sau hàm phải có '('
            if not expect:
                raise ValueError("Thieu dau * truoc " + t)
            if k + 1 >= len(tokens) or tokens[k + 1] != '(':
                raise ValueError(t + " phai di kem dau ngoac: " + t + "(...)")

            stack.append(t)
            expect = True

        # Gặp '(' thì đưa vào stack
        elif t == '(':
            # [Báo lỗi] Thiếu dấu * trước ngoặc: 2(x), x(y), (x)(y)
            if not expect:
                raise ValueError("Thieu dau * truoc dau '('")

            stack.append(t)
            expect = True

        # Gặp ')' thì đưa toán tử ra f đến '('
        elif t == ')':
            # [Báo lỗi] Ngoặc rỗng hoặc thiếu toán hạng cuối ngoặc: (), (x+), sin()
            if expect:
                raise ValueError("Thieu toan hang truoc dau ')'")

            # kiểm tra stack không rỗng để phát hiện ')' thừa
            while stack and stack[-1] != '(':
                f.append(stack.pop())

            # [Báo lỗi]Không tìm thấy '(' tương ứng
            if not stack:
                raise ValueError("Thua dau ')' or thieu dau '(' tuong ung")

            stack.pop()

            # Nếu trước ngoặc là một hàm (sqrt, ln, sin, ...), đưa hàm ra f
            if stack and stack[-1] in funcs:
                f.append(stack.pop())

            expect = False

        else:
            # Xử lý dấu +, - một ngôi
            if expect and t in ('+', '-'):
                stack.append('u' + t)
                expect = True
                continue

            # Toán tử hai ngôi mà thiếu toán hạng bên trái: *x, x*/y, (*x)
            if expect:
                raise ValueError("Thieu toan hang truoc toan tu '" + t + "'")

            # Xử lý độ ưu tiên và tính kết hợp
            # stack[-1] là hàm thì dừng (hàm chờ ')' mới được đưa ra f)
            while (stack and stack[-1] != '('
                   and stack[-1] not in funcs
                   and (priority[stack[-1]] > priority[t]
                        or (priority[stack[-1]] == priority[t]
                            and t != '^'))):
                f.append(stack.pop())

            stack.append(t)
            expect = True

    # [Báo lỗi] Biểu thức rỗng hoặc kết thúc bằng toán tử: '', 'x+', 'x*-'
    if expect:
        raise ValueError("Bieu thuc rong hoac thieu toan hang o cuoi")

    # Buoc 3: Đưa các toán tử còn lại ra f
    while stack:
        top = stack.pop()

        # [Báo lỗi] Còn '(' chưa được đóng
        if top == '(':
            raise ValueError("Thieu dau ')' (dau '(' chua duoc dong)")

        f.append(top)

    return f


# HÀM 2: TÍNH GIÁ TRỊ BIỂU THỨC HẬU TỐ
def calculate(f, x, y):
    stack = []

    for t in f:

        # Đưa biến vào stack
        if t == 'x':
            stack.append(x)
        elif t == 'y':
            stack.append(y)

        # Đưa hằng số (pi, e) vào stack
        elif t in consts:
            stack.append(consts[t])

        # Xử lý dấu +, - một ngôi
        elif t in ('u+', 'u-'):
            a = stack.pop()
            stack.append(a if t == 'u+' else -a)

        # Xử lý các hàm một biến (sqrt, ln, log, sin, cos, ...)
        elif t in funcs:
            a = stack.pop()
            stack.append(funcs[t](a))

        # Xử lý phép toán hai ngôi
        elif t in ('+', '-', '*', '/', '^'):
            b = stack.pop()
            a = stack.pop()

            if t == '+':
                stack.append(a + b)
            elif t == '-':
                stack.append(a - b)
            elif t == '*':
                stack.append(a * b)
            elif t == '/':
                stack.append(a / b)
            else:
                stack.append(a ** b)

        # Nếu là số thì đưa vào stack
        else:
            stack.append(float(t))

    return stack[0]


# ÁP DỤNG VÀO THUẬT TOÁN EULER
s = input("Nhap phuong trinh vi phan: y'= ")
f = to_postfix(s)

print("Nhap cac gia tri ban dau:")
x = float(input("Nhap x0 = "))
X = float(input("Nhap diem cuoi cua khoang X = "))
u = float(input("Nhap u0 = "))
n = int(input("Nhap so diem chia n = "))

x0 = x
h = (X - x0) / n
i = 0

print(f"{'i':<10}{'x_i':<15}{'u_i':<15}")
print(f"{i:<10}{x:<15.4f}{u:<15.6f}")

# Thực hiện n bước Euler
for i in range(1, n + 1):
    u = u + h * calculate(f, x, u)
    x = x0 + h * i

    print(f"{i:<10}{x:<15.4f}{u:<15.6f}")