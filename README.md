# Monitor de Estoque Kanban Inteligente — Relatório Técnico

---

## Identificação do Candidato

- **Nome completo:** Davi Neemias Cruz de Oliveira
- **GitHub:** Davincoliveira

---

## Visão Geral da Solução

O projeto implementa um monitor de estoque baseado em um sensor de peso HX711 conectado a um ESP32. O sistema acompanha a quantidade de peças em uma caixa e identifica quatro situações:

1. **Estoque Regular:** peso acima do limite mínimo.
2. **Alerta de Reposição:** peso igual ou inferior a 150g.
3. **Reabastecido:** a caixa retorna a 5000g após um alerta de reposição.
4. **Anomalia:** leitura de 0g, indicando ausência da caixa ou possível falha do sensor.

As mensagens de status e eventos são enviadas pela comunicação Serial e validadas pelos testes automatizados executados via Wokwi CLI.

---

## Arquitetura do Sistema Embarcado

O firmware é executado no arquivo `src/main.py`. Após inicializar os pinos do HX711 e exibir a mensagem inicial, o sistema entra em um loop contínuo:

1. Leitura do sensor HX711.
2. Conversão da leitura para o valor correspondente em gramas.
3. Atualização da máquina de estados.
4. Impressão da mensagem correspondente ao estado atual.

O sistema utiliza quatro estados:

| Estado | Valor | Descrição |
|---|---:|---|
| `STATE_REGULAR` | 0 | Estoque acima do limite mínimo |
| `STATE_RESTOCK_ALERT` | 1 | Peso igual ou inferior a 150g |
| `STATE_REFILLED` | 2 | Caixa reabastecida após um alerta |
| `STATE_ANOMALY` | 3 | Leitura de 0g |

A leitura do HX711 é realizada diretamente pelo firmware por meio de manipulação dos pinos GPIO, utilizando o protocolo de leitura de 24 bits do componente.

---

## Componentes Utilizados na Simulação

- **ESP32 DevKit C v4:** executa o firmware MicroPython.
- **HX711:** realiza a leitura do sensor de peso.
- **Serial Monitor:** exibe as mensagens de status do sistema.

O HX711 utiliza os pinos GPIO4 para dados (DOUT) e GPIO5 para clock (CLK), conforme definido no `diagram.json`.

---

## Decisões Técnicas Relevantes

- Os estados do sistema foram definidos como constantes inteiras, facilitando a leitura e manutenção do código.
- A lógica de transição foi centralizada na função `update_state()`.
- O protocolo do HX711 foi implementado diretamente no código, sem dependências externas.
- Os limites de peso foram definidos como constantes no início do programa:

```python
STOCK_FULL_G = 5000
STOCK_MINIMUM_G = 150
STOCK_ANOMALY_G = 0
```

O loop principal realiza o processamento continuamente, permitindo que as alterações de peso sejam detectadas durante a simulação.

---

## Resultados Obtidos

O sistema apresentou os seguintes comportamentos nos testes automatizados:

Inicialização correta com a mensagem Sistema Kanban Inicializado.
Detecção do alerta de reposição ao atingir o limite mínimo.
Detecção do reabastecimento quando o peso retorna ao valor de caixa cheia.
Detecção de anomalia quando o sensor retorna 0g.
O Teste 1 — Consumo Parcial — permaneceu como a única falha identificada no pipeline.

A falha está relacionada ao tratamento da transição entre o estado de anomalia e uma leitura válida de estoque. Na versão final, o estado inicial é STATE_ANOMALY, e a lógica de transição não contempla adequadamente todos os caminhos de retorno para STATE_REGULAR após uma leitura válida.

---

## Comentários Adicionais

Durante o desenvolvimento, a principal dificuldade foi lidar com o comportamento inicial do sensor HX711 na simulação e com a interação entre esse comportamento e a máquina de estados do firmware.

O projeto também evidenciou a importância de mapear todos os caminhos de transição de uma máquina de estados e de considerar o comportamento inicial dos componentes simulados.

Como possíveis melhorias futuras, poderiam ser implementadas filtragem das leituras do HX711, confirmação de múltiplas leituras antes de declarar uma anomalia e tratamento mais robusto de transições entre estados.