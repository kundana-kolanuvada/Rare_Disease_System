Rare disease diagnostic system UI: 
Imagine you open a website or web app called Rarity.

Home screen
The first screen is very clean and calm, with a medical feel (white background, soft blue accents).
At the top, there is:
    • A simple title: “Rarity – Rare Disease Diagnostic Assistant”
    • A one-line subtitle: “Helps clinicians and patients explore possible rare diseases. Not a substitute for medical diagnosis.”
In the center, there is a big card with a short wizard-style form and a button:
    • A large button: “Start a New Case”
    • Under it, a smaller line: “You will enter symptoms, demographics, and history step by step.”
Below that, a very small disclaimer in grey:
“For educational and decision-support use only. Not a diagnostic device.”

Step 1: Patient basics
After clicking “Start a New Case”, the screen becomes a multi-step form with a progress bar at the top:
Step 1 of 4 – Patient Basics
The form is centered and narrow (so it feels simple, not overwhelming).
Fields you see:
    • Age: a numeric box (e.g., 23)
    • Sex: radio buttons – Male, Female, Intersex, Prefer not to say
    • Ethnicity (optional): a dropdown with examples (South Asian, East Asian, African, European, etc.)
    • Country/Region: dropdown (for epidemiology context)
At the bottom, there are two buttons aligned to the right:
    • Grey “Back” (disabled on this first step)
    • Blue “Next”

Step 2: Symptoms description
The progress bar now says:
Step 2 of 4 – Symptoms
The left half of the screen shows a large text box with the label:
“Describe the symptoms in your own words (as detailed as possible).”
The user sees a prompt above the box such as:
“Example: ‘23‑year‑old woman with loose joints, frequent dislocations, easily bruised skin, slow wound healing, and similar problems in her father.’”
Below the text box, there is a list of chips that appear as the system parses the text:
    • A small section titled: “Recognized symptoms”
    • Under it, pill-shaped tags like:
        ◦ Joint hypermobility
        ◦ Easy bruising
        ◦ Skin fragility
Next to each pill tag there is a small trash icon (to remove it) and sometimes a drop-down arrow to set severity (e.g., Mild, Moderate, Severe).
Below the chips, there is a subtle line:
“If something is missing, add it as free text above; the system will update this list.”
Bottom-right again has “Back” and “Next” buttons.

Step 3: Family and history
Now the header says:
Step 3 of 4 – Family & History
The form includes:
    • Family history of similar symptoms?
        ◦ Radio buttons: Yes, No, Unknown
        ◦ If Yes, a text area appears: “Describe who and what symptoms.”
    • Onset of symptoms: dropdown
        ◦ Since birth, Early childhood, Teenage, Adulthood, Recent (last 6 months)
    • Previous diagnoses or labels (if any): text field
        ◦ Example hint: “e.g., ‘ruled out lupus’, ‘diagnosed with hypermobility spectrum disorder’”
    • Previous tests done: multi-line text field
        ◦ Example: “MRI normal, blood tests normal, genetic panel negative for X, Y”
At the side (or just below on mobile), there is a small info box:
“This information helps adjust likelihoods based on inheritance patterns and disease natural history.”
Buttons at the bottom: “Back”, “Next”.

Step 4: Review and run analysis
Header:
Step 4 of 4 – Review & Analyze
You see a summary card with all entered data in a neat layout:
    • Patient basics: Age, sex, ethnicity, region
    • Symptoms (normalized): a bullet list of standardized terms
    • Family history: short summary
    • Previous tests: brief list
Each section has a small “Edit” link on the right, which jumps back to that step.
At the bottom of the summary card, there is a centered button:
    • Large blue button: “Run Rare Disease Analysis”
    • Under it: “Takes about 3–5 seconds. We will generate a ranked list of possible rare diseases and suggested next steps.”
When clicked, the button turns into a spinner with the text: “Analyzing case…” and a progress animation appears.

Results screen: ranked rare disease candidates
After a short wait, the screen scrolls to a results section.
At the very top, a line in bold:
“This is not a diagnosis. Use as input for discussion with a healthcare professional.”
Then a ranked list of disease cards, one below another.
Each disease card looks like this:
Card layout for each disease
    • Left side (top row):
        ◦ Disease name in bold, e.g.,
“Ehlers–Danlos Syndrome, Classical Type (ORPHA: 234)”
        ◦ Under it, a small tag: Genetic connective tissue disorder
    • Right side (top row):
        ◦ A big percentage badge:
