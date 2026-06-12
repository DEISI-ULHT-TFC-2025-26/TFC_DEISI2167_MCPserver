# MCP Server: Integração Fluída e Segura entre LLMs e Data Warehouses

Este repositório contém a implementação de um servidor baseado no **Model Context Protocol (MCP)**. O objetivo principal é servir de ponte segura e padronizada entre Modelos de Linguagem (LLMs) e sistemas de dados estruturados, como Data Warehouses.

O projeto representa uma nova abordagem à adoção de IA nas empresas, com uma integração segura, auditável e determinística entre LLMs e grandes sistemas de dados.

---

## ☑️ Principais Funcionalidades

O servidor expõe um conjunto de *tools* que permitem aos agentes de IA interagir autonomamente com os dados:

- **Gestão de Conexões Dinâmicas:** Capacidade de ligar a múltiplas bases de dados através de identificadores ou nomes configurados.
- **Exploração de Metadados:** Listagem de esquemas, tabelas (Factos e Dimensões) e extração de relacionamentos/chaves estrangeiras para compreensão do modelo de dados pelo LLM.
- **Execução Segura de Consultas:** Execução de scripts SQL estritamente limitados a operações de leitura (`SELECT`).
- **Glossário de Negócio Integrado:** Consulta de termos, métricas e acrónimos corporativos (ex: *YTD Revenue*, *Churn Rate*) para garantir que o LLM calcula os KPIs corretamente.
- **Exportação de Dados:** Geração de ficheiros formatados a partir dos resultados das consultas em CSV, JSON e Excel (`.xlsx`).

---

## 🛠️ Tecnologias

| Categoria | Tecnologia |
|---|---|
| Linguagem | Python |
| Frameworks | FastMCP, FastAPI |
| Base de Dados | MS SQL Server (`pymssql`), SQLite |
| Integração IA | Langflow, Model Context Protocol (MCP) |

---

## 📋 Pré-requisitos

Graças à contentorização do projeto, o ambiente de execução é isolado e livre de dependências complexas no sistema operativo anfitrião. É necessário garantir a seguinte infraestrutura:

- **Docker / Docker Desktop:** Instalado e em execução na máquina local ou servidor.
- **Cliente MCP (Langflow):** Uma instância local ou em cloud do Langflow configurada para atuar como agente e consumir as *tools* do servidor.
- **Motor de Base de Dados:** Uma instância de Microsoft SQL Server a correr localmente ou num servidor remoto, onde os Data Warehouses (ex: BikeStores, MediaFlix) estejam alojados e acessíveis pela rede do container.

---

## ⚙️ Instalação e Configuração

### 🐳 Opção 1: Via Docker

A aplicação foi desenhada para correr de forma nativa em contentores, estando a imagem final disponível publicamente no Docker Hub.

Para iniciar o sistema, execute o seguinte comando no terminal. Este comando corre o servidor em *background* (`-d`) e expõe as portas necessárias para a API e para o transporte MCP:

```bash
docker run -d \
  -p 9990:9990 \
  -p 9991:9991 \
  --platform linux/arm64 \
  --name dw-mcp-server \
  --hostname dw-mcp-server \
  fabiojorge10/dw-mcp-server:latest
```

### 🛠️ Opção 2: Via Git (Python local)

1. Clonar o repositório:
   ```bash
   git clone <url-do-repositório>
   cd <nome-do-repositório>
   ```

2. Criar e ativar o ambiente virtual:
   - **Mac/Linux:**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   - **Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. Instalar as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Iniciar o servidor (corre em simultâneo a API e o Servidor MCP):
   ```bash
   python server.py
   ```

5. A API ficará disponível em: `http://localhost:9991`

6. Aceder ao playground, carregar a arquitetura no Langflow e interagir com o agente.

### 🔨 Opção 3: Compilação Manual da Imagem

Se pretende modificar o código fonte e gerar a sua própria imagem Docker, siga os passos abaixo na raiz do projeto:

1. Construir a imagem localmente:
   ```bash
   docker build -t <seu_utilizador>/dw-mcp-server:latest .
   ```

2. Publicar a imagem num registry:
   ```bash
   docker push <seu_utilizador>/dw-mcp-server:latest
   ```

3. Executar a nova imagem compilada:
   ```bash
   docker run -d \
     -p 9990:9990 \
     -p 9991:9991 \
     -e ADMIN_USER="admin" \
     -e ADMIN_PASSWORD="sua_password_segura" \
     --platform linux/arm64 \
     --name dw-mcp-server \
     --hostname dw-mcp-server \
     <seu_utilizador>/dw-mcp-server:latest
   ```

> **Nota:** Caso não sejam definidas variáveis de ambiente, as credenciais por defeito são `admin` / `admin`.

---

## 🔗 Links Úteis

- 🎥 [Demonstração no YouTube](https://youtu.be/qRdWHlIqgH0)
- ⚙️ [DockerHub](https://hub.docker.com/repository/docker/fabiojorge10/dw-mcp-server/general)
- 📄 [Relatório do Projeto](docs/TFC_a22303085.pdf)

---

**Autor:** Fábio Jorge (a22303085)