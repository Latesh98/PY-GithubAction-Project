FROM python:3.9-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN mkdir -p /app/data
RUN pip install --no-cache-dir --target=/app/dep -r requirements.txt

FROM gcr.io/distroless/python3-debian11:nonroot
WORKDIR /app
COPY --from=builder /app/dep /app/dep
COPY --from=builder /app/data /app/data
COPY --chown=nonroot:nonroot . .
ENV PYTHONPATH=/app/dep
USER nonroot
EXPOSE 5000
CMD ["app.py"]
