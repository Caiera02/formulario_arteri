async function BuscaCep() {
    // 1. Pega o valor do input de CEP
    const campoCep = document.getElementById('cep');
    let cep = campoCep.value.replace(/\D/g, '');

    // 2. Valida se tem 8 dígitos
    if (cep.length !== 8) {
        alert('Formato de CEP inválido.');
        return;
    }

    const url = `https://viacep.com.br/ws/${cep}/json/`;

    try {
        // 3. Faz a requisição assíncrona
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Erro ao conectar na API ViaCEP');
        }

        // 4. AQUI É CRIADA A VARIÁVEL 'dados' CORRETAMENTE
        const dados = await response.json();

        // 5. Verifica se o CEP existe na base do ViaCEP
        if (dados.erro) {
            alert('CEP não encontrado!');
            limparCampos();
            return;
        }

        // 6. Injeta os dados nos inputs mapeados pelos IDs do HTML
        document.getElementById('rua').value = dados.logradouro;
        document.getElementById('bairro').value = dados.bairro;
        document.getElementById('cidade').value = dados.localidade;

    } catch (error) {
        console.error('Erro na requisição:', error);
        alert('Erro ao buscar o CEP. Tente novamente.');
        limparCampos();
    }
}

// Função auxiliar para limpar em caso de erro
function limparCampos() {
    document.getElementById('rua').value = "";
    document.getElementById('bairro').value = "";
    document.getElementById('cidade').value = "";
    document.getElementById('cep').value = "";
}