FROM mysql:5.7.43

WORKDIR /app

RUN yum install -y python3
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["--character-set-server=utf8mb4", "--collation-server=utf8mb4_general_ci"]
# CMD ["sleep", "infinity"]
