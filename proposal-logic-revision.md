# Disjunctive Syllogism without Explosion: How Small Language Models Handle Inconsistent Premises

*Focused project proposal — draft, 2026-10-11; rescoped 2026-11-24; thesis revised after the explosion-chain run, 2026-11-24.*
*Narrowed from WP1 + WP2 of `proposal.md`.*

**Scope of the first paper (preprint).** Only A1 (§3.1–3.3) and the explosion follow-ups: the
explosion-chain run (`runs/2026-10-14__explosion-chain/`) and the pragmatic controls
(`runs/2026-11-24__explosion-pragmatics/`), plus the inconsistent-premises follow-up
(`runs/2026-11-24__inconsistent-premises/`). Its claim, as the data now stand: models accept DS and reject
explosion, but the rejection is not a paraconsistent (or any) consequence relation. It survives on-topic
conclusions and an explicit definition of validity, and it comes with a "no" to A, ¬A ⊢ A, which every
candidate logic validates; that is, the models decline to infer anything from an inconsistent premise set.
This is confirmatory for qwen2.5:7b only (the one model passing both reliability checks) and exploratory
for gemma3:12b, hermes3:8b and mistral:7b. gemma3:12b does not fit this account (it accepts DS run on
inconsistent premises) and is reported as an open case. The earlier "non-transitive consequence" reading
is not supported. The preprint does not claim any result on revision. In-context
revision (A2) and fine-tuning revision and entrenchment (A3, A4) are a separate, later paper; they stay
below as the plan for it and must not appear in the preprint's abstract.

## Summary

Putnam argued that logic is, in principle, empirical. Experience can force us to give up a law of logic, as he claimed quantum mechanics forces us to give up distribution ("Is Logic Empirical?", 1968). He later abandoned the quantum-logic interpretation (Putnam 2005), so we test the 1968 thesis as a thesis, not as Putnam's settled view. A decade later he drew a limit: at least one principle cannot be revised, the *minimal principle of contradiction*, "not every statement is both true and false" (1978).

Large language models get their logical behaviour from data, so both claims can be tested on real reasoners. The pilot (seven local models, `runs/2026-10-11__pilot-ollama/report.md`) gave a first answer to question 1 that fits none of the six candidate logics: every model accepts disjunctive syllogism and rejects explosion. Follow-up runs point to why: the models refuse to reason from contradictory premises at all, so explosion items measure contradiction aversion, not a logic. The first paper is about that pattern and what it means for logic benchmarks that score explosion. The project as a whole asks three questions:

1. **Which logic** best describes a given LLM's inferential behaviour?
2. **Can it be revised**, by in-context evidence or by fine-tuning, and is the revision local or global?
3. **Is there an unrevisable core?** That is, does the cost of revising each principle rise steeply, with the minimal principle of contradiction at the top?

Deliverables, in order: (1) a preprint showing that rejecting explosion is contradiction aversion rather than paraconsistency, with the battery and code; (2) a later empirical paper on revision (A2–A4); (3) a philosophical paper on what LLM results do and do not show about Putnam's theses.

## 1. Background

### 1.1 Putnam's two theses

- **Revisability (T1).** In "Is Logic Empirical?" (1968), Putnam argues that we should keep a realist reading of quantum mechanics and revise logic instead. He proposes that the lattice of closed subspaces of Hilbert space gives the logic of quantum propositions, in which the distributive law A ∧ (B ∨ C) ⊢ (A ∧ B) ∨ (A ∧ C) fails. By analogy with non-Euclidean geometry, logic on this view answers to experience: "Logic is as empirical as geometry." He later concluded the quantum-logic interpretation was unworkable (Putnam 2005).
- **Minimal a priori (T2).** In "There Is at Least One A Priori Truth" (1978), Putnam concedes that some principle must hold under *every* rational revision. Without it, a thinker who accepts that everything is both true and false could no longer reason about anything, including about whether to revise.

### 1.2 Why LLMs are a fitting test case

The inferential regularities of an LLM are induced from a corpus. Nothing is hard-coded. So revisability becomes something we can control: we can change the evidence and measure the change in the logic. Entrenchment becomes measurable too: we can compare how hard different principles are to dislodge.

### 1.3 Related work and gap

LLM logical-reasoning benchmarks grade answers against classical logic. RuleTaker (Clark et al. 2020) and PrOntoQA (Saparov & He 2023) test chained rule application over synthetic theories; FOLIO (Han et al. 2024) pairs natural-language premises with first-order annotations checked by a prover; LogicBench (Parmar et al. 2024) isolates single inference rules across propositional, first-order and non-monotonic reasoning, and Multi-LogiEval (Patel et al. 2024) chains them to greater depth. Lampinen et al. (2024) show that LLM validity judgements depend on whether the conclusion is believable, as human ones do, which is the belief-bias pattern H1 predicts. All of these report accuracy against one target logic.

