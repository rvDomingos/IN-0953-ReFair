# Por que o ReFAIR erra

> A versão difícil está em [analise-raiz-xgboost.md] / [metricas-formais-item-a.md](metricas-formais-item-a.md).
> Aqui é a versão **MUITO simples**. Prometido.

---

## O robô que não sabe ler 🤖

Imagina um robô que separa frases em caixas (uma caixa "Transporte", uma "Saúde", uma "Dinheiro"…).

Mas tem um segredo: **o robô NÃO lê as palavras.** Ele só olha **qual palavra está no lugar número 3** da frase. E decora.

---

## A frase que ENSINARAM pro robô (a "dele" 📘)

> "As a **transportation** researcher, I want to use summarization to summarize news about transportation policies…"
>
> (*"Como pesquisador de **transporte**, quero resumir notícias sobre políticas de transporte…"*)

Olha o **lugar número 3**: a palavra é **"transportation"** (transporte). 🚆

O robô decorou:
> 🤖 *"Se no lugar 3 tiver a palavra 'transportation' → caixa **Transporte**!"*

E ele acertou **toda vez** no treino. Por quê? Porque **todas** as frases de treino tinham a palavra "transportation" ali no lugar 3. Fácil! ✅ ✅ ✅ (100% de acerto)

---

## A NOSSA frase (a do UStAI 📗)

> "As a **driver**, I want a car that uses AI to react faster in emergencies…"
>
> (*"Como **motorista**, quero um carro com IA pra reagir mais rápido…"*)

Qualquer pessoa sabe: motorista + carro = **Transporte**, óbvio. 🚗

Mas o robô olha o **lugar número 3**… e vê **"driver"** (motorista), **não** "transportation".

> 🤖 *"Hã?? 'driver' não é a palavra que eu decorei… não sei o que fazer… joga na caixa Biologia! 🐸"*

❌ **ERRADO.** E foi isso que aconteceu **354 vezes** — o robô jogou um monte de frase na caixa errada ("Biologia"), só porque a palavra do lugar 3 não era a que ele decorou.

---

## 🟦 A cascata do erro (diagrama pro slide)

O ReFAIR trabalha em **3 etapas em fila**: primeiro o domínio, depois a tarefa de ML, depois os atributos sensíveis. Cada etapa **recebe o resultado da anterior**. Então, se a **primeira** erra, o erro **escorre** por todas — uma cascata 💧.

```text
+---------------------------------------+
| USER STORY                            |
| "As a driver, I want a car..."        |
+---------------------------------------+
                    |
            v  (o erro desce)
+---------------------------------------+
| 1) DOMINIO   <- o estagio que erra    |
| le SO a palavra do LUGAR 3            |
| [X] ve "driver"  ->  cai em Biologia  |
+---------------------------------------+
                    |
            v  (o erro desce)
+---------------------------------------+
| 2) ML TASK                            |
| herda o dominio errado                |
| [X] tarefa vazia ou errada            |
+---------------------------------------+
                    |
            v  (o erro desce)
+---------------------------------------+
| 3) ATRIBUTOS SENSIVEIS                |
| herda tudo errado                     |
| [X] recomendacao final errada         |
+---------------------------------------+
```

> ⚡ **90,6% dos erros NASCEM no estágio 1** (o domínio) — os outros dois só **herdam**. Conserta o topo da cascata e o resto melhora junto.

---

## Por que isso é burrice 🫏

O robô **decorou a PALAVRA**, não entendeu o **ASSUNTO**.

- Pra ele, "driver" (motorista) e "transportation" (transporte) são **coisas totalmente diferentes**, porque são palavras diferentes.
- Pra você e pra mim, são a **mesma ideia**: transporte! 🚗🚆

É como uma criança que aprende *"a resposta é sempre a 3ª figurinha"* — em vez de **entender** o desenho. Muda a ordem das figurinhas e ela se perde. 🃏

---

## Em uma frase 🎯

> **O ReFAIR não entende o que a frase QUER DIZER. Ele só decora qual palavra fica em qual lugar.**
> No treino dele, as palavras estavam sempre no mesmo lugar → acertou tudo.
> Nas nossas frases, as palavras estão em outros lugares → errou quase tudo (só 9 em 100). 😵

---

## E qual seria o jeito CERTO? ✅

Um robô esperto olharia o **SENTIDO**, não o lugar:

> 🤖✨ *"Tem carro? tem motorista? tem estrada? tem trânsito? → é **Transporte**!"*
>
> (não importa em que lugar da frase essas palavras aparecem)

Aí ele entenderia que **"driver" e "transportation" são a mesma família** — e acertaria a nossa frase também. 🎉

**E foi isso que a gente fez!** Trocamos o "olhar o lugar 3" por "olhar o sentido" (embeddings). O acerto do domínio **pulou de 9% para 37%** (4× mais), e o robô **parou de jogar tudo na caixa "Biologia"**. 🚀

---

## Resumão pra colar na geladeira 🧲

| | Robô do ReFAIR 🤖 | Robô esperto ✅ |
|---|---|---|
| O que olha | a **palavra no lugar 3** | o **sentido** da frase toda |
| No treino dele | acerta 100% | acerta |
| Nas nossas frases | erra (só 9%) | acertaria |
| Por quê | decorou, não entendeu | entende o assunto |

**Moral da história:** o ReFAIR é um ótimo **decorador** e um péssimo **entendedor**. Por isso ele vai bem nas frases de casa e mal nas frases do mundo real. 🏠➡️🌍

---

*Arquivos "adultos" com os números e o código: [metricas-formais-item-a.md](metricas-formais-item-a.md) · [resultados-experimento-refair-ustai.md](resultados-experimento-refair-ustai.md) · [o-que-falta.md](o-que-falta.md)*
