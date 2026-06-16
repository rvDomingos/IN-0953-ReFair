# Mapeamento de domínios — UStAI → ReFAIR (versão slide)

**Ideia do slide:** mostrar que o UStAI cobre boa parte dos domínios do ReFAIR — e onde NÃO cobre.

---

## Número de impacto

# **25 de 34**
### domínios do ReFAIR são exercitados pelo UStAI (**74%**)

```text
Cobertura dos 34 domínios:
[##########################______]  25 cobertos  |  9 sem nenhuma US
```

---

## Como os temas reais do UStAI caem nos domínios do ReFAIR

| Área | Domínios ReFAIR (US no UStAI) | Exemplo de tema real (abstract) |
|---|---|---|
| **Saúde & Medicina** | Health (90), Cardiology (30), Endocrinology (30), Medicine (30), Pediatrics (30), Pharmacology (30), Radiology (30) | "Diagnóstico de doença cardíaca", "Detecção de tuberculose em raio-X" |
| **Comportamento & Social** | Psychology (120), Social Media (30), Social Networks (60), Social Work (30), Demography (30) | "Recrutamento por IA", "Detecção de agressão no Twitter" |
| **Tecnologia & Dados** | Information Systems (120), Computer Vision (60), Computer Networks (30) | "Recomendação em e-commerce", "Detecção de intrusão em rede" |
| **Economia** | Economics (90), Finance & Marketing (90) | "Previsão de renda/pobreza", "Identificação de anúncios" |
| **Transporte** | Transportation (120) | "ADAS — reconhecimento de intenção do motorista" |
| **Direito & Política** | Law (30), Political Science (30) | "Previsão de reincidência criminal" |
| **Cultura & Linguagem** | Linguistics (30), Library (30), News (30), Music (30), Sport (30) | "Busca semântica de notícias", "Sucesso de playlists" |

> Os 3 maiores: **Transportation, Psychology e Information Systems (120 US cada)**.

---

## Os 9 domínios que o UStAI NÃO cobre

```text
Biology · Dermatology · Education · Literature · Movies
Nephrology · Plant Science · Sociology · Urban Studies
```

> São domínios da ontologia do ReFAIR **sem nenhuma user story** no UStAI → **não foram avaliados**. É uma **ameaça de cobertura** (a avaliação vale para os 25 cobertos).

---

## Frase de fecho (pro slide)

> **O UStAI testa o ReFAIR em 25 domínios reais e variados** — de saúde a transporte, de finanças a redes sociais. **9 ficam de fora**, e isso é declarado como limitação.

---

*Dados: `documents/datasets/essenciais/equivalencia-ustai-synthetic.csv` · detalhamento completo em [equivalencia-dominios-ustai-synthetic.md](equivalencia-dominios-ustai-synthetic.md) e [pessoa4-mapeamento-dominios.md](pessoa4-mapeamento-dominios.md).*