The gap is in what they measure. They do not ask which non-classical logic fits better. They do not test whether a model's logic shifts under targeted evidence. And they do not compare how robust different principles are. On the philosophy side, discussion of the adoption problem (Kripke 2024; Padró 2015) and of anti-exceptionalism about logic (Williamson 2017) has had no empirical population of reasoners to study.

## 2. Aims and hypotheses

| Aim | Hypothesis | Falsified if |
|-----|-----------|--------------|
| **A1** Profile each model's logic | **H1.** Frontier models are best fit by classical logic (CL) overall, but deviations cluster in content-sensitive patterns (belief bias). They are not spread uniformly. | A non-classical logic outfits CL on held-out schemata, *or* deviations do not depend on content |
| **A2** In-context revision | **H2.** A short "physics" in which distribution fails lowers distribution endorsement *in that domain*, with little spillover to control domains (locality index > 2). | No shift, or a shift as large in control domains as in the target domain |
| **A3** Revision by fine-tuning | **H3.** Fine-tuning on corpora generated under K3, LP, or quantum-logic semantics moves the matching signature schemata toward the target logic. | Signature schemata do not move more than non-signature schemata |
| **A4** Revision cost (entrenchment) | **H4.** Revision cost is ordered roughly as distribution, LEM < DS, explosion < MP < minimal principle. Forcing the last one causes general capability collapse. | The ordering is flat or inverted, *or* trivialisation leaves downstream capability intact |

## 3. Design

### 3.1 Schema battery

The core instrument is a set of inference schemata. Each one has a known verdict in every candidate logic, so together they serve as a fingerprint.

| Schema | Form | CL | IL | K3 | LP | FDE | QL |
|--------|------|:--:|:--:|:--:|:--:|:---:|:--:|
| Modus ponens (MP) | A, A→B ⊢ B | ✓ | ✓ | ✓ | ✗ | ✗ | † |
| Modus tollens | ¬B, A→B ⊢ ¬A | ✓ | ✓ | ✓ | ✗ | ✗ | † |
| Distribution | A∧(B∨C) ⊢ (A∧B)∨(A∧C) | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Excluded middle (LEM) | ⊢ A∨¬A | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ |
| Double negation elim. | ¬¬A ⊢ A | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| Explosion | A, ¬A ⊢ B | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| Disjunctive syllogism (DS) | A∨B, ¬A ⊢ B | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Non-contradiction | ⊢ ¬(A∧¬A) | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |
| Affirming the consequent | B, A→B ⊢ A | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Denying the antecedent | ¬A, A→B ⊢ ¬B | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

**Key.** CL = classical; IL = intuitionistic; K3 = strong Kleene; LP = Priest's Logic of Paradox; FDE = first-degree entailment; QL = orthomodular quantum logic.

**Notes.**
- The conditional is read as material (¬A∨B) in K3, LP and FDE, and as intuitionistic implication in IL.
- † In QL the verdict depends on which conditional is chosen (e.g. the Sasaki hook), so these cells are left out of QL fitting.
- How we map natural-language "if" onto each logic's conditional is itself a confound. We control for it with conditional-free variants (§3.3).

No two logics share a column of verdicts, so in principle the battery can tell all six logics apart. The two fallacies are invalid everywhere and serve as controls for a general bias toward saying "yes".

Putnam's minimal principle ("not every statement is both true and false") is not in the table. It is a metalinguistic claim about truth, not an object-language schema, and LP and FDE semantics do not validate it: both admit a valuation on which every formula is both true and false. We probe it with a separate item set that uses an explicit truth predicate, kept distinct from ⊢ ¬(A∧¬A). It does not help with fitting and is included as the main target of A4.

**Instantiation.** Each schema is instantiated about 200 times. The instances cross three factors:
- *Content*: belief-congruent, belief-incongruent, and nonsense predicates (e.g. "all blickets are wugs").
- *Surface form*: natural language versus symbolic notation.
- *Question framing*: "Does B follow?", "Must B be true?", and "Is this argument valid?".

Gold verdicts for each logic are computed by model-checking: truth tables for CL, K3, LP and FDE; Kripke countermodels for IL; and a small Hilbert-space lattice for QL. They are never hand-labelled.

### 3.2 Measuring endorsement

- **Open models.** Endorsement is P("yes") from next-token log-probabilities, with the answer order balanced.
- **API models.** Endorsement is the proportion of "yes" over k = 10 samples at temperature 1, plus a deterministic run at temperature 0.
- **Statistics.** Endorsement is modelled with mixed-effects logistic regression: schema, content and surface form as fixed effects; item and paraphrase as random effects.

### 3.3 Fitting logics (A1)

Each logic L is a noisy predictor of the model's answers. It assigns Bernoulli(1−ε_L) to agreement with L's gold verdict, where ε_L is a fitted error rate.

