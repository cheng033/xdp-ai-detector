FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        software-properties-common \
        python3 python3-pip python3-setuptools \
        clang llvm make gcc git \
        iproute2 net-tools iputils-ping && \
    add-apt-repository universe

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-bpfcc \
        bpfcc-tools \
        libbpfcc-dev \
        python3-numpy \
        python3-pandas \
        python3-sklearn \
        python3-joblib \
        python3-matplotlib\
        kmod

WORKDIR /xdp_app
COPY . .

ENTRYPOINT ["python3", "app/monitor.py"]
CMD ["-i", "enp0s3"]

