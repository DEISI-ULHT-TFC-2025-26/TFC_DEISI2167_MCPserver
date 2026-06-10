// Carregar as conexões assim que a página abre
document.addEventListener("DOMContentLoaded", loadConnections);

// Variavel global para guardar os dados e facilitar a edição
let connectionsData = [];

async function loadConnections() {
    const response = await fetch('/api/connections');
    connectionsData = await response.json();
    
    const tbody = document.getElementById("connections-table-body");
    tbody.innerHTML = ""; // Limpa a tabela

    connectionsData.forEach(conn => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${conn.id}</td>
            <td><strong>${conn.name}</strong></td>
            <td>${conn.dialect}</td>
            <td>${conn.driver}</td>
            <td>${conn.host || 'N/A'}</td>
            <td>${conn.port || 'N/A'}</td>
            <td>${conn.database_name}</td>
            <td>${conn.username || 'N/A'}</td>
            <td style="text-align: center;">
                <button onclick="editConnection(${conn.id})">Editar</button>
                <button onclick="deleteConnection(${conn.id})" style="background: red; color: white;">Eliminar</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function saveConnection(event) {
    event.preventDefault(); // Impede o reload da página

    const id = document.getElementById("conn_id").value;
    
    // Constrói o objeto (convertendo porto para inteiro se existir)
    const payload = {
        name: document.getElementById("name").value,
        dialect: document.getElementById("dialect").value,
        driver: document.getElementById("driver").value || null,
        host: document.getElementById("host").value || null,
        port: document.getElementById("port").value ? parseInt(document.getElementById("port").value) : null,
        username: document.getElementById("username").value || null,
        password: document.getElementById("password").value || null,
        database_name: document.getElementById("database_name").value
    };

    let url = '/api/connections';
    let method = 'POST';

    // Se tiver ID escondido no formulário, é um UPDATE (PUT)
    if (id) {
        url = `/api/connections/${id}`;
        method = 'PUT';
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert(id ? "Atualizado com sucesso!" : "Criado com sucesso!");
            resetForm();
            loadConnections(); // Recarrega a tabela
        } else {
            const error = await response.json();
            alert("Erro: " + error.detail);
        }
    } catch (err) {
        alert("Erro de comunicação com a API.");
    }
}

function editConnection(id) {
    // Procura o objeto na lista
    const conn = connectionsData.find(c => c.id === id);
    if (!conn) return;

    // Preenche o formulário
    document.getElementById("conn_id").value = conn.id;
    document.getElementById("name").value = conn.name;
    document.getElementById("dialect").value = conn.dialect;
    document.getElementById("driver").value = conn.driver || '';
    document.getElementById("host").value = conn.host || '';
    document.getElementById("port").value = conn.port || '';
    document.getElementById("username").value = conn.username || '';
    // password idealmente não é devolvida no GET por segurança, mas se for:
    document.getElementById("password").value = conn.password || '';
    document.getElementById("database_name").value = conn.database_name;

    document.getElementById("form-title").innerText = "Editar Ligação #" + conn.id;
    document.getElementById("save-btn").innerText = "Atualizar";
    window.scrollTo(0, 0); // Sobe a página para o formulário
}

async function deleteConnection(id) {
    if (!confirm(`Tem a certeza que deseja eliminar a conexão #${id}?`)) return;

    const response = await fetch(`/api/connections/${id}`, {
        method: 'DELETE'
    });

    if (response.ok) {
        loadConnections(); // Recarrega a tabela
    } else {
        alert("Erro ao eliminar.");
    }
}

function resetForm() {
    document.getElementById("db-form").reset();
    document.getElementById("conn_id").value = "";
    document.getElementById("form-title").innerText = "Nova Ligação";
    document.getElementById("save-btn").innerText = "Guardar";
}