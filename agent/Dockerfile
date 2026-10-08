FROM python:3.11-slim

WORKDIR /mcp-finance/agent

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["sh", "-c"]
CMD ["python mcp_agent.py"]
