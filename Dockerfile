FROM gcr.io/dataflow-templates-base/python3-template-launcher-base

ARG WORKDIR=/dataflow/template
RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}

COPY requirements.txt .
COPY example/__init__.py ./example/__init__.py
COPY example/cloud_tasks.py ./example/cloud_tasks.py

ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${WORKDIR}/requirements.txt"
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/example/cloud_tasks.py"

RUN pip install -U --quiet apache-beam[gcp]
RUN pip install -U -r ./requirements.txt
