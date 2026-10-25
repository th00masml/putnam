# Is Logic Learned? Putnam's Philosophy of Logic and Large Language Models

*Research proposal — draft, 2026-10-11*

## Abstract

Hilary Putnam spent fifty years on one cluster of questions: is logic revisable on empirical grounds? Can theory, however rich, fix what its words refer to? When does a physical system actually compute what we say it computes? And can any mechanical procedure be a universal inductive reasoner? For most of that time these were thought experiments. Large language models (LLMs) now make them experiments. An LLM is a system whose logical competence comes, as far as we can tell, entirely from exposure to data. It is trained only on text, with no other link to the world. And its "implementation" of an inference rule is an open empirical question for mechanistic interpretability.

This project takes five of Putnam's theses about logic and turns each into a falsifiable research question about LLMs. The aim runs both ways. Putnam's arguments give LLM research sharper concepts than the vague "do LLMs reason?". In return, LLMs give philosophy of logic its first population of non-human reasoners whose logic can be measured, perturbed and revised under controlled conditions.

## 1. Background and motivation

### 1.1 Putnam's philosophy of logic in brief

Five Putnam theses frame the project. They come from different decades, and Putnam himself later qualified several of them. That tension is useful rather than a problem.

| # | Thesis | Key texts |
|---|--------|-----------|
| T1 | **Logic is (in principle) empirical.** Our choice of logic can be revised in response to experience, as quantum mechanics arguably requires giving up the distributive law. | "Three-Valued Logic" (1957); "Is Logic Empirical?" (1968) |
| T2 | **There is a minimal a priori core.** At least one logical principle survives every revision: the *minimal principle of contradiction*, "not every statement is both true and false." | "There Is at Least One A Priori Truth" (1978) |
| T3 | **Theory does not fix reference.** By the model-theoretic argument, any consistent theory, even one including every operational constraint, has unintended models. Adding more constraints is "just more theory." | "Models and Reality" (1980); *Reason, Truth and History* (1981) |
| T4 | **Implementation is cheap.** Every ordinary open physical system can be described as realizing every finite automaton, so "realizing a computation" cannot by itself ground mentality. | *Representation and Reality* (1988), Appendix |
| T5 | **No computable inductive method is universal.** A diagonal argument shows that, for any computable confirmation function, there is an environment where it never learns a true hypothesis that some other method would. | "'Degree of Confirmation' and Inductive Logic" (1963); "Trial and Error Predicates" (1965) |

Putnam is also, unusually, a founder of automated reasoning. The Davis–Putnam procedure (1960) is the ancestor of DPLL and of every modern SAT solver. A project that asks how neural networks relate to symbolic logic stands, quite literally, on his algorithm.

### 1.2 Why LLMs change the situation

- **Logic acquired from data.** No logic module is written into an LLM's architecture. Any inferential regularity it shows was induced from a corpus. So T1 becomes a design variable: we can change the data and watch whether the logic changes.
- **A purely textual reasoner.** An LLM is close to the agent Putnam's model-theoretic argument imagines: something whose only constraints on interpretation are more sentences. The symbol-grounding debate about LLMs (Bender & Koller 2020; Piantadosi & Hill 2022; Mollo & Millière 2023) restates T3, mostly without citing it.
- **Implementation is now an empirical question.** Mechanistic interpretability and causal abstraction (Geiger et al. 2021) offer operational criteria for when a network implements an algorithm. These criteria are exactly what Putnam's triviality argument (T4) says are needed, and what Chalmers (1996) tried to supply.
- **Universal predictors meet diagonalization.** LLMs are often described as approximate universal sequence predictors. T5 places a precise limit on any such claim, and that limit can be shown concretely against a given model.

### 1.3 Gap

Empirical work on LLM reasoning (e.g. Clark et al. 2020; Saparov & He 2023; Zhang et al. 2023; Berglund et al. 2023) mostly asks *how well* models follow classical logic. It rarely asks *which* logic a model's behaviour best fits, whether that logic can be revised, or what it would take for a model to *have* a logic at all. Philosophical work on LLMs, meanwhile, focuses on meaning and understanding and rarely engages with the philosophy of logic. This project sits in that gap.