Match score: 94%
        ◦ Below it, a smaller line: Risk level: High priority for evaluation
Below the top row, the card is split into sections with clear headings:
    1. Why this matches your case
        ◦ Short bullet points written in simple language, for example:
            ▪ “You reported joint hypermobility, which is a core feature of this condition.”
            ▪ “Easy bruising and fragile skin are common in many classical EDS cases.”
            ▪ “Family history suggests an inherited pattern consistent with autosomal dominant diseases.”
    2. Key typical features of this disease
        ◦ Bullet list summarizing what the disease usually looks like (from Orphanet):
            ▪ “Skin hyperextensibility”
            ▪ “Atrophic scars”
            ▪ “Joint dislocations”
    3. How your case compares
        ◦ Two columns visually described in text:
            ▪ Column 1: “Typical disease features”
            ▪ Column 2: “Present in this case?” (Yes/No/Unknown)
        ◦ Example (described, not shown as a real table):
            ▪ “Joint hypermobility – Present”
            ▪ “Skin hyperextensibility – Present (based on ‘skin tears easily’)”
            ▪ “Atrophic scars – Unknown (not mentioned)”
    4. Suggested next steps (for clinicians)
        ◦ A short numbered list:
            ▪ “Consider referral to a clinical geneticist.”
            ▪ “Consider genetic testing of COL1A1, COL1A2 if accessible.”
            ▪ “Consider dermatology evaluation for skin fragility.”
    5. Evidence and references
        ◦ A few bullet lines:
            ▪ “Approximate prevalence: 1 in 20,000.”
            ▪ “Typical onset: childhood to early adulthood.”
            ▪ “Number of similar case reports found: 12 (last 10 years).”
        ◦ Each bullet would, in implementation, link to a paper or Orphanet entry.
At the bottom right of each card, there is a small “Mark as explored / Save” button and maybe a “Not relevant” button.

Side panel: filters and controls
On the right (or as a collapsible pane on mobile), there is a slim filter/control panel:
    • Filters:
        ◦ Checkbox: Show only high-priority candidates
        ◦ Slider or dropdown: Minimum match score (e.g., 60–100%)
        ◦ Toggle: Show only diseases with genetic tests available
    • Display options:
        ◦ Radio buttons:
            ▪ Compact view (just names and scores)
            ▪ Detailed view (full explanations and recommendations)
    • Export options:
        ◦ Buttons:
            ▪ Download PDF summary
            ▪ Copy summary for EMR/notes

Case summary view
There is also a “Case Summary” tab near the top of the results section.
When opened, it shows:
    • A concise one-page style summary:
        ◦ Patient details
        ◦ Recognized symptoms (standard names)
        ◦ Top 3 candidate diseases with match scores
        ◦ One paragraph of explanation per disease
        ◦ One short “Next steps” section for clinicians
This view is designed to be printable or shareable as a PDF.

Feedback interaction (learning)
At the bottom of the page, a simple section:
“Did any of these suggestions turn out to be correct (after tests/doctor visits)?”
    • Radio buttons:
        ◦ Yes, one of them was confirmed
        ◦ No, none were correct
        ◦ Not sure / still in progress
If Yes is selected, a dropdown appears:
    • “Which one?” → list of the diseases shown
Optional text box:
“Anything you’d like to share about the final diagnosis or journey?”
This allows the system (later) to learn from outcomes and refine scoring.

Navigation and overall feel
At the top of every screen (thin header bar), there are:
    • A small logo: “Rarity”
    • Links:
        ◦ New Case
        ◦ My Saved Cases
        ◦ About & Limitations
        ◦ Help
The entire UI is:
    • Very text-driven, with clear headings and short paragraphs.
    • Uses simple bullet points instead of crowded tables.
    • Avoids dense medical jargon when possible, but keeps technical terms available for clinicians.
    • Clearly separates:
        ◦ “What the patient said”
        ◦ “How the system interpreted it”
        ◦ “What diseases it suggests”
        ◦ “Why it suggests them”
        ◦ “What to do next”
If you read it line by line, you can reconstruct exactly what the screen looks like and what each section is doing, without needing any pictures.
If you want next, a concrete textual mockup for one full “case result” page (like a wireframe written only in text) can be created so you can almost copy-paste it into a design doc or README.
