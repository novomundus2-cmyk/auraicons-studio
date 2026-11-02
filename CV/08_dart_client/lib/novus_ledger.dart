import 'dart:convert';
import 'package:crypto/crypto.dart';

enum EntryDirection { debit, credit }

class InvalidAmountException implements Exception {
  final String message;
  InvalidAmountException(this.message);

  @override
  String toString() => 'InvalidAmountException: $message';
}

class UnbalancedTransactionException implements Exception {
  final int totalDebits;
  final int totalCredits;

  UnbalancedTransactionException(this.totalDebits, this.totalCredits);

  @override
  String toString() =>
      'UnbalancedTransactionException: Debits ($totalDebits) != Credits ($totalCredits)';
}

/// Represents an immutable monetary amount strictly in integer cents (e.g. 10.50 EUR = 1050 cents).
/// Eliminates IEEE 754 floating-point inaccuracies.
class Money {
  final int cents;
  final String currency;

  const Money(this.cents, {this.currency = 'EUR'})
      : assert(cents >= 0, 'Amount must be non-negative');

  factory Money.fromEuros(double euros, {String currency = 'EUR'}) {
    return Money((euros * 100).round(), currency: currency);
  }

  double get inEuros => cents / 100.0;

  Money operator +(Money other) {
    _ensureSameCurrency(other);
    return Money(cents + other.cents, currency: currency);
  }

  Money operator -(Money other) {
    _ensureSameCurrency(other);
    if (cents < other.cents) {
      throw InvalidAmountException('Resulting balance cannot be negative');
    }
    return Money(cents - other.cents, currency: currency);
  }

  void _ensureSameCurrency(Money other) {
    if (currency != other.currency) {
      throw ArgumentError('Currency mismatch: $currency != ${other.currency}');
    }
  }

  @override
  String toString() => '${inEuros.toStringAsFixed(2)} $currency';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Money && cents == other.cents && currency == other.currency;

  @override
  int get hashCode => cents.hashCode ^ currency.hashCode;
}

/// Atomic ledger entry for double-entry bookkeeping.
class LedgerEntry {
  final String accountId;
  final EntryDirection direction;
  final int amountCents;

  LedgerEntry({
    required this.accountId,
    required this.direction,
    required this.amountCents,
  }) {
    if (amountCents <= 0) {
      throw InvalidAmountException('Entry amount must be strictly > 0 cents');
    }
  }
}

/// Transaction payload holding symmetric ledger entries and idempotency metadata.
class TransactionPayload {
  final String tenantId;
  final String correlationId;
  final String description;
  final List<LedgerEntry> entries;

  TransactionPayload({
    required this.tenantId,
    required this.correlationId,
    required this.description,
    required this.entries,
  });

  /// Calculates total debits in integer cents.
  int get totalDebits => entries
      .where((e) => e.direction == EntryDirection.debit)
      .fold(0, (sum, e) => sum + e.amountCents);

  /// Calculates total credits in integer cents.
  int get totalCredits => entries
      .where((e) => e.direction == EntryDirection.credit)
      .fold(0, (sum, e) => sum + e.amountCents);

  /// Verifies the fundamental accounting invariant: Total Debits == Total Credits.
  bool get isBalanced => totalDebits == totalCredits && totalDebits > 0;

  /// Validates transaction balance or throws [UnbalancedTransactionException].
  void validateBalance() {
    if (entries.isEmpty) {
      throw InvalidAmountException('Transaction must contain at least two entries');
    }
    if (totalDebits != totalCredits) {
      throw UnbalancedTransactionException(totalDebits, totalCredits);
    }
  }

  /// Generates a deterministic SHA-256 idempotency request hash.
  String generateIdempotencyHash() {
    final canonicalString =
        '$tenantId|$correlationId|$totalDebits|${entries.length}';
    final bytes = utf8.encode(canonicalString);
    return sha256.convert(bytes).toString();
  }
}
