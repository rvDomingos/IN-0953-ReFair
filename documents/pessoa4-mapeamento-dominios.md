# Pessoa 4 — Mapeamento Domínios UStAI ↔ ReFair

Mapeamento dos **roles do UStAI** (eixo de domínio do dataset) atribuídos à Pessoa 4 para os **34 domínios da ontologia ReFair Synthetic**. Fonte: `documents/datasets/essenciais/equivalencia-ustai-synthetic.csv`.

- **Roles (UStAI) atribuídos:** 47
- **Domínios (ReFair) cobertos:** 25 de 34

## 1. UStAI (role) → ReFair (domínio)

| UStAI — `role_shorten` | ReFair — `equivalent_domain` |
|:-----------------------|:------------------------------|
| HR specialist | Economics; Psychology |
| UX designer | Economics; Information Systems; Library; Social Networks; Transportation |
| administrator | Cardiology; Computer Networks; Economics; Endocrinology; Health; Law; Library; Medicine; Psychology; Radiology; Social Media; Social Networks; Transportation |
| analyst | Cardiology; Computer Networks; Computer Vision; Demography; Economics; Endocrinology; Finance & Marketing; Health; Information Systems; Law; Linguistics; Music; News; Political Science; Psychology; Social Networks; Social Work; Sport; Transportation |
| cardiologist | Cardiology |
| client | Economics |
| credit card issuer | Finance & Marketing |
| customer | Economics; Finance & Marketing; Information Systems |
| data engineer | Computer Vision; Economics; Finance & Marketing |
| defense contractor | Political Science |
| demographer | Demography |
| economic historian | Demography |
| entrepreneur | Pharmacology |
| fact-checker | Linguistics; News |
| field commander | Political Science |
| forecasting expert | Finance & Marketing |
| government official | Economics; Law |
| grant writer | Social Work |
| manager | Computer Networks; Computer Vision; Economics; Finance & Marketing; Health; Information Systems; Library; Linguistics; Psychology; Social Media; Sport; Transportation |
| military commander | Political Science |
| musician | Music |
| non-profit organization | Economics; Psychology |
| officer | Computer Networks; Computer Vision; Economics; Endocrinology; Finance & Marketing; Health; Law; Political Science; Psychology; Social Media; Social Networks; Social Work; Transportation |
| online retailer | Information Systems |
| organizer | Social Networks |
| participant | Transportation |
| pediatrician | Pediatrics |
| person | Endocrinology; Psychology; Social Media |
| person with dietary restricttions | Computer Vision |
| playlist curator | Music |
| professional | Psychology; Transportation |
| publisher | Library |
| quality assurance specialist | Cardiology; Computer Networks; Computer Vision; Economics; Health; Information Systems; Medicine; Pediatrics; Radiology; Social Networks; Transportation |
| radiologist | Radiology |
| recruiter | Psychology |
| regulator | Endocrinology; Finance & Marketing; Pharmacology; Transportation |
| residential care staff member | Health |
| security expert | Computer Vision |
| social media moderator | Linguistics |
| software architect | Information Systems |
| specialist | Cardiology; Computer Vision; Law |
| strategist | Information Systems; Music; Political Science; Social Networks; Social Work; Sport; Transportation |
| system | Health |
| system designer | Psychology; Social Media |
| therapist | Psychology |
| vaccination site coordinator | Health |
| visually impaired person | Transportation |

## 2. ReFair (domínio) → UStAI (roles)

| ReFair — `equivalent_domain` | UStAI — `role_shorten` |
|:-----------------------------|:------------------------|
| Cardiology | administrator; analyst; cardiologist; quality assurance specialist; specialist |
| Computer Networks | administrator; analyst; manager; officer; quality assurance specialist |
| Computer Vision | analyst; data engineer; manager; officer; person with dietary restricttions; quality assurance specialist; security expert; specialist |
| Demography | analyst; demographer; economic historian |
| Economics | HR specialist; UX designer; administrator; analyst; client; customer; data engineer; government official; manager; non-profit organization; officer; quality assurance specialist |
| Endocrinology | administrator; analyst; officer; person; regulator |
| Finance & Marketing | analyst; credit card issuer; customer; data engineer; forecasting expert; manager; officer; regulator |
| Health | administrator; analyst; manager; officer; quality assurance specialist; residential care staff member; system; vaccination site coordinator |
| Information Systems | UX designer; analyst; customer; manager; online retailer; quality assurance specialist; software architect; strategist |
| Law | administrator; analyst; government official; officer; specialist |
| Library | UX designer; administrator; manager; publisher |
| Linguistics | analyst; fact-checker; manager; social media moderator |
| Medicine | administrator; quality assurance specialist |
| Music | analyst; musician; playlist curator; strategist |
| News | analyst; fact-checker |
| Pediatrics | pediatrician; quality assurance specialist |
| Pharmacology | entrepreneur; regulator |
| Political Science | analyst; defense contractor; field commander; military commander; officer; strategist |
| Psychology | HR specialist; administrator; analyst; manager; non-profit organization; officer; person; professional; recruiter; system designer; therapist |
| Radiology | administrator; quality assurance specialist; radiologist |
| Social Media | administrator; manager; officer; person; system designer |
| Social Networks | UX designer; administrator; analyst; officer; organizer; quality assurance specialist; strategist |
| Social Work | analyst; grant writer; officer; strategist |
| Sport | analyst; manager; strategist |
| Transportation | UX designer; administrator; analyst; manager; officer; participant; professional; quality assurance specialist; regulator; strategist; visually impaired person |

