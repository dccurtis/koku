FROM centos/python-36-centos7
RUN git config --global http.sslVerify false
RUN git clone https://gitlab.cee.redhat.com/insights-qe/iqe-tests.git /opt/app-root/src/iqe-tests/
ADD settings.local.yaml /opt/app-root/src/iqe-tests/iqe/conf
WORKDIR /opt/app-root/src/iqe-tests/
RUN pip install --upgrade pip
RUN pip install devpi-client
RUN devpi use http://devpi.ocp-sprout-02.cmqe.lab.eng.rdu2.redhat.com/test/psav --set-cfg
RUN pip install -U pip setuptools setuptools_scm wheel devpi-client
RUN pip install -e .

WORKDIR /opt/app-root/src/
RUN git clone -b docurtis/pip_cfg_update https://gitlab.cee.redhat.com/insights-qe/hccm-plugin.git
RUN iqe plugin install --editable /opt/app-root/src/hccm-plugin/
USER root
# RUN mkdir /test
# RUN mkdir /test/aws_local && mkdir /test/aws_local_0 && mkdir /test/aws_local_1 && mkdir /test/aws_local_2 && mkdir /test/aws_local_3 && mkdir /test/aws_local_4 && mkdir /test/insights_local
