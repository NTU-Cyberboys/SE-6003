"""Supplementary experiments for the RSA-OAEP report.

The rsaoaep package is used unchanged; instrumentation is done by wrapping
module-level functions at runtime. Run from the repository root:

    PYTHONPATH=src python report/experiments/report_experiments.py <section> ...

Sections: env, prime:<bits>, keygen:<bits>, bench:<bits>, mr, timing, crt,
hashes, random (e.g. ``prime:1024 bench:2048``). Each section writes
report/experiments/results_<section>[_<bits>].json.
PyCryptodome is needed only for the "hashes" interoperability section.
"""

from __future__ import annotations

import json
import math
import platform
import secrets
import statistics
import sys
import time
from pathlib import Path

import rsaoaep.oaep as oaep
import rsaoaep.primality as prim
import rsaoaep.rsa_core as core
from rsaoaep import decrypt, encrypt, generate_keypair

OUT = Path(__file__).resolve().parent
SMALL = prim._SMALL_PRIMES


def save(name: str, data: object) -> None:
    (OUT / f"results_{name}.json").write_text(json.dumps(data, indent=2) + "\n")
    print(f"[{name}] done", flush=True)


def med(xs):
    return statistics.median(xs)


def summary(xs):
    return {
        "n": len(xs),
        "mean": statistics.mean(xs),
        "median": statistics.median(xs),
        "stdev": statistics.stdev(xs) if len(xs) > 1 else 0.0,
        "min": min(xs),
        "max": max(xs),
    }


# ---------------------------------------------------------------- env
def run_env():
    save("env", {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
    })


# ---------------------------------------------------------------- prime search statistics
def run_prime(arg="1024"):
    bits_one = int(arg)
    samples = {512: 300, 1024: 150, 1536: 60}[bits_one]
    orig = prim.is_probable_prime
    result = {}
    td_survival = 1.0
    for p in SMALL[1:]:
        td_survival *= 1 - 1 / p
    for bits in (bits_one,):
        cand, td, mr, first_round_pass = [], [], [], 0
        mr_composites = 0
        for _ in range(samples):
            c = {"n": 0, "td": 0, "mr": 0}

            def wrapped(x, rounds=40, c=c):
                c["n"] += 1
                r = orig(x, rounds)
                if not r:
                    if any(x % p == 0 for p in SMALL):
                        c["td"] += 1
                    else:
                        c["mr"] += 1
                        wrapped.mr_list.append(x)
                return r

            wrapped.mr_list = []
            prim.is_probable_prime = wrapped
            try:
                prim.generate_prime(bits)
            finally:
                prim.is_probable_prime = orig
            cand.append(c["n"])
            td.append(c["td"])
            mr.append(c["mr"])
            # how many MR-rejected composites would pass a single MR round?
            for x in wrapped.mr_list[:20]:
                mr_composites += 1
                if orig(x, 1):
                    first_round_pass += 1
        result[bits] = {
            "samples": samples,
            "candidates": summary(cand),
            "rejected_trial_division": summary(td),
            "rejected_miller_rabin": summary(mr),
            "expected_candidates_pnt": bits * math.log(2) / 2,
            "single_round_checked": mr_composites,
            "single_round_false_accepts": first_round_pass,
        }
    result["trial_division_survival_theory"] = td_survival
    # time for generate_prime with 40 vs 4 rounds
    timing = {}
    for bits in ((bits_one,) if bits_one != 512 else ()):
        for rounds in (40, 4):
            ts = []
            for _ in range(20 if bits == 1024 else 8):
                t = time.perf_counter()
                prim.generate_prime(bits, rounds)
                ts.append((time.perf_counter() - t) * 1000)
            timing[f"{bits}_{rounds}"] = summary(ts)
        # cost of the 40 rounds applied to an actual prime
        p = prim.generate_prime(bits)
        ts40 = []
        for _ in range(30):
            t = time.perf_counter()
            prim.is_probable_prime(p, 40)
            ts40.append((time.perf_counter() - t) * 1000)
        timing[f"{bits}_final40"] = summary(ts40)
    result["timing_ms"] = timing
    save(f"prime_{bits_one}", result)