## 3. Como o mapeamento foi feito (e como replicar manualmente)

Esta seção documenta o **método de equivalência** usado para gerar `documents/datasets/essenciais/equivalencia-ustai-synthetic.csv` — o arquivo que alimenta este relatório. A fonte completa do raciocínio está em [documents/equivalencia-dominios-ustai-synthetic.md](equivalencia-dominios-ustai-synthetic.md); abaixo está o resumo prático para quem precisa **conferir, ajustar ou refazer** um mapeamento à mão.

### 3.1. Os dois vocabulários envolvidos

| Lado | O que é | Cardinalidade |
|---|---|---|
| **UStAI** (`UStAI-annotated_V2.pdf`) | 42 *abstracts* × 3 LLMs × 10 user stories, com `role_shorten` declarado em cada uma. O `role_shorten` é o eixo de domínio do UStAI. | 179 roles distintos |
| **Synthetic User Stories — ReFair** (`Synthetic User Stories.xlsx`) | Ontologia do ReFair, com coluna `Domain` (34 domínios de aplicação). | 34 domínios |

Os **34 domínios** do ReFair são:

`Biology, Cardiology, Computer Networks, Computer Vision, Demography, Dermatology, Economics, Education, Endocrinology, Finance & Marketing, Health, Information Systems, Law, Library, Linguistics, Literature, Medicine, Movies, Music, Nephrology, News, Pediatrics, Pharmacology, Plant Science, Political Science, Psychology, Radiology, Social Media, Social Networks, Social Work, Sociology, Sport, Transportation, Urban Studies`

### 3.2. Princípio central — desambiguar pelo *abstract*, não pelo role

O `role_shorten` sozinho **não basta** para definir o domínio. Roles genéricos (`researcher`, `developer`, `analyst`, `manager`, `user`, `administrator`, `officer`…) aparecem em dezenas de *abstracts* diferentes. Um `developer` pode estar em transporte autônomo (A1), recomendação (A25), intrusão de rede (A34) ou previsão de vendas (A35) — por isso a tabela 1 acima mostra vários domínios para esses roles.

> **Regra-mãe:** todas as user stories de um mesmo *abstract* compartilham o **mesmo domínio**, porque descrevem **um único sistema de IA**. A unidade de classificação é o **abstract (A1–A42)**, não o role.

Roles específicos (`radiologist`, `cardiologist`, `taxi driver`, `pharmacist`…) são consistentes com seu *abstract* e servem de "sanity check".

### 3.3. Passo-a-passo para mapear **um abstract** manualmente

Faça isso uma vez por abstract (A1, A2, …) — depois propague para as 30 US dele.

1. **Leia o título e o resumo do abstract** no PDF `UStAI-annotated_V2.pdf`. Identifique o sistema de IA descrito e o domínio de aplicação real-world.
2. **Escolha o `equivalent_domain` entre os 34** do ReFair, seguindo esta ordem:
   - **Match direto** — existe um domínio óbvio? (raios-X → `Radiology`; coração → `Cardiology`; trânsito → `Transportation`).
   - **Match temático mais próximo** — quando não há match perfeito, escolha o mais próximo e marque `Medium` em confiança.
   - **Sem domínio adequado** — escolha o menos ruim e marque `Low` (ex.: A4 militar → `Political Science`; A38 recrutamento → `Psychology`).
3. **Atribua confiança** (`High`/`Medium`/`Low`) e justifique em `mapping_notes` quando for `Low`.
4. **Propague** o domínio às 30 user stories daquele abstract.

### 3.4. Heurísticas para casos difíceis

| Situação | O que fazer |
|---|---|
| Role genérico (`analyst`, `developer`, `manager`) numa US | **Ignore o role** — use só o abstract. |
| Role específico discorda do abstract (ex.: `cardiologist` em A1 Transport) | Verifique o texto da US — geralmente é um *plot twist* do LLM; mantenha o domínio do abstract e registre a anomalia em `mapping_notes`. |
| Não há domínio perfeito entre os 34 | Escolha o mais próximo, marque `Low` em `domain_confidence` e justifique. |
| Estudo cobre duas áreas (ex.: saúde + redes sociais) | Escolha o domínio do **objeto de predição** (o que o modelo prevê), não o do dado de entrada. |
| Vários `abstract`s caem no mesmo domínio | É esperado — Transportation tem A1, A6, A14, A36, todos legítimos. |

### 3.5. Como conferir o mapeamento na prática

Para cada role da Tabela 1, você consegue rastrear a decisão em três cliques:

1. Pegue um role → veja qual(is) **domínio(s)** ReFair recebe nesta tabela.
2. Abra [documents/equivalencia-dominios-ustai-synthetic.md](equivalencia-dominios-ustai-synthetic.md), Seção 4, e procure o(s) abstract(s) que produziram esse domínio: lá está a **justificativa**, a **ML task âncora** e a **confiança**.
3. Se a confiança for `Low` ou `Medium`, leia as **notas** logo abaixo da tabela — elas listam as alternativas que foram consideradas e descartadas.

### 3.6. O que **não** fazer

- Decidir domínio só pelo `role_shorten` — viesa para roles genéricos.
- Tentar inventar um 35º domínio — a ontologia do ReFair é fechada em 34; use `Low` em vez disso.
- Mudar o domínio entre as user stories do mesmo abstract — elas descrevem o mesmo sistema.
