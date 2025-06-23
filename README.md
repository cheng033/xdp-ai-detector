# xdp-ai-detector

一個以 eBPF/XDP 實作的即時流量監測結合AI異常偵測


## 快速開始

1. **建置 Docker 映像檔**
    ```bash
    sudo docker build -t xdp-anomaly-detector .
    ```

2. **啟動 Container（請依網卡名稱修改介面 ex. enp0s3）**
    ```bash
    sudo docker run --rm -it \
        --privileged \
        --net=host \
        -v /lib/modules:/lib/modules:ro \
        -v /usr/src:/usr/src:ro \
        xdp-anomaly-detector:latest -i enp0s3
    ```

3. **測試:  使用另一台主機製造 TCP flood 應該會跳出 Anomaly**
   ```bash
   sudo hping3 -S <enp0s3 ip> -p 80 --flood
   ```



