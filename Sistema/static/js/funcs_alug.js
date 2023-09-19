// Função para validar se a data e hora selecionadas são futuras
function validarDataHora(event) {
    event.preventDefault(); // Impede o envio padrão do formulário

    let inputDateTime = document.getElementById("data_inicial");
    let valorInput = inputDateTime.value;
    let dataHoraSelecionada = new Date(valorInput);
    let agora = new Date();

    // Arredonde as datas para o minuto mais próximo
    dataHoraSelecionada.setSeconds(0, 0);
    agora.setSeconds(0, 0);

    console.log(dataHoraSelecionada)
    console.log(agora)

    // Verifica se a data e hora selecionadas são no futuro
    if (dataHoraSelecionada < agora) {
        alert("Por favor, selecione uma data e hora futuras.");
        return false; // Impede o envio do formulário
    }


    // Se a validação for bem-sucedida, você pode continuar com o envio do formulário aqui
    document.getElementById("form_aluguel").submit();
}

// Adiciona um ouvinte de evento ao formulário para chamar a função de validação quando for enviado
document.getElementById("form_aluguel").addEventListener("submit", validarDataHora);