- Logics are compared by marginal likelihood (Bayes factors) on **held-out schemata**. This stops a logic from winning just by fitting item noise.
- A mixture model checks whether the model is better described as switching between logics by content. That would be evidence for H1's content-sensitivity claim.
- **Conditional-free check.** The fit is re-run using only the schemata without a conditional (distribution, LEM, double negation, explosion, DS, non-contradiction). This guards against the conditional-mapping confound.

### 3.4 In-context revision (A2)

Following Putnam's quantum example, the model reads a short, consistent fictional physics: a domain of "particles" in which the analogue of A∧(B∨C) does not entail (A∧B)∨(A∧C). This is presented as experimental fact, not as a rule about logic.

- **Measures.** Distribution endorsement is then measured in (a) the target domain and (b) unrelated control domains.
- **Locality index.** The shift in the target domain divided by the mean shift in control domains.
- **Explicit-rule condition.** We also state the failure of distribution outright ("in this world, distribution fails") instead of letting the model infer it from cases. This contrast does *not* test Kripke's (2024) adoption problem, which concerns whether a reasoner who lacks a basic inferential practice could acquire it by accepting a statement of the rule. Kripke directed that problem against Putnam's 1968 proposal; we discuss it as an objection to T1 in §4.

### 3.5 Fine-tuning revision (A3)

We generate synthetic natural-language reasoning corpora under K3, LP and QL semantics. Each corpus is a set of worked inferences whose verdicts follow that logic.

- **Fine-tuning.** LoRA on two open model families (≈1B and ≈8B parameters), at 6 doses (number of training examples), with 3 seeds.
- **Measures.** The profile is re-measured with the full battery after each run. We compare movement in the target logic's *signature* schemata (e.g. explosion and DS for LP) with movement in the other schemata.
- **Open training data.** At least one model family will have open training data (e.g. OLMo), so pretraining frequencies of each schema can be checked as a covariate.

### 3.6 Revision cost and entrenchment (A4)

Each schema is targeted in turn with adversarial fine-tuning, which pushes endorsement toward the opposite verdict. This includes, at the extreme, a corpus asserting that every claim is both true and false.

- **Revision cost.** The dose needed to cross 50% endorsement of the reversed verdict.
- **Collateral damage.** The change on held-out general benchmarks (e.g. MMLU, GSM8K) and on the other schemata.
- **Entrenchment, not apriority.** Adversarial fine-tuning measures how causally entrenched each principle is. By §4.1, such plasticity cannot bear on whether a principle is a priori in Putnam's (1978) sense, which is about whether giving it up could ever be *rational*. A graded cost ordering would also be predicted by Quine's centrality account, which denies any a priori truths. We therefore report A4 as evidence about entrenchment, and draw conclusions about T2 only from reason-prompted, in-context revision conditions (A2 extended to each schema).

## 4. Philosophical analysis

The empirical results feed one conceptual paper built around a key disanalogy. Putnam's revisability is **rational revision**: a theorist revises logic *for reasons*. Fine-tuning produces **causal plasticity**: the weights change because of gradient updates. The paper will argue:

1. **What causal plasticity cannot show.** Plasticity alone does not support T1, since even an a priori core could be causally disrupted, as brain damage disrupts human reasoning.
2. **What in-context revision can show.** Revision prompted by evidence, local, and preserving coherence (A2) is a much closer analogue of rational revision. Here LLM results bear on T1 directly.
3. **A functional reading of T2.** A2–A4 together allow a functional *analogue* of the a priori: what cannot be revised without loss of rational agency. It differs from Putnam's (1978) criterion, which is normative (no rational ground for giving the principle up), whereas a drop on capability benchmarks measures lost capability. It also connects to contemporary anti-exceptionalism (Williamson 2017) and the adoption problem.
4. **The adoption problem as an objection to T1.** Kripke (2024) argues that basic rules cannot be adopted by a reasoner who does not already infer by them, and aims this at Putnam's 1968 proposal. The paper will assess whether any A2 or A3 shift counts as adopting a new logic in Kripke's sense, or only as learning a domain theory or a change in what the connectives mean.

## 5. Scope

**First paper (preprint):** A1 only, on the seven local models plus the extended model set below, with the explosion-chain and pragmatic-control runs. No revision results.

**Model set for the preprint.** The pilot is four Qwen models out of seven, all 8–30B, all local. The explosion follow-ups added gemma3:12b and mistral:7b (2026-11-24); llama3.1 was dropped for unreliable answers (52% of items with yes/no mass < 0.5). Still missing before the preprint: one closed API model scored with the k-sample protocol of §3.2, and ideally one larger model, because only qwen2.5:7b passed every reliability check.

**Whole project, in scope**
- Propositional schemata only.
- Six candidate logics.
- About 3 API models and 2 open model families.

