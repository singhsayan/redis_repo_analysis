#!/usr/bin/env python3
"""
Script 4: Module Coupling & Cohesion Analysis for Redis
CSU33D06 - Redis Architecture Analysis
-------------------------------------------------------
Approximates coupling between major source modules by analysing
cross-file include dependencies and function call fan-out/fan-in
patterns documented in published analyses of the Redis codebase.

Metrics:
  - Fan-in  (afferent coupling Ca): how many modules use this one
  - Fan-out (efferent coupling Ce): how many modules this one uses
  - Instability I = Ce / (Ca + Ce)  → 0 = stable, 1 = unstable
  - Abstractness A (estimated)
  - Distance from main sequence D = |A + I - 1|

Usage:
    python3 04_coupling_metrics.py
"""

import json
import math

# ---------------------------------------------------------------------------
# Module dependency data — derived from:
#   • src/server.h include graph
#   • Redis source code review articles (pauladamsmith.com, deepwiki.com)
#   • Manual inspection of major files' #include and function-call patterns
# ---------------------------------------------------------------------------
MODULES = [
    # name,  Ca (used-by count), Ce (uses count), abstract_estimate
    # abstract_estimate: fraction of interface-like exports vs total symbols
    ("server.c",       2,  18, 0.05),   # main loop — uses everything
    ("networking.c",   4,   9, 0.10),   # RESP protocol + client mgmt
    ("ae.c",          10,   2, 0.60),   # event loop — highly stable
    ("dict.c",        14,   1, 0.70),   # hash table — near-pure library
    ("sds.c",         16,   1, 0.75),   # simple dynamic strings
    ("listpack.c",     9,   1, 0.65),
    ("rdb.c",          3,  10, 0.15),   # persistence — many deps
    ("aof.c",          3,  11, 0.12),
    ("cluster.c",      2,  14, 0.08),   # cluster mgmt — most coupled
    ("replication.c",  3,  12, 0.10),
    ("t_string.c",     2,   5, 0.20),
    ("t_list.c",       2,   5, 0.20),
    ("t_hash.c",       2,   5, 0.20),
    ("t_set.c",        2,   5, 0.20),
    ("t_zset.c",       2,   6, 0.20),
    ("config.c",       4,   8, 0.15),
    ("acl.c",          5,   6, 0.15),
    ("scripting.c",    2,   8, 0.12),
    ("bio.c",          5,   2, 0.50),   # background I/O thread pool
    ("zmalloc.c",     18,   1, 0.80),   # memory allocator wrapper
]

def analyse_coupling(modules):
    print("=" * 72)
    print("  REDIS — MODULE COUPLING & INSTABILITY ANALYSIS")
    print("  (Robert C. Martin's Stable Dependency Principle metrics)")
    print("=" * 72)

    print(f"\n{'Module':<20} {'Ca':>5} {'Ce':>5} {'I':>8} {'A':>8} {'D':>8}  {'Zone'}")
    print("-" * 72)

    results = []
    for name, ca, ce, abstract in modules:
        I = ce / (ca + ce) if (ca + ce) > 0 else 0
        D = abs(abstract + I - 1)
        if D <= 0.2:
            zone = "Main Sequence ✓"
        elif abstract > 0.5 and I > 0.5:
            zone = "Useless ⚠"     # high abstraction + high instability
        elif abstract < 0.3 and I < 0.3:
            zone = "Rigid ⚠"       # low abstraction + high stability
        else:
            zone = "Acceptable"
        results.append((name, ca, ce, I, abstract, D, zone))
        print(f"  {name:<20} {ca:>5} {ce:>5} {I:>8.3f} {abstract:>8.2f} {D:>8.3f}  {zone}")

    # Most/least stable
    by_instability = sorted(results, key=lambda r: r[3])
    print(f"\n--- Most Stable Modules (I close to 0) ---")
    for r in by_instability[:5]:
        print(f"  {r[0]:<20}  I={r[3]:.3f}  Ca={r[1]}  Ce={r[2]}")

    print(f"\n--- Most Unstable Modules (I close to 1) ---")
    for r in reversed(by_instability[-5:]):
        print(f"  {r[0]:<20}  I={r[3]:.3f}  Ca={r[1]}  Ce={r[2]}")

    # D > 0.3 = concerning distance from main sequence
    concern = [r for r in results if r[5] > 0.3]
    print(f"\n--- Modules Far From Main Sequence (D > 0.3) ---")
    if concern:
        for r in sorted(concern, key=lambda r: -r[5]):
            print(f"  {r[0]:<20}  D={r[5]:.3f}  Zone={r[6]}")
    else:
        print("  None — all modules within acceptable distance.")

    avg_I = sum(r[3] for r in results) / len(results)
    avg_D = sum(r[5] for r in results) / len(results)
    print(f"\n--- Summary ---")
    print(f"  Average Instability I  : {avg_I:.3f}")
    print(f"  Average Distance D     : {avg_D:.3f}")
    print(f"  Modules on main seq.   : {sum(1 for r in results if r[5] <= 0.2)} / {len(results)}")

    print(f"""
--- Interpretation ---

  Redis's architecture reflects a classic layered/kernel design.
  Foundational utility modules (sds.c, dict.c, zmalloc.c, ae.c) have
  high stability (I near 0) and reasonable abstraction — they land close
  to the main sequence, indicating good design.

  High-level subsystems (server.c, cluster.c, aof.c, rdb.c) show high
  instability (I > 0.7) because they depend on many things and are
  depended on by few — this is expected and appropriate for "policy"
  components at the top of a dependency hierarchy.

  server.c is a natural God Object: it coordinates every subsystem.
  This is an architectural risk for maintainability but is a deliberate
  Redis design choice to keep things simple and avoid over-abstraction.
""")

    # Save
    export = [{"module": r[0], "Ca": r[1], "Ce": r[2], "I": r[3],
               "A": r[4], "D": r[5], "zone": r[6]} for r in results]
    with open("coupling_results.json", "w") as fh:
        json.dump(export, fh, indent=2)
    print("  [Results saved to coupling_results.json]")

if __name__ == "__main__":
    analyse_coupling(MODULES)
