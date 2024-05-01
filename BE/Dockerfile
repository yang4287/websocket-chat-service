FROM python:3.11
# 設置工作目錄
WORKDIR /app

# 安裝依賴
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個應用到容器中
COPY . .

# 設置一個命令讓 uvicorn 在開發模式下運行，自動重啟並開啟debug模式
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]