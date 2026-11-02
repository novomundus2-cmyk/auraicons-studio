import 'package:test/test.dart';
import '../lib/novus_ledger.dart';

void main() {
  group('Money Value Object', () {
    test('creates money in integer cents without float precision error', () {
      final m1 = Money.fromEuros(10.25);
      expect(m1.cents, equals(1025));
      expect(m1.inEuros, equals(10.25));
      expect(m1.toString(), equals('10.25 EUR'));
    });

    test('adds money instances correctly with exact cent precision', () {
      final a = Money(10050); // 100.50 EUR
      final b = Money(4950);  // 49.50 EUR
      final sum = a + b;

      expect(sum.cents, equals(15000));
      expect(sum.inEuros, equals(150.0));
    });

    test('subtracts money and throws when balance would drop below zero', () {
      final balance = Money(5000);
      final debit = Money(2000);
      expect((balance - debit).cents, equals(3000));

      final excessiveDebit = Money(6000);
      expect(
        () => balance - excessiveDebit,
        throwsA(isA<InvalidAmountException>()),
      );
    });

    test('rejects negative cents on initialization', () {
      expect(() => Money(-100), throwsA(isA<AssertionError>()));
    });
  });

  group('Double-Entry Bookkeeping Ledger Invariants', () {
    late TransactionPayload validTransfer;

    setUp(() {
      validTransfer = TransactionPayload(
        tenantId: 'novus-capital-enterprise',
        correlationId: 'CORR-DART-001',
        description: 'Pago instantáneo Novus SEPA',
        entries: [
          LedgerEntry(
            accountId: 'ACC-TREASURY',
            direction: EntryDirection.credit,
            amountCents: 50000, // 500.00 EUR
          ),
          LedgerEntry(
            accountId: 'ACC-RESERVE',
            direction: EntryDirection.debit,
            amountCents: 50000, // 500.00 EUR
          ),
        ],
      );
    });

    test('validates symmetric double-entry balance correctly', () {
      expect(validTransfer.isBalanced, isTrue);
      expect(validTransfer.totalDebits, equals(50000));
      expect(validTransfer.totalCredits, equals(50000));
      expect(() => validTransfer.validateBalance(), returnsNormally);
    });

    test('rejects unbalanced transactions at client validation level', () {
      final corruptTx = TransactionPayload(
        tenantId: 'novus-capital-enterprise',
        correlationId: 'CORR-CORRUPT',
        description: 'Intento desbalanceado',
        entries: [
          LedgerEntry(
            accountId: 'ACC-TREASURY',
            direction: EntryDirection.credit,
            amountCents: 50000,
          ),
          LedgerEntry(
            accountId: 'ACC-RESERVE',
            direction: EntryDirection.debit,
            amountCents: 45000, // Asymmetric! 500.00 != 450.00
          ),
        ],
      );

      expect(corruptTx.isBalanced, isFalse);
      expect(
        () => corruptTx.validateBalance(),
        throwsA(isA<UnbalancedTransactionException>()),
      );
    });

    test('rejects non-positive entry amounts', () {
      expect(
        () => LedgerEntry(
          accountId: 'ACC-1',
          direction: EntryDirection.debit,
          amountCents: 0,
        ),
        throwsA(isA<InvalidAmountException>()),
      );

      expect(
        () => LedgerEntry(
          accountId: 'ACC-1',
          direction: EntryDirection.debit,
          amountCents: -500,
        ),
        throwsA(isA<InvalidAmountException>()),
      );
    });

    test('generates deterministic SHA-256 idempotency request hash', () {
      final hash1 = validTransfer.generateIdempotencyHash();
      final hash2 = validTransfer.generateIdempotencyHash();

      expect(hash1, equals(hash2));
      expect(hash1.length, equals(64)); // Standard SHA-256 hexadecimal output length
    });
  });
}
