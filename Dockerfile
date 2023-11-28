FROM debian:latest
RUN apt update && apt install -y curl libopencv-dev build-essential ffmpeg clang libssl-dev libclang-dev
RUN curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain nightly -y
RUN mkdir /dddb
WORKDIR /dddb
ENV PATH="/root/.cargo/bin:${PATH}"
ADD . /dddb
CMD /bin/bash
