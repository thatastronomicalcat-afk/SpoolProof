# SpoolProof
Offline 3D-print job costing and envelope checks. No account, network, API key, or third-party package required. Python 3.10 or later.

Run: `python spoolproof.py example_job.json --output report.json`
Windows: `py spoolproof.py example_job.json --output report.json`
Tests: `python -m unittest -v test_spoolproof.py`

Edit example_job.json with your slicer's mass/time and your costs. Cost inputs use a single currency consistently; margin and failure probability use fractions (0.30 means 30%). Mass and hours are per attempt, labor per successful part, setup per job. Machine rate should exclude separately entered power and labor to avoid double counting. The price excludes tax/shipping unless included in setup.

Optional STL: add "stl":"your.stl", "stl_units":"mm" (or "in"). STL has no standard units. This checks bounding-box extents only, in six axis permutations; it is not a slicer. Default envelope 245 mm each axis is a conservative user-selectable allowance, not a certification of printer compatibility.

Expected repeatable costs = (material + electricity + machine) / (1 - failure_probability).
Job cost = quantity * (repeatable costs + labor) + setup.
Price = cost / (1 - gross margin), rounded upward to the next cent.
The independent identical failure-attempt model is an estimate, not measured reliability. Materials may still run out. No customer data is needed.

No live printer connection, mesh repair, automatic mass estimation, arbitrary-angle packing, tax calculation, or payment processing. Sample numbers are synthetic. This software has not been tested on a physical printer.

Created November 2, 2026 with ChatGPT/Codex assistance. See submission.md and test_results.txt. MIT license applies to original source files.

Desktop form: `py spoolproof_gui.py` (compiled only; see desktop_note.md).
