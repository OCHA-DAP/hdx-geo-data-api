FROM ghcr.io/osgeo/gdal:alpine-normal-3.11.4

WORKDIR /srv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV GDAL_NUM_THREADS=ALL_CPUS
ENV OGR_GEOJSON_MAX_OBJ_SIZE=0
ENV OGR_ORGANIZE_POLYGONS=ONLY_CCW

RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    apk add --no-cache python3 && \
    python -m venv /opt/venv && \
    pip install --no-cache-dir -r requirements.txt

COPY app ./

CMD ["fastapi", "run", "app"]
