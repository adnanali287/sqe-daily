# SQE Daily design plan

Visual thesis: a contemporary legal daily, where the typographic confidence of a newspaper meets the quiet clarity of a good exam paper.

## Content order
1. Masthead: SQE Daily, independent SQE1 practice, email navigation.
2. Short promise: one free original question a day, worked answer and source; live countdown to FLK1.
3. Today's question: date, subject, scenario, stem and five generous answer buttons. A slim desktop margin carries question metadata and the daily email invitation.
4. After answering: unmistakable result, correct answer, key rule, complete worked reasoning and linked primary authority. No answer-changing or score anxiety.
5. Daily email, three concise steps, original and primary-source checking statement, understated sponsor note, disclaimer.

## Interaction
One click (or keyboard Enter/Space) commits an answer and reveals the reasoning in place. Feedback uses words and symbols as well as colour. A short reveal motion never delays reading. Email submission posts to an explicitly documented placeholder and confirms this is a preview; it never pretends to have subscribed someone.

## Tokens
- Type: self-hosted Newsreader for the masthead and editorial display, self-hosted DM Sans for body and controls. Serif fallback Georgia; sans fallback Arial.
- Colour: paper #f9faf7, ink #142f2b, mint #e2eee5, accent red #b63d2c, muted #53645d, rules #c3cec5. Correct #235c42; incorrect #a13224.
- Spacing: 4px base; 8, 12, 16, 24, 32, 48, 64, 80. Max content width 1240px; mobile gutters 20px.
- Shape: square editorial bands; answer controls 4px corners. No floating section cards.
- Motion: 180ms opacity and 6px translation, 120ms control states; disabled under prefers-reduced-motion.
- Visual assets: original SVG daily mark (sun over an open page), favicon and social sharing artwork. No third-party logos or decorative hero imagery.

## Critique and revision before implementation
An editorial theme can lapse into a generic beige magazine, and a huge slogan can push the actual question too far down. Revised direction: cool near-white and green paper, dark green ink plus one red accent, a compact introductory band, and a visible real question in the first desktop viewport. Avoid badges, pills, cards, fake testimonials and illustrative legal scales. Use the question number as the only large margin device. Keep the brand name prominent, and use the supplied question text verbatim without an answer-revealing title before selection.

## Visual QA
Two screenshot review and refinement loops are recorded below after implementation.

### Round 1
Reviewed full-page desktop 1440px and mobile 390px screenshots before and after an incorrect answer. Weaknesses: mobile display wrapped to three lines and delayed the question; 12px option text was too small; explanation grouped the incorrect options into one dense paragraph; desktop headline phrases touched. Revisions: 45px mobile display, 14px option text and explanation, 15px scenario, separate paragraph for each explanation line, and a small inline headline gap. Also increased mobile form notes for readability.

### Round 2
Reviewed new full-page 1440px and 390px screenshots before answering and after the correct answer. Typography and explanation spacing now work well. Remaining weakness: answer boundaries were too faint for confident interaction; strengthened their colour to meet 3:1 contrast against the panel. Added a compact 320px treatment for the masthead and stacked email controls. Removed redundant font preloads that caused browser warnings. Final screenshots are captured after these fixes.