## 2. Research questions

- **RQ1 (Empirical logic).** Which logic best fits an LLM's inferential behaviour, and can that logic be revised by data or context the way Putnam said ours could?
- **RQ2 (A priori core).** Is there a minimal set of principles that resists all such revision, and does it line up with Putnam's minimal principle of contradiction?
- **RQ3 (Reference).** Does anything in a text-only model's behaviour or internal states rule out the unintended interpretations that Pucontintnam's model-theoretic argument guarantees?
- **RQ4 (Implementation).** Under what non-trivial criteria does a transformer *implement* an inference rule or a proof procedure such as DPLL, as opposed to merely being describable as doing so?
- **RQ5 (Induction).** Can Putnam's diagonal argument be made concrete against actual LLMs, and what does it show about their claimed generality as inductive learners?

## 3. Work packages

### WP1 — Is logic empirical *for an LLM*? (T1)

**Idea.** Treat a model's logic as a measurable profile, not a yes/no question.

**Method.**
1. Build a **schema battery**: a set of inference schemata, each instantiated across many content domains with lexical surface varied. It includes modus ponens, modus tollens, contraposition, distribution (∧ over ∨ and ∨ over ∧), excluded middle, double-negation elimination, explosion, and disjunctive syllogism. Each item has a valid form and matched invalid controls (affirming the consequent and similar).
2. For each model, estimate the **endorsement profile**: the probability that it accepts each schema. Then fit candidate consequence relations to it: classical, intuitionistic, strong Kleene K3, LP, FDE, and an orthomodular (quantum) lattice logic. Model selection uses held-out schemata.
3. **Revision experiments.** (a) *In context*: give the model a short "physics" in which distribution fails, as in Putnam's quantum-logic example, and check whether its distributive-law endorsement shifts locally or globally. (b) *Fine-tuning*: train small open models on synthetic corpora generated under a non-classical semantics. Measure which schemata move and which do not.
4. Relate the results to the *adoption problem* (Kripke, as reconstructed by Padró 2015). If a model must already reason by modus ponens to take in a rule stated in context, then in-context "adoption" of a basic logical rule should fail in a predictable way.

**Output.** An open benchmark of logic profiles, and a paper on whether, and how locally, LLM logic is revisable.

### WP2 — The minimal a priori (T2)

**Idea.** Putnam (1978) retreated from full revisability to a single unrevisable principle. Test whether neural reasoners have a comparable fixed core.

**Method.**
1. Run adversarial revision, using fine-tuning and long-context persuasion, aimed at each schema in turn, including the minimal principle of contradiction itself. The target is getting the model to endorse that *every* statement is both true and false.
2. Measure **revision cost**: the data or optimisation pressure needed to flip each principle, and the collateral damage to unrelated capabilities.
3. Ask whether a model forced to accept "everything is true and false" stays a coherent reasoner at all, which is Putnam's own argument. Look for this collapse empirically as degradation in downstream task performance.

**Hypothesis.** Revision cost will be strongly non-uniform. Distribution and excluded middle will be cheap to revise. Minimal non-contradiction will be expensive, and revising it will cause widespread capability collapse. That pattern would be a functional analogue of Putnam's a priori core.

### WP3 — The model-theoretic argument and vector grounding (T3)

**Idea.** Putnam's argument predicts that a purely textual theory cannot distinguish intended from permuted interpretations. LLMs let us check what, if anything, breaks that symmetry.

**Method.**
1. **Permutation tests.** Build permuted interpretations of a domain vocabulary: systematic swaps that preserve all inferential relations in a toy theory, such as cat↔cherry style permutations over a closed domain. Ask whether model behaviour or internal representations prefer the intended interpretation. Text-only behaviour should not prefer it, by Putnam's argument.
2. **Constraint injection.** Add constraints step by step: more text, then multimodal (vision) grounding, then interactive or tool feedback. Test which kinds of constraint break the symmetry. This is the empirical version of the "just more theory" reply, and it tests whether causal or perceptual links are different in kind, as Lewis (1984) argued with "reference magnetism."
3. **Representational alignment.** Measure how closely model concept spaces match each other and match perceptual embeddings. High alignment among text-only models, together with permutation invariance, would be the signature of Putnam-style indeterminacy.

