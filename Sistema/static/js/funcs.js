// Obtenha os dados do template
var dadosCarros = {{ dados | tojson | safe }};
    
// Função para preencher um campo de seleção com base em dados
function preencherSelect(elementId, dataKey) {
    var select = document.getElementById(elementId);
    var uniqueValues = [...new Set(dadosCarros.map(item => item[dataKey]))];
    uniqueValues.forEach(function (value) {
        var option = document.createElement("option");
        option.value = value;
        option.text = value;
        select.appendChild(option);
    });
}

// Preencha os campos de seleção com os dados dos carros
preencherSelect("tipo", "tipo");
preencherSelect("marca", "marca");
preencherSelect("modelo", "modelo");
preencherSelect("ano", "ano");