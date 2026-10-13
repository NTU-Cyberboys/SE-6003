# Report outline

1. **Objective:** implement and evaluate RSA-OAEP with SHA-256.
2. **Design:** describe key generation, Miller–Rabin, modular arithmetic,
   MGF1, OAEP encoding/decoding, CLI, and serialization.
3. **Correctness:** summarize unit/integration tests and negative cases,
   including overlong messages, ciphertext length/range, wrong labels,
   tampering, and malformed padding.
4. **Experiment:** state hardware/software, commands, key sizes, repetitions,
   and timing methodology from `experiment_plan.md`.
5. **Results:** include the generated timing chart and summary CSV table.
   Discuss trends and variance without making cross-machine claims.
6. **Limitations:** educational-only implementation, non-constant-time
   arithmetic, no blinding/CRT, and no formal cryptographic review.
7. **References:** cite Bellare and Rogaway for the OAEP construction,
   Pointcheval for RSA-encryption security context, and RFC 8017 for the
   standardized RSAES-OAEP encoding. Cite any optional reference-library
   validation as an independent cross-check, not as the implementation.