**Output.** A paper connecting the model-theoretic argument to the vector grounding problem, with experimental criteria for when grounding is achieved.

### WP4 — When does a network implement logic? (T4)

**Idea.** Putnam's triviality argument says that without constraints, any system implements any automaton. Causal abstraction gives a concrete candidate set of constraints.

**Method.**
1. Train small transformers on propositional entailment and on SAT instances, with NeuroSAT-style tasks as reference (Selsam et al. 2019).
2. Write down candidate high-level algorithms: truth-table evaluation, resolution, Davis–Putnam / DPLL with unit propagation, and heuristic shortcuts.
3. Use interchange interventions to test which algorithm, if any, is a faithful causal abstraction of the network.
4. **Triviality check.** Show that a naive mapping-based criterion of "implementation" would also certify random networks or unrelated systems, as Putnam predicted. Then show which extra constraints, such as counterfactual and interventional robustness and Chalmers' combinatorial state structure, block this.

**Hypothesis.** Networks that generalise out of distribution will be well abstracted by propagation-style algorithms close to Davis–Putnam. Networks that only fit the training distribution will match no clean algorithm. That would be a fitting result, given that Putnam co-invented the procedure.

### WP5 — Diagonalizing the inductive machine (T5)

**Idea.** Putnam (1963) proved that every computable inductive method has a blind spot. Build that blind spot for real models.

**Method.**
1. For an open model with deterministic decoding, build Putnam-style **diagonal sequences**: binary or symbolic environments in which each next element is chosen as the opposite of what the model most expects. The resulting environment is computable, and a simple rival method learns it at once, yet the model never converges.
2. Look at softer versions: sequences generated by simple rules that lie just outside the model's inductive bias, as in "learning in the limit" (Gold 1967; Putnam 1965).
3. Compare with in-context learning curves on ordinary rule-generated sequences. The question is how close real models come to the idealised Solomonoff predictor that diagonalization rules out.

**Output.** A short technical paper giving a concrete, reproducible instance of Putnam's theorem against modern LLMs, plus a discussion of what "general" inductive competence can mean.

## 4. Methodology and resources

- **Models.** A mix of (a) frontier models via API for behavioural profiling in WP1, WP2 and WP3, and (b) open-weight models from 1B to 70B parameters for fine-tuning, interpretability and deterministic diagonalization in WP1, WP2, WP4 and WP5.
- **Data.** Synthetic, programmatically generated items with gold labels from model checkers for each candidate logic. Lexical and domain variation is controlled to separate form from content.
- **Analysis.** Bayesian model comparison over consequence relations (WP1); dose-response curves for revision cost (WP2); representational similarity analysis and permutation tests (WP3); interchange-intervention accuracy (WP4); convergence diagnostics (WP5).
- **Philosophical method.** Each empirical result feeds back into a conceptual paper asking which reading of Putnam it supports or undermines. Putnam changed his mind often, so the project will track his early and late positions separately.
- **Compute.** Modest. The most expensive part is fine-tuning open models up to about 13B parameters in WP1 and WP2.

## 5. Timeline (24 months)

| Months | Activity |
|--------|----------|
| 1–4 | Literature synthesis; schema battery and generators; model-checker gold labels |
| 4–9 | WP1 profiling and in-context revision; WP5 diagonal construction (fast win) |
| 8–14 | WP1 and WP2 fine-tuning revision experiments; WP4 toy-model training |
| 12–18 | WP4 causal abstraction analysis; WP3 permutation and grounding experiments |
| 18–24 | Integration; philosophical synthesis monograph or article; public release of benchmark and code |

## 6. Expected contributions

