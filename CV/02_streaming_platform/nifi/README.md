# Apache NiFi Ingestion Architecture

In this enterprise platform, Apache NiFi serves as the **edge buffer and heterogeneous ingestion gateway**.

## Accessing NiFi UI
* URL: `https://localhost:8443/nifi`
* Username: `admin`
* Password: `adminPassword123!`

*(Accept the self-signed SSL certificate in your browser)*

## Typical Ingestion Pattern in this Stack:
1. **Source:** `InvokeHTTP` (polling external payment APIs) or `GenerateFlowFile` (synthetic events).
2. **Schema & Conversion:** `ConvertRecord` or `JoltTransformJSON` to standardize payloads.
3. **Queue & Backpressure:** Configured at 10,000 objects / 1 GB buffer to prevent downstream broker saturation.
4. **Publish to Kafka:** `PublishKafkaRecord_2_6`:
   * Kafka Brokers: `kafka:29092`
   * Topic: `financial_transactions`
   * Delivery Guarantee: `Guarantee Replicated Delivery` (acks=all)