# ---------------------------------------------------------------- key generation: pair rejection
def run_keygen(arg="1024"):
    orig = core.generate_prime
    result = {}
    for bits, n in (((1024, 200),) if arg == "1024" else ((2048, 40),)):
        primes_per_key = []
        for _ in range(n):
            calls = [0]

            def wrapped(b, rounds=40, calls=calls):
                calls[0] += 1
                return orig(b, rounds)

            core.generate_prime = wrapped
            try:
                generate_keypair(bits)
            finally:
                core.generate_prime = orig
            primes_per_key.append(calls[0])
        pairs = [k / 2 for k in primes_per_key]
        result[bits] = {
            "keys": n,
            "pairs_per_key": summary(pairs),
            "acceptance_rate_empirical": n / sum(pairs),
            "acceptance_rate_theory": 2 - 2 * math.log(2),
        }
    save(f"keygen_{arg}", result)


# ---------------------------------------------------------------- benchmarks
def run_bench(arg="1024"):
    plan = {int(arg): {1024: 30, 2048: 20, 3072: 10, 4096: 12}[int(arg)]}
    message = b"RSA-OAEP benchmark sample"
    out = {}
    for bits, reps in plan.items():
        kg = []
        pair = None
        for _ in range(reps):
            t = time.perf_counter()
            pair = generate_keypair(bits)
            kg.append((time.perf_counter() - t) * 1000)
        enc, dec = [], []
        for _ in range(200 if bits < 4096 else 60):
            t = time.perf_counter()
            c = encrypt(message, pair.public_key)
            enc.append((time.perf_counter() - t) * 1000)
            t = time.perf_counter()
            m = decrypt(c, pair.private_key)
            dec.append((time.perf_counter() - t) * 1000)
            assert m == message
        out[bits] = {"keygen_ms": summary(kg), "encrypt_ms": summary(enc),
                     "decrypt_ms": summary(dec)}
        print(bits, med(kg), med(enc), med(dec), flush=True)
        save(f"bench_{arg}", out)


# ---------------------------------------------------------------- Miller-Rabin liars
def strong_liar(a, n, d, s):
    x = pow(a, d, n)
    if x in (1, n - 1):
        return True
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1:
            return True
    return False


def decompose(n):
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    return d, s


def run_mr():
    exact = []
    for n in (9, 15, 21, 25, 91, 341, 561, 703, 1105, 1729, 2047, 2465, 8911, 1373653):
        d, s = decompose(n)
        bases = range(2, n - 1)  # the implementation samples a in [2, n-2]
        strong = sum(strong_liar(a, n, d, s) for a in bases)
        fermat = sum(pow(a, n - 1, n) == 1 for a in bases)
        phi = sum(1 for a in range(1, n) if math.gcd(a, n) == 1)
        exact.append({"n": n, "bases": n - 3, "strong_liars": strong,
                      "fermat_liars": fermat, "phi": phi,
                      "strong_fraction": strong / (n - 3)})
    sampled = []
    for n in (3215031751, 3825123056546413051):
        d, s = decompose(n)
        trials = 200000
        hits = sum(strong_liar(secrets.randbelow(n - 3) + 2, n, d, s) for _ in range(trials))
        fixed = [a for a in (2, 3, 5, 7, 11, 13, 17, 19, 23) if strong_liar(a, n, d, s)]
        implementation = sum(prim.is_probable_prime(n, 40) for _ in range(1000))
        sampled.append({"n": n, "trials": trials, "liar_hits": hits,
                        "fixed_bases_lying": fixed,
                        "impl_accepts_out_of_1000": implementation})
    # random 512-bit odd composites that survive trial division: single-round acceptance
    tested = accepted = 0
    while tested < 20000:
        x = secrets.randbits(512) | (1 << 511) | 1
        if any(x % p == 0 for p in SMALL) or prim.is_probable_prime(x, 40):
            continue
        tested += 1
        accepted += prim.is_probable_prime(x, 1)
    save("mr", {"exact": exact, "sampled": sampled,
                "random512": {"tested": tested, "single_round_accepted": accepted}})


# ---------------------------------------------------------------- decoding-failure timing
def run_timing(bits=2048, reps=400, decode_reps=20000):
    pair = generate_keypair(bits)
    pub, priv = pair.public_key, pair.private_key
    k = pub.size_bytes
    valid_em = oaep.oaep_encode(b"timing test", k)
    cases = {
        "nonzero_first_byte": b"\x01" + secrets.token_bytes(k - 1),
        "bad_label_hash": b"\x00" + secrets.token_bytes(k - 1),
        "valid": valid_em,
    }
    # decode-only
    decode = {}
    for name, em in cases.items():
        ts = []
        for _ in range(decode_reps):
            t = time.perf_counter_ns()
            try:
                oaep.oaep_decode(em)
            except Exception:
                pass
            ts.append((time.perf_counter_ns() - t) / 1000)
        decode[name] = summary(ts)
    # end to end, interleaved
    cts = {name: pow(int.from_bytes(em, "big"), pub.e, pub.n).to_bytes(k, "big")
           for name, em in cases.items()}
    e2e = {name: [] for name in cases}
    for _ in range(reps):
        for name, c in cts.items():
            t = time.perf_counter_ns()
            try:
                decrypt(c, priv)
            except Exception:
                pass
            e2e[name].append((time.perf_counter_ns() - t) / 1000)
    save("timing", {"bits": bits, "decode_us": decode,
                    "end_to_end_us": {n: summary(v) for n, v in e2e.items()}})


