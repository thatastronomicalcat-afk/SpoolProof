"""SpoolProof: offline print-job costing and STL envelope checks. Python 3.10+."""
import argparse, csv, itertools, json, math, struct
from pathlib import Path


def number(value, name, positive=False):
    if isinstance(value, bool):
        raise ValueError(f'{name} must be a number')
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f'{name} must be a number')
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(f'{name} must be finite and {"positive" if positive else "nonnegative"}')
    return value


def stl_bounds(path):
    """Read binary or ASCII STL vertices; never infer units or mesh solidity."""
    data = Path(path).read_bytes()
    if len(data) > 100_000_000:
        raise ValueError('STL exceeds 100 MB limit')
    points = []
    if len(data) >= 84 and 84 + 50 * struct.unpack_from('<I', data, 80)[0] == len(data):
        for off in range(84, len(data), 50):
            vals = struct.unpack_from('<12fH', data, off)
            points.extend([vals[3:6], vals[6:9], vals[9:12]])
    else:
        try:
            for line in data.decode('ascii').splitlines():
                cols = line.strip().split()
                if cols and cols[0].lower() == 'vertex':
                    if len(cols) != 4:
                        raise ValueError('Malformed STL vertex')
                    points.append(tuple(float(v) for v in cols[1:]))
        except (UnicodeError, ValueError) as exc:
            raise ValueError(f'Invalid ASCII STL: {exc}')
    if not points or len(points) % 3:
        raise ValueError('STL must contain complete triangles')
    if not all(math.isfinite(v) for p in points for v in p):
        raise ValueError('Nonfinite STL coordinate')
    return [max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]


def quote(job, base=Path('.')):
    grams = number(job['grams'], 'grams', True)
    hours = number(job['hours'], 'hours', True)
    qty = number(job.get('quantity', 1), 'quantity', True)
    if not qty.is_integer():
        raise ValueError('quantity must be an integer')
    material = grams / 1000 * number(job['filament_per_kg'], 'filament_per_kg')
    power = hours * number(job.get('watts', 0), 'watts') / 1000 * number(job.get('electricity_per_kwh', 0), 'electricity_per_kwh')
    machine = hours * number(job.get('machine_per_hour', 0), 'machine_per_hour')
    fail = number(job.get('failure_probability', 0), 'failure_probability')
    margin = number(job.get('margin', 0), 'margin')
    if fail >= 1 or margin >= 1:
        raise ValueError('failure_probability and margin must be below 1')
    repeat = (material + power + machine) / (1-fail)
    labor = number(job.get('labor_minutes', 0), 'labor_minutes') / 60 * number(job.get('labor_per_hour', 0), 'labor_per_hour')
    cost = qty * (repeat + labor) + number(job.get('setup_cost', 0), 'setup_cost')
    dims = job.get('dimensions_mm')
    if job.get('stl'):
        dims = stl_bounds(base / job['stl'])
        unit = job.get('stl_units')
        if unit not in ('mm', 'in'):
            raise ValueError('STL has no units: set stl_units to mm or in')
        dims = [d * (25.4 if unit == 'in' else 1) for d in dims]
    fit = None
    if dims is not None:
        if len(dims) != 3:
            raise ValueError('dimensions_mm needs three dimensions')
        dims = [number(v, 'dimension', True) for v in dims]
        envelope = job.get('build_mm', [245, 245, 245])
        if len(envelope) != 3:
            raise ValueError('build_mm needs three dimensions')
        envelope = [number(v, 'build dimension', True) for v in envelope]
        fit = any(all(a <= b+1e-6 for a, b in zip(orient, envelope)) for orient in itertools.permutations(dims))
    spool = job.get('spool_remaining_g')
    expected_grams = grams * qty / (1-fail)
    return {'name':str(job.get('name', 'Untitled')), 'quantity':int(qty),
        'material_per_attempt':round(material, 4), 'power_per_attempt':round(power, 4),
        'machine_per_attempt':round(machine, 4), 'labor_per_part':round(labor, 4),
        'expected_job_cost':round(cost, 2), 'suggested_price':math.ceil(cost/(1-margin)*100-1e-9)/100,
        'target_gross_margin':margin, 'expected_filament_g':round(expected_grams, 2),
        'spool_expected_sufficient':None if spool is None else number(spool, 'spool_remaining_g') >= expected_grams,
        'dimensions_mm':dims, 'fits_axis_aligned':fit,
        'limitations':['Cost estimate uses user-provided slicer mass/time and independent identical failure attempts.',
        'Labor is charged once per finished part; setup once per job. Adjust rates to your process.',
        'Fit tests only 90-degree axis permutations. No support, brim, collision, strength or manifold analysis.',
        'Expected filament is not a guarantee of sufficient stock. Currency follows your inputs.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', type=Path, help='JSON job file')
    parser.add_argument('--output', type=Path, help='Write JSON report')
    args = parser.parse_args()
    try:
        result = quote(json.loads(args.job.read_text()), args.job.parent)
        report = json.dumps(result, indent=2, allow_nan=False)
        if args.output:
            args.output.write_text(report+'\n')
        print(report)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(2, f'Error: {exc}\n')

if __name__ == '__main__':
    main()
