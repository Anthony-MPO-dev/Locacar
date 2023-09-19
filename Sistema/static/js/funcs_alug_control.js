const opcoesRadio = document.querySelectorAll('input[type="radio"][name="escolha"]');
const campos = document.querySelectorAll('.campo');

opcoesRadio.forEach(opcao => {
  opcao.addEventListener('change', () => {
    campos.forEach(campo => {
      campo.style.display = 'none';
    });

    const opcaoSelecionada = document.getElementById(`campo-${opcao.value}`);
    if (opcaoSelecionada) {
      opcaoSelecionada.style.display = 'block';
    }
  });
});


campos.forEach(campo => {
    campo.style.display = 'none';
  });