# ---------------------------------------------------------------- CRT what-if
def run_crt():
    orig = core.generate_prime
    out = {}
    for bits in (2048, 3072):
        seen = []

        def wrapped(b, rounds=40):
            p = orig(b, rounds)
            seen.append(p)
            return p

        core.generate_prime = wrapped
        try:
            pair = generate_keypair(bits)
        finally:
            core.generate_prime = orig
        p, q = seen[-2], seen[-1]
        n, d = pair.private_key.n, pair.private_key.d
        assert p * q == n
        dp, dq, qinv = d % (p - 1), d % (q - 1), pow(q, -1, p)
        c = secrets.randbelow(n)
        plain, crt = [], []
        for _ in range(60):
            t = time.perf_counter()
            m1 = pow(c, d, n)
            plain.append((time.perf_counter() - t) * 1000)
            t = time.perf_counter()
            mp, mq = pow(c, dp, p), pow(c, dq, q)
            m2 = mq + q * ((qinv * (mp - mq)) % p)
            crt.append((time.perf_counter() - t) * 1000)
            assert m1 == m2
        out[bits] = {"plain_ms": summary(plain), "crt_ms": summary(crt),
                     "speedup": med(plain) / med(crt)}
    save("crt", out)


# ---------------------------------------------------------------- hash variants + interop
def run_hashes():
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.Hash import SHA3_256, SHA3_512, SHA256, SHA512
    from Crypto.PublicKey import RSA

    variants = {"sha256": SHA256, "sha512": SHA512, "sha3_256": SHA3_256, "sha3_512": SHA3_512}
    pair = generate_keypair(2048)
    ref_priv = RSA.construct((pair.private_key.n, pair.private_key.e, pair.private_key.d))
    ref_pub = ref_priv.publickey()
    k = pair.public_key.size_bytes
    saved = (oaep.HASH_NAME, oaep.HASH_LENGTH)
    out = {}
    try:
        for name, mod in variants.items():
            import hashlib
            oaep.HASH_NAME = name
            oaep.HASH_LENGTH = hashlib.new(name).digest_size
            ok = 0
            trials = 50
            for i in range(trials):
                msg = secrets.token_bytes(1 + i % (k - 2 * oaep.HASH_LENGTH - 2))
                label = secrets.token_bytes(i % 7)
                c1 = encrypt(msg, pair.public_key, label)
                a = PKCS1_OAEP.new(ref_priv, hashAlgo=mod, label=label).decrypt(c1) == msg
                c2 = PKCS1_OAEP.new(ref_pub, hashAlgo=mod, label=label).encrypt(msg)
                b = decrypt(c2, pair.private_key, label) == msg
                ok += a and b
            ts = []
            em_msg = b"x" * 32
            for _ in range(5000):
                t = time.perf_counter_ns()
                oaep.oaep_encode(em_msg, k)
                ts.append((time.perf_counter_ns() - t) / 1000)
            out[name] = {"hLen": oaep.HASH_LENGTH, "max_message_bytes_2048": k - 2 * oaep.HASH_LENGTH - 2,
                         "interop_trials": trials, "interop_ok": ok,
                         "encode_us": summary(ts)}
    finally:
        oaep.HASH_NAME, oaep.HASH_LENGTH = saved
    save("hashes", out)


# ---------------------------------------------------------------- randomisation
def run_random():
    pair = generate_keypair(1024)
    cts = {encrypt(b"yes", pair.public_key) for _ in range(1000)}
    save("random", {"encryptions": 1000, "distinct_ciphertexts": len(cts)})


SECTIONS = {"env": run_env, "prime": run_prime, "keygen": run_keygen, "bench": run_bench,
            "mr": run_mr, "timing": run_timing, "crt": run_crt, "hashes": run_hashes,
            "random": run_random}

if __name__ == "__main__":
    for spec in sys.argv[1:] or list(SECTIONS):
        name, _, arg = spec.partition(":")
        SECTIONS[name](arg) if arg else SECTIONS[name]()
