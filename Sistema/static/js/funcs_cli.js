function validarTell(){
    var selectElement = document.getElementById("telefone");
    var numero = selectElement.value;

    // Verifica se o valor é um número e está abaixo de 999.999.999
    if (numero < 999999999 && numero > 900000000) {
        return true; // O valor está abaixo de 999.999.999
    } else {
        alert("Numero de Telefone Inválido.");
        return false; // O valor não é um número válido ou está acima de 999.999.999    
    }
}









