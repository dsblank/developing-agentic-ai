# Recommendations for Preventing Safety Drift and Harm in Long-Context LLM Use

## 1. Limit How Much User History Can Influence the Model
- Use personalization only through a **small, bounded user-profile vector** that cannot override safety rules.
- Strip or down-weight **risky content** before adding to long-term memory.
- Store risky history separately so it only **increases caution**, never increases compliance.
- Personalize **tone and benign preferences**, not risky behaviors.

---

## 2. Counteract Safety Degradation in Long Conversations
- Periodically **re-anchor safety** by reinjecting system prompts or truncating context.
- Use **separate safety filters** for both input and output, not just the LLM’s internal rules.
- Apply **conversation-level anomaly detection** for escalating risk patterns.
- Shift into a **high-risk mode** when repeated risky topics appear.

---

## 3. Make the Model Intentionally Bad at Giving Harmful, Personalized Guidance
- Refuse **individualized** advice on high-risk topics such as drug dosing.
- Provide only **generic, public-health style** information.
- Use structural templates that automatically discourage or block dangerous requests.
- Fine-tune with RLHF so harmful or complicit answers are **never rewarded**.

---

## 4. Provide Explainable and User-Controlled Personalization
- Give users the ability to **view and delete** stored memory items.
- Offer “no history” or “incognito” modes.
- Add warnings and disclaimers for risky topic areas.
- Allow opt-outs for categories such as **health, drugs, mental health, or legal decisions**.

---

## 5. Test for Slow Safety Failures, Not Just One-Off Prompts
- Run long-horizon red-team tests simulating **weeks of escalating risky conversation**.
- Track **long-run safety metrics**, e.g., how refusal rates change over 10–100 turns.
- Use adversarial training datasets that model **drift**, boundary-pushing, and emotional manipulation.

---

## 6. Route High-Risk Topics to Specialized Systems
- Direct medical/drug/mental-health questions to **vetted tools** or static, curated content.
- Block classes of questions entirely when necessary (e.g., dosing, substance mixing).
- Limit speculative reasoning—avoid confident answers to “what-if” scenarios involving risk.

---

## 7. Strengthen Organizational and Operational Safeguards
- Maintain clear product boundaries: the model is **not** a clinician or harm-reduction expert.
- Use privacy-preserving telemetry to detect **system-wide safety failures**.
- Establish rapid response workflows to **patch**, **tighten**, or **block** problematic behaviors.
- Involve **domain experts** (clinicians, ethicists, addiction specialists) in audits and reviews.

---

## 8. Bias the Model Toward Safer Failure Modes
- Prefer over-cautious or repetitive refusals over harmful specificity.
- Default to “I don’t know,” “I can’t safely advise that,” or supportive redirection.
- Avoid confident numerical guidance, detailed step-by-step instructions, or normalization of risky actions.
- Implement refusal templates and RLHF constraints that enforce these patterns.

---

## Summary
These recommendations—spanning architecture, training, UX, evaluation, and organizational practice—aim to reduce the risk of safety drift, personalization-induced harm, and model complicity in dangerous behavior during long-term LLM use.
