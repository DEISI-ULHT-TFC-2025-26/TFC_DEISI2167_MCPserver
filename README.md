# MCP Server: Integração fluída e segura entre LLMs e Data Warehouses

Este repositório contém a implementação de um servidor baseado no Model Context Protocol (MCP). O objetivo principal é servir de ponte segura e padronizada entre Modelos de Linguagem (LLMs) e sistemas de dados estruturados, como Data Warehouses. 
O projeto consiste numa nova adoção de IA nas empresas, com uma integração segura, auditável e determinística entre LLMs e grandes sistemas de dados.

## ✨ Principais Funcionalidades
O servidor expõe um conjunto de *tools* que permitem aos agentes de IA interagir autonomamente com os dados:

* **Gestão de Conexões Dinâmicas:** Capacidade de ligar a múltiplas bases de dados através de identificadores ou nomes configurados.
* **Exploração de Metadados:** Listagem de esquemas, tabelas (Factos e Dimensões) e extração de relacionamentos/chaves estrangeiras para compreensão do modelo de dados pelo LLM.
* **Execução Segura de Consultas:** Execução de scripts SQL estritamente limitados a operações de leitura (`SELECT`).
* **Glossário de Negócio Integrado:** Consulta de termos, métricas e acrónimos corporativos (ex: *YTD Revenue*, *Churn Rate*) para garantir que o LLM calcula os KPIs corretamente.
* **Exportação de Dados:** Geração de ficheiros formatados a partir dos resultados das consultas em CSV, JSON e Excel (`.xlsx`).

## 🛠️ Tecnologias
* **Linguagem:** Python
* **Frameworks:** FastMCP, FastAPI
* **Base de Dados:** MS SQL Server (`pymssql`), SQLite (para configurações de servidor)
* **Integração IA:** Langflow, Model Context Protocol (MCP)

## 📋 Pré-requisitos
Para que o servidor funcione e interaja corretamente com os modelos de linguagem, é necessário garantir a seguinte infraestrutura:

* **Python 3.10+**: Instalado no ambiente onde o servidor vai correr.
* **Cliente MCP (Langflow)**: Uma instância local ou em cloud do Langflow configurada para atuar como agente e consumir as *tools* do servidor. Em alternativa, qualquer outro cliente compatível com o protocolo MCP (ex: Claude Desktop).
* **Motor de Base de Dados**: Uma instância de Microsoft SQL Server a correr localmente ou num servidor remoto, onde os Data Warehouses (ex: BikeStores, MediaFlix) estejam alojados.

## ⚙️ Instalação e configuração

1. Clonar o repositório
2. Criar o ambiente virtual e ativá-lo:
   - **Mac/Linux:** `python -m venv venv` e depois `source venv/bin/activate`
   - **Windows:** `venv\Scripts\activate`
3. Instalar as dependências executando: `pip install -r requirements.txt`
4. O sistema corre em simultâneo a API e o Servidor MCP, execute o comando: `python server.py`
5. A API ficará disponível em: `http://localhost:9991`
6. Clicar no playground, com a arquitetura no Langflow, e interagir com o agente.

## 🔗 Links úteis
* 🎥 [Demonstração no Youtube](https://youtu.be/bJ8VfqrNo5A)
* 📄 [Relatório do Projeto](docs/TFC_a22303085.pdf)

---

**Autor:** Fábio Jorge (a22303085)