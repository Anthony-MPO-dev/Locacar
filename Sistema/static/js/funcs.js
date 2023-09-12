// Impede a inserção de anos invalidos
function validarAno(input) {
    var valor = parseInt(input.value, 10); // Converte o valor inserido em um número inteiro
    if (valor < 1900 || valor > 2023) {
        input.setCustomValidity("Digite um ano entre 1900 e 2023.");
    } else {
        input.setCustomValidity(""); // Limpa a mensagem de erro personalizada
    }
}


function verificarSelecao() {
    var selectElement = document.getElementById("tipo_cadastro");
    var selectedValue = selectElement.value;

    if (selectedValue !== "") {
        return true;
        
    } else {
        alert("Por favor, selecione um Tipo de Carro.");
        return false;
    }
}



