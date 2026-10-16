# Industrial Frontier — estabilização do núcleo

Esta branch aplica correções conservadoras à versão publicada em `main`. Ela **não substitui** uma comparação com o ZIP mais recente do projeto: esse arquivo não está anexado nesta conversa, então esta revisão usa somente o conteúdo atual do repositório.

## Escopo

- Corrigir a dupla contagem do valor patrimonial das instalações.
- Impedir que novos transportes sejam enviados quando não houver espaço reservado no armazém de destino, evitando cargas retidas por excesso de capacidade.
- Definir um comportamento explícito para falta de caixa durante a manutenção: instalações ativas são desativadas quando a empresa não consegue cobrir a manutenção do passo.
- Acrescentar testes de regressão para esses casos.

## Limitações que permanecem

- Salvamento/carregamento persistente ainda precisa ser implementado e validado em uma etapa separada.
- Não há mapa explorável, construção de colônias ou progressão tecnológica; isso pertence às próximas etapas do sandbox.
- A suíte precisa ser executada no ambiente de CI antes de considerar esta branch validada.
- A manutenção é debitada por passo de simulação; o comportamento de insolvência aqui é deliberadamente simples e pode evoluir para falência, crédito ou recuperação numa etapa posterior.

## Próximos passos

1. Executar a suíte completa em CI.
2. Revisar as regras econômicas e o modelo de ativos.
3. Implementar salvamento versionado e testes de ida e volta.
4. Criar o primeiro ciclo jogável de exploração → construção → produção → logística → expansão.
