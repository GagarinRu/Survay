FROM python:3.13

RUN groupadd -g 1000 app_group && \
    useradd -r -u 1000 -g app_group -m -s /sbin/nologin app_user && \
    mkdir -p /app /app/staticfiles /app/media && \
    chown -R app_user:app_group /app && \
    chmod -R 775 /app /app/staticfiles /app/media

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip

COPY --chown=app_user:app_group requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt \
    && pip cache purge

COPY --chown=app_user:app_group src/ .

COPY --chown=app_user:app_group entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

USER app_user

ENTRYPOINT ["/entrypoint.sh"]