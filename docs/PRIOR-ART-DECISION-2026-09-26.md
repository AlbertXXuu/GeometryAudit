# Current candidate retired after prior-art review

Decision date: **2026-09-26**. Candidate: `CAND-GEO-01`. Disposition: **KILL under its current definition**.

The candidate sought to combine foundation-model confidence, geometric evidence and graph consistency to identify unreliable relative poses and control correction. We no longer treat that capability chain as sufficient novelty for an independent flagship contribution. The earlier prior-art review was incomplete. This is a portfolio decision about our proposed contribution, not an experimental finding that geometry reliability is solved.

## Primary-source check

Reviewed [GeoCond, arXiv:2609.18465v1](https://arxiv.org/abs/2609.18465v1), submitted 16 September 2026, and its [full text](https://arxiv.org/html/2609.18465v1), on 26 September 2026. The following are author-reported results; we have not reproduced them.

- Sections 3.3–3.6 combine backbone-derived geometry and native confidence in a pose-uncertainty head, support independent-edge cycle supervision, and use reliability for gated refinement and graph weighting/pruning.
- Table 3 reports outdoor AUSE 0.32 → 0.20 for a head trained on mixed indoor/outdoor data and tested on held-out scenes. This headline is not the separate zero-shot experiment. Its outdoor gated AUC@30 is 58.4, above uniform BA at 38.4 but below unrefined feed-forward poses at 60.3.
- Table 6 shows uneven backbone transfer. For MapAnything, native AUSE is 0.209 versus 0.496 zero-shot, 0.240 supervised and 0.251 cycle-distilled; cycle fusion reaches 0.147 but requires independent-edge graphs at inference.
- Conditioning features come from model predictions. Cycles supply consistency signals, not independent ground truth or guarantees of correctness. Section 5 identifies domain-dependent calibration and setting-dependent refinement benefit.

## Consequence for this repository

The overlap removes the novelty rationale for our current candidate. Differences in image-matching evidence, audit presentation or model coverage would need a specific, independently motivated contribution and direct comparison; their existence alone does not justify proceeding. GeoCond's limitations do not automatically establish such a contribution for us.

The [next protocol draft](PROTOCOL-NEXT.md) and [scene register](SCENE-CANDIDATES.md) are closed preparation records. No new failure-space audit, scene admission, model run or implementation follows from them. No replacement candidate or mainline is selected by this decision.

GeometryAudit remains a public record of the Motorcycle and TUM engineering runs, their preserved protocols and CPU-checkable pose calculations. Existing code, raw-evidence provenance and reported limitations remain useful reproducibility assets. The frozen protocols, archived sources, reports and records are unchanged. Closing the candidate neither invalidates those measurements nor upgrades them into reliability or repair results.

Any future 3D direction starts with a distinct capability target, a primary-source comparison and a new bounded decision. It is not a continuation authorized by this retired draft.
