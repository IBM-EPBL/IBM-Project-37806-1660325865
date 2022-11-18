FROM python:3.7.0

WORKDIR /app

RUN curl https://public.dhe.ibm.com/ibmdl/export/pub/software/data/db2/drivers/odbc_cli/linuxx64_odbc_cli.tar.gz > linuxx64_odbc_cli.tar.gz
RUN pip3 install setuptools
COPY requirements.txt requirements.txt
RUN pip install --upgrade setuptools pip
ENV IBM_DB_HOME /app/db2_license/licenses/clidriver
ENV LD_LIBRARY_PATH /app/db2_license/licenses/clidriver/lib:$LD_LIBRARY_PATH
RUN python3 -m pip install --upgrade pip
RUN pip3 install setuptools_rust
RUN pip3 install -r requirements.txt
RUN pip3 install setuptools

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]