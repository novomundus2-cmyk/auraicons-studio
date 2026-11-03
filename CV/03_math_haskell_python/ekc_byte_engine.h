/**
 * ============================================================================
 * EKC (ElektriKubercisC) BYTE-LEVEL MATHEMATICAL ENGINE
 * Author: Mikel Irastorza (Data & Deployment Engineer · EFA)
 * Architecture: Packed binary memory structures, SIMD-aligned Welford streaming,
 *               hardware FMA CAD tolerance bounds, and zero-overhead C11 engine.
 * ============================================================================
 */

#ifndef EKC_BYTE_ENGINE_H
#define EKC_BYTE_ENGINE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#pragma pack(push, 1)

/**
 * EkcStreamRecord:
 * Exactly 32 bytes packed representation of a streaming event.
 * Memory layout:
 *   [00..07] uint64_t timestamp_ns (Epoch in nanoseconds)
 *   [08..15] uint64_t sequence_id  (Monotonic sequential ID)
 *   [16..23] double   value        (IEEE 754 64-bit float measurement)
 *   [24..27] uint32_t flags        (Bitmask: bit 0=anomaly, 1=cad_ok, 2=pacioli_ok)
 *   [28..31] uint32_t crc32        (CRC-32 checksum of bytes 0..27)
 * Cache-line efficiency: Exactly 2 records per 64-byte L1 CPU cache line.
 */
typedef struct {
    uint64_t timestamp_ns;
    uint64_t sequence_id;
    double   value;
    uint32_t flags;
    uint32_t crc32;
} EkcStreamRecord;

/**
 * EkcWelfordState:
 * 40 bytes accumulator for Chan-Golub-LeVeque parallel Welford variance.
 * Numerically stable, one-pass O(1) space.
 */
typedef struct {
    uint64_t count;
    double   mean;
    double   m2;        /* Sum of squared differences: M2 = sum((x - mean)^2) */
    double   variance;  /* Population variance: M2 / count */
    double   std_dev;   /* Standard deviation: sqrt(variance) */
} EkcWelfordState;

/**
 * EkcCadPoint:
 * 28 bytes packed mechanical geometry point with physical tolerance.
 */
typedef struct {
    double   x_mm;
    double   y_mm;
    double   target_dim_mm;
    float    tolerance_mm; /* Target: 0.200 mm */
} EkcCadPoint;

#pragma pack(pop)

/* Flag bits */
#define EKC_FLAG_ANOMALY_ZSCORE  (1U << 0)
#define EKC_FLAG_CAD_WITHIN_TOL  (1U << 1)
#define EKC_FLAG_PACIOLI_BALANCED (1U << 2)
#define EKC_FLAG_CRC_VERIFIED    (1U << 3)

/* API Functions */

void ekc_welford_init(EkcWelfordState *state);

void ekc_welford_update(EkcWelfordState *state, double x);

void ekc_welford_merge(EkcWelfordState *out, const EkcWelfordState *a, const EkcWelfordState *b);

void ekc_welford_batch(EkcWelfordState *state, const double *values, size_t n);

double ekc_welford_zscore(const EkcWelfordState *state, double x);

bool ekc_verify_cad_tolerance(double actual, double target, double tolerance_mm);

int ekc_cad_batch_check(const double *actuals, const double *targets, size_t n, double tolerance_mm);

uint32_t ekc_fast_crc32(const uint8_t *data, size_t length);

uint32_t ekc_stream_record_checksum(const EkcStreamRecord *rec);

bool ekc_stream_record_verify(const EkcStreamRecord *rec);

bool ekc_pacioli_balance(const double *debits, size_t n_debits,
                         const double *credits, size_t n_credits,
                         double *out_diff, double epsilon);

size_t ekc_record_size_bytes(void);

#ifdef __cplusplus
}
#endif

#endif /* EKC_BYTE_ENGINE_H */