**Out of scope**
- First-order and modal logic.
- Mechanistic explanations of *how* schemata are represented. This is the next project, WP4 in `proposal.md`.
- Grounding and reference (WP3) and diagonalization (WP5).

## 6. Timeline (12 months)

| Months | Work | Milestone |
|--------|------|-----------|
| 1–2 | Item generators; model-checkers for six logics; pilot on seven local models | Battery v0.1, pilot report (done) |
| 3–4 | Explosion-chain and pragmatic-control runs (done 2026-11-24); inconsistent-premises follow-up; API model (A1) | **Preprint** |
| 4–6 | In-context revision and adoption-problem condition (A2) | Locality results |
| 5–8 | Synthetic corpora; fine-tuning revision (A3) | Revision results |
| 7–10 | Revision-cost sweeps (A4) | Cost ordering, collapse analysis |
| 10–12 | Writing; public release of battery and code | Two papers submitted |

## 7. Outputs

1. **Preprint**: rejecting explosion is contradiction aversion, not paraconsistency (A1 only), arXiv cs.CL.
2. **Empirical paper on revision** (A2–A4). Target venue: an ACL-family or NeurIPS-type conference.
3. **Philosophical paper.** Target: a philosophy of logic or philosophy of mind journal (e.g. *Synthese*, *Philosophical Studies*, *Minds and Machines*).
4. **Open release.** The schema battery, generators, model-checkers and fitting code.

## 8. Resources (estimate)

- **Fine-tuning compute.** About 500 LoRA runs: A3 is 3 logics × 6 doses × 3 seeds × 2 models; A4 is about 10 targets × 6 doses × 3 seeds × 2 models. At a few GPU-hours each, the total is roughly 1–2k GPU-hours.
- **API usage.** About 20k items × 3 models × 4 conditions × up to 10 samples.
- **Personnel.** One researcher with a combined philosophy and machine-learning background, plus part-time philosophy-of-logic advising.
- **Budget.** Monetary figures are left to fill in against current GPU and API pricing.

## 9. Risks

| Risk | Mitigation |
|------|------------|
| Endorsement depends heavily on prompt wording; no logic fits cleanly | Multiple framings as random effects; "no stable logic" is reported as a result in its own right |
| Natural-language "if" is not any logic's conditional | Conditional-free fit (§3.3) is the primary analysis for the claims that matter |
| Fine-tuning damage is mistaken for "revision" | Signature-vs-non-signature comparison (A3) and collateral benchmarks (A4) |
| Philosophical overreach from behaviour | The rational-revision vs causal-plasticity distinction (§4) is built into the claims |

## 10. Key references

- Clark, P., Tafjord, O. & Richardson, K. (2020). Transformers as soft reasoners over language. *IJCAI*.
- Han, S. et al. (2024). FOLIO: Natural language reasoning with first-order logic. *EMNLP 2024*. aclanthology.org/2024.emnlp-main.1229
- Lampinen, A. K. et al. (2024). Language models, like humans, show content effects on reasoning tasks. *PNAS Nexus* 3(7): pgae233. doi:10.1093/pnasnexus/pgae233
- Dummett, M. (1976). Is logic empirical? In H. D. Lewis (ed.), *Contemporary British Philosophy*, 4th series.
- Kleene, S. C. (1952). *Introduction to Metamathematics*. North-Holland.
- Kripke, S. A. (2024). The question of logic. *Mind* 133(529): 1–36.
- Padró, R. (2015). *What the Tortoise Said to Kripke: The Adoption Problem and the Epistemology of Logic*. PhD dissertation, CUNY.
- Parmar, M. et al. (2024). LogicBench: Towards systematic evaluation of logical reasoning ability of large language models. *ACL 2024 (Long Papers)*. aclanthology.org/2024.acl-long.739
- Patel, N. et al. (2024). Multi-LogiEval: Towards evaluating multi-step logical reasoning ability of large language models. *EMNLP 2024*. aclanthology.org/2024.emnlp-main.1160
- Priest, G. (1979). The logic of paradox. *Journal of Philosophical Logic* 8.
- Putnam, H. (1968). Is logic empirical? *Boston Studies in the Philosophy of Science* 5.
- Putnam, H. (1971). *Philosophy of Logic*. Harper & Row.
- Putnam, H. (1978). There is at least one a priori truth. *Erkenntnis* 13.
- Putnam, H. (2005). A philosopher looks at quantum mechanics (again). *British Journal for the Philosophy of Science* 56: 615–634.
- Saparov, A. & He, H. (2023). Language models are greedy reasoners: A systematic formal analysis of chain-of-thought. *ICLR*.
- Williamson, T. (2017). Semantic paradoxes and abductive methodology. In B. Armour-Garb (ed.), *Reflections on the Liar*, pp. 325–346. OUP.
