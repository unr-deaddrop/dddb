FROM debian:latest
RUN DEBIAN_FRONTEND=noninteractive apt update && apt install -yq --no-install-recommends curl libopencv-dev build-essential ffmpeg clang libssl-dev libclang-dev ca-certificates python3
RUN curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain nightly -y
RUN mkdir /dddb
WORKDIR /dddb
ENV PATH="/root/.cargo/bin:${PATH}"
ADD . /dddb
CMD /bin/bash
