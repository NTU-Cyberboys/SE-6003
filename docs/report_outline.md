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
7. **References:** RFC 8017 and any optional reference-library validation,
   clearly labeled as an independent cross-check rather than implementation.
