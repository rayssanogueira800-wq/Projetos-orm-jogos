# Ilha dos Enigmas

Jogo 2D top-down de exploração, sobrevivência leve e resolução de enigmas, feito em Python com Pygame. O jogador atravessa quatro ilhas, administra fome, sede e sono e resolve desafios de texto, arrastar e soltar, formas e sequência lógica.

## Requisitos

- Python 3.10 ou superior
- Pygame 2.5.2 ou superior

## Instalação

No terminal, dentro da pasta do projeto:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

Instale a dependência e execute:

```bash
python -m pip install -r requirements.txt
python main.py
```

## Controles

| Ação | Controle |
|---|---|
| Mover | `WASD` ou setas |
| Interagir com altar, recursos e barco | `E` |
| Abrir/interagir também pelo botão da tela | Clique em **INTERAGIR [E]** |
| Responder ao enigma textual | Digitar e pressionar `Enter` |
| Arrastar relíquias | Clique, segure e solte com o mouse |
| Escolher formas e runas | Clique com o mouse |
| Fechar um enigma | `Esc` |

## Como jogar

1. Explore a ilha e encontre o altar no centro para iniciar o enigma.
2. Recolha frutas, beba água e descanse nos pontos indicados no mapa.
3. Ao resolver o enigma, o barco no sul da ilha será liberado.
4. Interaja com o barco para seguir para a próxima ilha.
5. Resolva os quatro enigmas para concluir a jornada.

Os recursos continuam diminuindo durante a exploração e durante os enigmas. Caso uma barra chegue a zero, o jogador pode se recuperar no abrigo; o progresso dos enigmas é preservado.

## Estrutura

```text
ilha_dos_enigmas/
├── main.py          # Inicialização do Pygame
├── game.py          # Mundo, personagem, sobrevivência e interface
├── puzzles.py       # Os quatro enigmas e seus controles
├── settings.py      # Dimensões, cores e parâmetros
├── requirements.txt # Dependências Python
├── README.md        # Instalação e instruções
├── Agents.md        # Diretrizes para agentes de código
└── CLAUDE.md        # Entrada de instruções para Claude Code
```

## Observações técnicas

- Todos os elementos visuais são desenhados com primitivas do Pygame. Não são necessários arquivos de imagem, áudio ou fontes adicionais.
- A lógica dos enigmas fica isolada em `puzzles.py`; cada puzzle implementa `draw()` e `handle_event()`.
- As configurações globais ficam em `settings.py` para facilitar ajustes de resolução, velocidade e drenagem dos recursos.
