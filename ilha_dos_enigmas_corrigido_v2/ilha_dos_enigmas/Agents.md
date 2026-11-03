# Diretrizes do Projeto — Ilha dos Enigmas

## Objetivo
Manter e evoluir um jogo 2D top-down de exploração, sobrevivência leve e puzzles, desenvolvido em Python com Pygame.

## Arquitetura
- `main.py`: inicialização e encerramento do Pygame.
- `game.py`: loop principal, estados, movimentação, ilhas, recursos e interface.
- `puzzles.py`: implementação isolada dos quatro enigmas.
- `settings.py`: constantes, dimensões, cores e parâmetros de balanceamento.

## Convenções
- Use Python 3.10+ e mantenha compatibilidade com Pygame 2.x.
- Prefira funções e classes pequenas, com nomes claros e responsabilidades únicas.
- Mantenha textos visíveis ao jogador em português brasileiro.
- Não adicione dependências ou assets externos sem necessidade; priorize os recursos vetoriais do Pygame.
- Centralize novos parâmetros globais em `settings.py`.
- Preserve a separação entre lógica do mundo e lógica específica dos puzzles.

## Contrato dos puzzles
Cada puzzle deve expor:
- `solved: bool` para indicar conclusão;
- `draw(surface, fonts, accent)` para renderização;
- `handle_event(event) -> bool`, retornando `True` quando for resolvido.

Ao adicionar uma ilha, atualize `ISLANDS` em `game.py` e `create_puzzle()` em `puzzles.py`, mantendo a progressão e os controles consistentes.

## Qualidade e validação
- Antes de concluir mudanças, execute `python -m compileall .`.
- Quando Pygame estiver instalado, valide o jogo com `python main.py`.
- Teste: iniciar nova partida, movimentar, coletar recursos, resolver cada puzzle, liberar o barco, trocar de ilha e concluir a jornada.
- Evite alterar o contrato de eventos ou estados sem atualizar todos os consumidores.
- Não remova funcionalidades existentes sem necessidade; explique alterações de comportamento no README.