1. **Philosophy of logic.** The first controlled tests of logical revisability and of an a priori core in a class of real reasoners.
2. **Philosophy of mind and language.** An experimental route into Putnam's model-theoretic argument, and a criterion for "grounding" that is more than "just more theory."
3. **AI and interpretability.** A benchmark of logic *profiles* rather than accuracy, a principled answer to triviality worries about "the model implements X," and a concrete demonstration of the limits of inductive generality.
4. **History of ideas.** A reassessment of Putnam as a single figure joining philosophy of logic, philosophy of mind and computer science, roles usually studied separately.

## 7. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Endorsement profiles are noisy or depend on the prompt, so no logic fits | Report fit uncertainty; use many surface variants; treat "no stable logic" as a substantive finding |
| Frontier models are closed, which limits WP4 and WP5 | Run those WPs on open-weight models; use frontier models only for behaviour |
| Philosophical conclusions overreach from behaviour | State explicitly which Putnam thesis each experiment bears on and which it does not; get philosophers to review every paper |
| Permutation experiments are hard to build without triviality | Start with closed toy domains, which make the permutations exact, before natural vocabulary |

## 8. Key references

> Citations are from memory and should be checked against the originals before submission.

**Putnam**
- Putnam, H. (1957). Three-valued logic. *Philosophical Studies* 8(5).
- Davis, M. & Putnam, H. (1960). A computing procedure for quantification theory. *Journal of the ACM* 7(3).
- Putnam, H. (1960). Minds and machines. In S. Hook (ed.), *Dimensions of Mind*.
- Putnam, H. (1963). "Degree of confirmation" and inductive logic. In P. A. Schilpp (ed.), *The Philosophy of Rudolf Carnap*.
- Putnam, H. (1965). Trial and error predicates and the solution to a problem of Mostowski. *Journal of Symbolic Logic* 30(1).
- Putnam, H. (1967). Mathematics without foundations. *Journal of Philosophy* 64(1).
- Putnam, H. (1968). Is logic empirical? *Boston Studies in the Philosophy of Science* 5. (Reprinted as "The logic of quantum mechanics.")
- Putnam, H. (1971). *Philosophy of Logic*. Harper & Row.
- Putnam, H. (1975). The meaning of "meaning." *Minnesota Studies in the Philosophy of Science* 7.
- Putnam, H. (1978). There is at least one a priori truth. *Erkenntnis* 13.
- Putnam, H. (1980). Models and reality. *Journal of Symbolic Logic* 45(3).
- Putnam, H. (1981). *Reason, Truth and History*. Cambridge University Press.
- Putnam, H. (1988). *Representation and Reality*. MIT Press.

**Philosophy**
- Button, T. (2013). *The Limits of Realism*. Oxford University Press.
- Chalmers, D. (1996). Does a rock implement every finite-state automaton? *Synthese* 108.
- Dummett, M. (1976). Is logic empirical? In H. D. Lewis (ed.), *Contemporary British Philosophy*, 4th series.
- Lewis, D. (1984). Putnam's paradox. *Australasian Journal of Philosophy* 62(3).
- Padró, R. (2015). *What the Tortoise Said to Kripke: The Adoption Problem and the Epistemology of Logic*. PhD dissertation, CUNY.

**AI and machine learning**
- Bender, E. & Koller, A. (2020). Climbing towards NLU: On meaning, form, and understanding in the age of data. *ACL*.
- Berglund, L. et al. (2024). The reversal curse: LLMs trained on "A is B" fail to learn "B is A." *ICLR*.
- Clark, P., Tafjord, O. & Richardson, K. (2020). Transformers as soft reasoners over language. *IJCAI*.
- Geiger, A., Lu, H., Icard, T. & Potts, C. (2021). Causal abstractions of neural networks. *NeurIPS*.
- Gold, E. M. (1967). Language identification in the limit. *Information and Control* 10(5).
- Mollo, D. C. & Millière, R. (2023). The vector grounding problem. arXiv.
- Piantadosi, S. & Hill, F. (2022). Meaning without reference in large language models. arXiv.
- Saparov, A. & He, H. (2023). Language models are greedy reasoners. *ICLR*.
- Selsam, D. et al. (2019). Learning a SAT solver from single-bit supervision. *ICLR*.
- Zhang, H. et al. (2023). On the paradox of learning to reason from data. *IJCAI*.
