FROM python:3.13-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 9990 9991
CMD ["python", "server.py"] 
#CMD ["uvicorn", "server:mcp", "--host", "0.0.0.0", "--port", "9990"]  
#CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9991"] 
