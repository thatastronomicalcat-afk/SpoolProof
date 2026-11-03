# GenHacks submission draft
## Title
SpoolProof — know the cost before the first layer
## Track
Open (software utility; does not claim to operate hardware).
## Inspiration
A student maker can count filament and still miss labor, failed attempts, and machine time. SpoolProof makes those assumptions visible before quoting a print job.
## What it does
A local Python command-line tool accepts slicer estimates and rates, calculates an itemized cost and margin-based price, estimates filament including retries, flags expected spool shortages, and checks dimensions against a configurable build envelope. Optional ASCII/binary STL inspection measures extents with explicit units.
## How it was built
Python standard library; JSON input/output; isolated pure calculation functions and unittest tests. No network services, paid APIs, accounts, or personal data required.
## Validation
Eight automated tests passed covering known costs, retry expectations, stock warnings, axis permutations, invalid numeric input, labor accounting, ASCII/binary STL and unknown units. No real-user study or physical printer test has been performed. All example job data is synthetic.
## Limitations
Estimates depend on input accuracy. Envelope checks do not guarantee a printable mesh. Labor and failures follow explicitly documented assumptions.
## AI disclosure
ChatGPT/Codex generated implementation, documentation, test cases, and demonstration assets on November 2, 2026 in response to the entrant's brief. The entrant must inspect, run, understand, and accurately describe this assistance; do not claim unaided authorship.
## Remaining submission steps
Entrant reviews and runs code; confirms eligibility/consent and free participation; uploads source to a public repository; uploads demo to YouTube/Vimeo with embedding enabled; adds actual name/team and required links; reviews official rules and submits. Nothing has been submitted.


## Hosted demo
https://www.youtube.com/watch?v=jFRRMe0OkZE&feature=youtu.be
Published unlisted November 3, 2026; saved in Devpost draft.
