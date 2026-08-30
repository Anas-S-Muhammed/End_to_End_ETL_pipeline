FROM apache/airflow:2.9.3

# Keep the Python dependencies used by the DAG code reproducible instead of
# installing an unpinned set every time an Airflow container starts.
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
