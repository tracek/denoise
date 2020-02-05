FROM ubuntu:18.04

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y wget curl bzip2 ca-certificates git build-essential cmake ffmpeg && \
    curl -sL https://deb.nodesource.com/setup_13.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.7.12-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete && \
    /opt/conda/bin/conda clean -afy

RUN conda install -c conda-forge -c comet_ml --quiet --yes \
    tensorflow=2.0.0 \
    keras=2.3.1 \
    h5py=2.10.0 \
    comet_ml=3.0.2 \
    click=7.0 \
    joblib=0.14.1 \
    swig=4.0.1 \
    pip && \
    pip install webrtc-audio-processing==0.1.3

RUN git clone https://github.com/emscripten-core/emsdk.git /opt/emsdk && \
    ./opt/emsdk/emsdk install fastcomp-clang-e1.38.21-64bit && \
    ./opt/emsdk/emsdk install emscripten-1.38.21 && \
    ./opt/emsdk/emsdk activate emscripten-1.38.21 && \
    ./opt/emsdk/emsdk activate fastcomp-clang-e1.38.21-64bit && \
    echo "source /opt/emsdk/emsdk_env.sh" >> ~/.bashrc

CMD [ "/bin/bash" ]